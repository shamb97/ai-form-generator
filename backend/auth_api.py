"""
Authentication API endpoints
JWT-based authentication with role-based access control
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from auth_database import (
    User, StudyDesigner, Investigator, Subject, InvestigatorSiteAssignment,
    get_db, verify_password, get_password_hash, generate_access_code
)

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    """Generic registration request for any role"""
    username: str
    email: EmailStr
    password: str
    role: str  # "study_designer", "subject", "designer", or "participant"
    organization: Optional[str] = None

class RegisterDesignerRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    organization: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

# ============================================================================
# JWT HELPER FUNCTIONS
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/register", response_model=TokenResponse)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Generic user registration endpoint
    Supports both study_designer and subject roles
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate and normalize role
    role_mapping = {
        "study_designer": "study_designer",
        "designer": "study_designer",
        "subject": "subject",
        "participant": "subject"
    }
    
    normalized_role = role_mapping.get(request.role.lower())
    if not normalized_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(role_mapping.keys())}"
        )
    
    # Create base user
    password_hash = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        role=normalized_role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create role-specific record
    if normalized_role == "study_designer":
        designer = StudyDesigner(
            user_id=new_user.user_id,
            organization=request.organization,
            created_at=datetime.utcnow()
        )
        db.add(designer)
    elif normalized_role == "subject":
        subject = Subject(
            user_id=new_user.user_id,
            created_at=datetime.utcnow()
        )
        db.add(subject)
    
    db.commit()
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username, "role": new_user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }
    }

@router.post("/register/designer", response_model=TokenResponse)
def register_designer(request: RegisterDesignerRequest, db: Session = Depends(get_db)):
    """
    Register a new study designer (legacy endpoint - use /register instead)
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    password_hash = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        role="study_designer",
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create study designer record
    designer = StudyDesigner(
        user_id=new_user.user_id,
        organization=request.organization,
        created_at=datetime.utcnow()
    )
    db.add(designer)
    db.commit()
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username, "role": new_user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }
    }

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint
    Returns JWT token on successful authentication
    """
    # Find user by username
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return {
        "id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint (token invalidation handled client-side)
    """
    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }

@router.post("/validate-access-code")
def validate_access_code(access_code: str, db: Session = Depends(get_db)):
    """
    Validate an access code for study enrollment
    """
    from auth_database import AccessCode
    
    code = db.query(AccessCode).filter(
        AccessCode.code == access_code,
        AccessCode.is_active == True
    ).first()
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired access code"
        )
    
    # Check if code has usage limit
    if code.max_uses and code.uses >= code.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access code has reached maximum usage limit"
        )
    
    # Check expiration
    if code.expires_at and code.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access code has expired"
        )
    
    return {
        "valid": True,
        "study_id": code.study_id,
        "message": "Access code is valid"
    }