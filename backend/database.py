"""
Database models and operations for AI Form Generator.
Uses SQLite with SQLAlchemy ORM.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

# Database setup
DATABASE_URL = "sqlite:///./research_forms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELS ====================

class Study(Base):
    """Represents a research study with its configuration."""
    __tablename__ = "studies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    forms = relationship("Form", back_populates="study", cascade="all, delete-orphan")
    day_types = relationship("DayType", back_populates="study", cascade="all, delete-orphan")
    completions = relationship("FormCompletion", back_populates="study", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Study(id={self.id}, name='{self.name}')>"


class Form(Base):
    """Represents a single form with its JSON schema."""
    __tablename__ = "forms"
    
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False)
    form_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
    schema_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    study = relationship("Study", back_populates="forms")
    completions = relationship("FormCompletion", back_populates="form", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Form(id={self.id}, form_id='{self.form_id}', frequency={self.frequency})>"


class DayType(Base):
    """Represents a day type (e.g., 'abc_day', 'a_day', 'eot_day')."""
    __tablename__ = "day_types"
    
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False)
    day_type_id = Column(String, nullable=False)
    condition = Column(Text, nullable=False)
    forms_list = Column(JSON, nullable=False)
    cycle_days = Column(JSON, nullable=False)
    phase_context = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    study = relationship("Study", back_populates="day_types")
    
    def __repr__(self):
        return f"<DayType(id={self.id}, day_type_id='{self.day_type_id}', phase='{self.phase_context}')>"


class FormCompletion(Base):
    """Tracks when a form was completed."""
    __tablename__ = "form_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    day_type_id = Column(String, nullable=False)
    phase = Column(String, nullable=False)
    submission_date = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    study = relationship("Study", back_populates="completions")
    form = relationship("Form", back_populates="completions")
    
    def __repr__(self):
        return f"<FormCompletion(id={self.id}, form_id={self.form_id}, phase='{self.phase}')>"


# ==================== DATABASE OPERATIONS ====================

def init_db():
    """Initialize the database (create tables)."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


def get_db():
    """Get database session (for dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== CRUD OPERATIONS ====================

def create_study(db, name: str, description: str = ""):
    """Create a new study."""
    study = Study(name=name, description=description)
    db.add(study)
    db.commit()
    db.refresh(study)
    return study


def create_form(db, study_id: int, form_id: str, title: str, frequency: int, schema_json: dict):
    """Create a new form."""
    form = Form(
        study_id=study_id,
        form_id=form_id,
        title=title,
        frequency=frequency,
        schema_json=schema_json
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    return form


def create_day_type(db, study_id: int, day_type_id: str, condition: str, 
                    forms_list: list, cycle_days: list, phase_context: str, priority: int = 0):
    """Create a new day type."""
    day_type = DayType(
        study_id=study_id,
        day_type_id=day_type_id,
        condition=condition,
        forms_list=forms_list,
        cycle_days=cycle_days,
        phase_context=phase_context,
        priority=priority
    )
    db.add(day_type)
    db.commit()
    db.refresh(day_type)
    return day_type


def create_completion(db, study_id: int, form_id: int, day_type_id: str, 
                      phase: str, submission_date: datetime, data: dict):
    """Record a form completion."""
    completion = FormCompletion(
        study_id=study_id,
        form_id=form_id,
        day_type_id=day_type_id,
        phase=phase,
        submission_date=submission_date,
        data=data
    )
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return completion


def get_study(db, study_id: int):
    """Get a study by ID."""
    return db.query(Study).filter(Study.id == study_id).first()


def get_all_studies(db):
    """Get all studies."""
    return db.query(Study).all()


def get_forms_by_study(db, study_id: int):
    """Get all forms for a study."""
    return db.query(Form).filter(Form.study_id == study_id).all()


def get_day_types_by_study(db, study_id: int):
    """Get all day types for a study, ordered by priority."""
    return db.query(DayType).filter(DayType.study_id == study_id).order_by(DayType.priority.desc()).all()


def get_completions_by_study(db, study_id: int):
    """Get all completions for a study."""
    return db.query(FormCompletion).filter(FormCompletion.study_id == study_id).all()


def is_form_complete(db, study_id: int, form_id: int, day_type_id: str, phase: str, date: datetime) -> bool:
    """Check if a form is completed for specific context."""
    completion = db.query(FormCompletion).filter(
        FormCompletion.study_id == study_id,
        FormCompletion.form_id == form_id,
        FormCompletion.day_type_id == day_type_id,
        FormCompletion.phase == phase,
        FormCompletion.submission_date == date
    ).first()
    return completion is not None


# ==================== UTILITY FUNCTIONS ====================

def reset_database():
    """Drop all tables and recreate (USE WITH CAUTION - DELETES ALL DATA)."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("⚠️  Database reset complete - all data deleted!")


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
    print("Database ready at:", DATABASE_URL)