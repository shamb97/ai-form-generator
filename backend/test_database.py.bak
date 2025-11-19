"""
Test suite for database operations.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from database import Base, Study, Form, DayType, FormCompletion
from database import create_study, create_form, create_day_type, create_completion
from database import get_study, get_all_studies, get_forms_by_study, get_day_types_by_study
from database import is_form_complete

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_research_forms.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_create_study(db):
    """Test creating a study."""
    study = create_study(db, "Test Study", "Test description")
    
    assert study.id is not None
    assert study.name == "Test Study"
    assert study.description == "Test description"
    assert study.created_at is not None
    print("✅ Study creation works")


def test_create_form(db):
    """Test creating a form."""
    study = create_study(db, "Test Study")
    
    schema = {
        "title": "Daily Diary",
        "type": "object",
        "properties": {
            "pain_level": {"type": "number", "minimum": 0, "maximum": 10}
        }
    }
    
    form = create_form(db, study.id, "daily_diary", "Daily Pain Diary", 1, schema)
    
    assert form.id is not None
    assert form.form_id == "daily_diary"
    assert form.frequency == 1
    assert form.schema_json == schema
    assert form.study_id == study.id
    print("✅ Form creation works")


def test_create_day_type(db):
    """Test creating a day type."""
    study = create_study(db, "Test Study")
    
    day_type = create_day_type(
        db,
        study.id,
        "a_day_intervention",
        "day_in_cycle NOT IN [7, 14, 21] AND phase == 'intervention'",
        ["form_a"],
        list(range(1, 22)),
        "intervention",
        priority=3
    )
    
    assert day_type.id is not None
    assert day_type.day_type_id == "a_day_intervention"
    assert day_type.priority == 3
    print("✅ Day type creation works")


def test_create_completion(db):
    """Test recording a form completion."""
    study = create_study(db, "Test Study")
    schema = {"title": "Test Form"}
    form = create_form(db, study.id, "test_form", "Test Form", 1, schema)
    
    data = {"pain_level": 7, "notes": "Moderate pain today"}
    completion = create_completion(
        db,
        study.id,
        form.id,
        "a_day_intervention",
        "intervention",
        datetime.now(),
        data
    )
    
    assert completion.id is not None
    assert completion.data == data
    assert completion.phase == "intervention"
    print("✅ Form completion recording works")


def test_is_form_complete(db):
    """Test checking form completion status."""
    study = create_study(db, "Test Study")
    schema = {"title": "Test Form"}
    form = create_form(db, study.id, "test_form", "Test Form", 1, schema)
    
    test_date = datetime(2024, 11, 8, 10, 0, 0)
    
    # Initially not complete
    assert is_form_complete(db, study.id, form.id, "a_day", "intervention", test_date) is False
    
    # Complete the form
    create_completion(db, study.id, form.id, "a_day", "intervention", test_date, {"data": "test"})
    
    # Now should be complete
    assert is_form_complete(db, study.id, form.id, "a_day", "intervention", test_date) is True
    print("✅ Form completion checking works")


def test_phase_isolation(db):
    """Test that completions are phase-specific."""
    study = create_study(db, "Test Study")
    schema = {"title": "Test Form"}
    form = create_form(db, study.id, "test_form", "Test Form", 1, schema)
    
    test_date = datetime(2024, 11, 8, 10, 0, 0)
    
    # Complete in screening phase
    create_completion(db, study.id, form.id, "a_day", "screening", test_date, {"phase": "screening"})
    
    # Should be complete in screening
    assert is_form_complete(db, study.id, form.id, "a_day", "screening", test_date) is True
    
    # Should NOT be complete in intervention
    assert is_form_complete(db, study.id, form.id, "a_day", "intervention", test_date) is False
    print("✅ Phase isolation works correctly")


def test_relationships(db):
    """Test database relationships."""
    study = create_study(db, "Test Study")
    schema = {"title": "Form 1"}
    form1 = create_form(db, study.id, "form_a", "Form A", 1, schema)
    form2 = create_form(db, study.id, "form_b", "Form B", 7, schema)
    
    # Test study -> forms relationship
    retrieved_study = get_study(db, study.id)
    assert len(retrieved_study.forms) == 2
    assert retrieved_study.forms[0].form_id in ["form_a", "form_b"]
    print("✅ Database relationships work")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
