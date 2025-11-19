"""
Complete authentication and role-based database schema
Multi-role, multi-site support for clinical trials platform
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from passlib.context import CryptContext
import secrets
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_form_generator_auth.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# MODELS
# ============================================================================

class User(Base):
    """Base user model for all roles"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # designer, investigator, subject
    access_code = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    designer_profile = relationship("StudyDesigner", back_populates="user", uselist=False)
    investigator_profile = relationship("Investigator", back_populates="user", uselist=False)
    subject_profile = relationship("Subject", back_populates="user", uselist=False)


class StudyDesigner(Base):
    """Study Designer profile"""
    __tablename__ = "study_designers"
    
    designer_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    organization = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="designer_profile")
    studies = relationship("Study", back_populates="designer", cascade="all, delete-orphan")


class Study(Base):
    """Research study (can have multiple sites)"""
    __tablename__ = "studies"
    
    study_id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("study_designers.designer_id"))
    study_code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    ai_config = Column(JSON)  # AI-generated configuration
    schedule_config = Column(JSON)  # LCM schedule
    phases = Column(JSON)  # List of phase names
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    designer = relationship("StudyDesigner", back_populates="studies")
    sites = relationship("Site", back_populates="study", cascade="all, delete-orphan")
    forms = relationship("Form", back_populates="study", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="study", cascade="all, delete-orphan")


class Site(Base):
    """Research site (multi-center trial support)"""
    __tablename__ = "sites"
    
    site_id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.study_id"))
    site_code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    study = relationship("Study", back_populates="sites")
    investigator_assignments = relationship("InvestigatorSiteAssignment", back_populates="site", cascade="all, delete-orphan")


class Investigator(Base):
    """Investigator (can manage multiple sites)"""
    __tablename__ = "investigators"
    
    investigator_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="investigator_profile")
    site_assignments = relationship("InvestigatorSiteAssignment", back_populates="investigator", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="investigator", cascade="all, delete-orphan")


class InvestigatorSiteAssignment(Base):
    """Junction table: Investigators can manage multiple sites"""
    __tablename__ = "investigator_site_assignments"
    
    assignment_id = Column(Integer, primary_key=True, index=True)
    investigator_id = Column(Integer, ForeignKey("investigators.investigator_id"))
    site_id = Column(Integer, ForeignKey("sites.site_id"))
    role = Column(String, default="investigator")  # principal_investigator, coordinator, etc.
    is_primary = Column(Boolean, default=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    investigator = relationship("Investigator", back_populates="site_assignments")
    site = relationship("Site", back_populates="investigator_assignments")


class Subject(Base):
    """Study participant"""
    __tablename__ = "subjects"
    
    subject_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    investigator_id = Column(Integer, ForeignKey("investigators.investigator_id"))
    study_id = Column(Integer, ForeignKey("studies.study_id"))
    subject_code = Column(String, unique=True, index=True)
    current_phase = Column(String, default="screening")
    study_day = Column(Integer, default=1)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")
    
    user = relationship("User", back_populates="subject_profile")
    investigator = relationship("Investigator", back_populates="subjects")
    study = relationship("Study", back_populates="subjects")
    completions = relationship("Completion", back_populates="subject", cascade="all, delete-orphan")


class Form(Base):
    """Study form"""
    __tablename__ = "forms"
    
    form_id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.study_id"))
    form_code = Column(String, index=True)
    name = Column(String, nullable=False)
    frequency = Column(Integer)
    schema = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    study = relationship("Study", back_populates="forms")
    completions = relationship("Completion", back_populates="form", cascade="all, delete-orphan")


class Completion(Base):
    """Form completion record"""
    __tablename__ = "completions"
    
    completion_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))
    form_id = Column(Integer, ForeignKey("forms.form_id"))
    phase = Column(String)
    day_type = Column(String)
    study_day = Column(Integer)
    data = Column(JSON)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    subject = relationship("Subject", back_populates="completions")
    form = relationship("Form", back_populates="completions")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_access_code(prefix: str = "") -> str:
    """Generate unique access code"""
    code = secrets.token_urlsafe(8)
    return f"{prefix}{code}" if prefix else code


def generate_study_code() -> str:
    """Generate study code like STU-ABC123"""
    return f"STU-{secrets.token_hex(3).upper()}"


def generate_site_code(study_code: str, number: int) -> str:
    """Generate site code like STU-ABC123-SITE01"""
    return f"{study_code}-SITE{number:02d}"


def generate_subject_code(site_code: str, number: int) -> str:
    """Generate subject code like STU-ABC123-SITE01-S001"""
    return f"{site_code}-S{number:03d}"


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def reset_db():
    """Drop and recreate all tables (USE WITH CAUTION)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("⚠️  Database reset complete")


# ============================================================================
# SEED DATA (For Testing)
# ============================================================================

def create_test_data(db):
    """Create test users for development"""
    
    # Designer
    designer_user = User(
        username="designer1",
        email="designer@test.com",
        password_hash=get_password_hash("password123"),
        role="designer"
    )
    db.add(designer_user)
    db.commit()
    db.refresh(designer_user)
    
    designer_profile = StudyDesigner(
        user_id=designer_user.user_id,
        organization="Test University"
    )
    db.add(designer_profile)
    db.commit()
    
    # Study
    study_code = generate_study_code()
    study = Study(
        designer_id=designer_profile.designer_id,
        study_code=study_code,
        name="Test Pain Study",
        description="28-day pain diary",
        phases=["screening", "baseline", "intervention", "followup"],
        status="active"
    )
    db.add(study)
    db.commit()
    db.refresh(study)
    
    # Site
    site_code = generate_site_code(study_code, 1)
    site = Site(
        study_id=study.study_id,
        site_code=site_code,
        name="London Site",
        location="London, UK"
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    
    # Investigator
    inv_access_code = generate_access_code("INV-")
    investigator_user = User(
        username="investigator1",
        email="investigator@test.com",
        password_hash=get_password_hash("password123"),
        role="investigator",
        access_code=inv_access_code
    )
    db.add(investigator_user)
    db.commit()
    db.refresh(investigator_user)
    
    investigator_profile = Investigator(
        user_id=investigator_user.user_id
    )
    db.add(investigator_profile)
    db.commit()
    db.refresh(investigator_profile)
    
    # Assign investigator to site
    assignment = InvestigatorSiteAssignment(
        investigator_id=investigator_profile.investigator_id,
        site_id=site.site_id,
        role="principal_investigator",
        is_primary=True
    )
    db.add(assignment)
    db.commit()
    
    # Subject
    subj_access_code = generate_access_code("SUB-")
    subject_code = generate_subject_code(site_code, 1)
    subject_user = User(
        username="subject001",
        email="subject001@test.com",
        password_hash=get_password_hash("password123"),
        role="subject",
        access_code=subj_access_code
    )
    db.add(subject_user)
    db.commit()
    db.refresh(subject_user)
    
    subject_profile = Subject(
        user_id=subject_user.user_id,
        investigator_id=investigator_profile.investigator_id,
        study_id=study.study_id,
        subject_code=subject_code,
        current_phase="screening",
        study_day=1
    )
    db.add(subject_profile)
    db.commit()
    
    print(f"✅ Test data created!")
    print(f"\nCredentials:")
    print(f"  Designer:     designer1 / password123")
    print(f"  Investigator: investigator1 / password123 (Code: {inv_access_code})")
    print(f"  Subject:      subject001 / password123 (Code: {subj_access_code})")


if __name__ == "__main__":
    init_db()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        db = next(get_db())
        create_test_data(db)
        db.close()
