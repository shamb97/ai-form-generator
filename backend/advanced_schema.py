"""
Advanced Database Schema
Tables for 9 advanced components
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# ============================================================================
# COMPONENT 2: EVENT TRIGGER SYSTEM
# ============================================================================

class EventTrigger(Base):
    """Store event-triggered schedule changes"""
    __tablename__ = "event_triggers"
    
    id = Column(Integer, primary_key=True)
    study_id = Column(Integer, nullable=False)
    subject_id = Column(Integer, nullable=False)
    event_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # 'withdrawal', 'adverse_event', 'protocol_deviation'
    trigger_day = Column(Integer, nullable=False)  # Day when event occurred
    trigger_datetime = Column(DateTime, default=datetime.now)
    triggered_forms = Column(JSON)  # List of forms that should be triggered
    priority = Column(Integer, default=1)  # Event priority (higher = more important)
    handled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

# ============================================================================
# COMPONENT 3: CONDITIONAL DEPENDENCIES
# ============================================================================

class FormActivationStatus(Base):
    """Track which forms are unlocked/activated for a subject"""
    __tablename__ = "form_activation_status"
    
    id = Column(Integer, primary_key=True)
    study_id = Column(Integer, nullable=False)
    subject_id = Column(Integer, nullable=False)
    form_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)
    activation_condition = Column(Text)  # JSON: condition that must be met
    activated_by_event = Column(Integer)  # FK to event_triggers.id
    activated_at = Column(DateTime)
    deactivated_at = Column(DateTime)

# ============================================================================
# COMPONENT 4: FORM INSTANCE MANAGER (Multiple per day)
# ============================================================================

class FormInstance(Base):
    """Allow multiple instances of same form on same day"""
    __tablename__ = "form_instances"
    
    id = Column(Integer, primary_key=True)
    study_id = Column(Integer, nullable=False)
    subject_id = Column(Integer, nullable=False)
    form_id = Column(Integer, nullable=False)
    study_day = Column(Integer, nullable=False)
    instance_number = Column(Integer, default=1)  # 1st, 2nd, 3rd instance
    instance_label = Column(String)  # "Morning", "Evening", "After Meal"
    scheduled_time = Column(String)  # "09:00", "21:00"
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    data = Column(JSON)  # Form submission data
    created_at = Column(DateTime, default=datetime.now)

# ============================================================================
# COMPONENT 5: PHASE TRANSITION CONTROLLER
# ============================================================================

class PhaseTransition(Base):
    """Track when subjects move between study phases"""
    __tablename__ = "phase_transitions"
    
    id = Column(Integer, primary_key=True)
    study_id = Column(Integer, nullable=False)
    subject_id = Column(Integer, nullable=False)
    from_phase = Column(String)
    to_phase = Column(String, nullable=False)
    transition_day = Column(Integer, nullable=False)
    transition_datetime = Column(DateTime, default=datetime.now)
    transition_type = Column(String)  # 'automatic', 'manual', 'event_triggered'
    approved_by_user_id = Column(Integer)
    incomplete_forms_count = Column(Integer, default=0)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# ============================================================================
# COMPONENT 7: AUDIT TRAIL SYSTEM
# ============================================================================

class AuditLog(Base):
    """Complete audit trail of all system actions"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    user_id = Column(Integer)
    user_role = Column(String)  # 'designer', 'investigator', 'subject'
    subject_id = Column(Integer)
    study_id = Column(Integer)
    action_type = Column(String, nullable=False)  # 'create', 'update', 'delete', 'complete', 'trigger_event'
    entity_type = Column(String)  # 'study', 'form', 'subject', 'phase'
    entity_id = Column(Integer)
    action_details = Column(Text)  # JSON with detailed info
    before_state = Column(Text)    # JSON snapshot before change
    after_state = Column(Text)     # JSON snapshot after change
    reason = Column(Text)
    ip_address = Column(String)
    
# ============================================================================
# CREATE ALL TABLES FUNCTION
# ============================================================================

def create_advanced_tables():
    """Create all advanced feature tables in database"""
    from sqlalchemy import create_engine
    
    # Create database engine
    engine = create_engine('sqlite:///ai_form_generator_advanced.db')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("✅ Advanced database tables created!")
    print("\nCreated tables:")
    print("  1. event_triggers (Component 2: Event System)")
    print("  2. form_activation_status (Component 3: Conditional Dependencies)")
    print("  3. form_instances (Component 4: Multiple Forms Per Day)")
    print("  4. phase_transitions (Component 5: Phase Transitions)")
    print("  5. audit_log (Component 7: Audit Trail)")
    print("\nDatabase file: ai_form_generator_advanced.db")

if __name__ == "__main__":
    create_advanced_tables()
