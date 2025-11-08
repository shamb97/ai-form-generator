"""
Informed Consent Module

Handles creation, display, acceptance, and tracking of informed consent
for research studies. Ensures ethical compliance and regulatory requirements.

Key Features:
- Consent form creation with structured sections
- Acceptance tracking with signatures
- Version control for consent updates
- Access control (can't participate without consent)
- Audit trail for compliance
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import hashlib
import json


class ConsentType(str, Enum):
    """Types of consent forms."""
    INITIAL = "initial"  # First consent at study entry
    RE_CONSENT = "re_consent"  # Updated consent during study
    WITHDRAWAL = "withdrawal"  # Consent withdrawal form
    ASSENT = "assent"  # For minors (with parental consent)


class ConsentSection(BaseModel):
    """
    A section of the consent form.
    
    Example:
        {
            "heading": "Study Purpose",
            "content": "This study aims to understand...",
            "order": 1
        }
    """
    heading: str = Field(description="Section heading")
    content: str = Field(description="Section content (can include HTML)")
    order: int = Field(description="Display order (1, 2, 3...)")
    required_reading: bool = Field(
        default=True,
        description="Must user scroll through this section?"
    )


class ConsentSchema(BaseModel):
    """
    Complete consent form schema.
    
    This is a special form type specifically for informed consent.
    """
    form_id: str = Field(description="Unique consent form ID")
    form_type: str = Field(default="consent", description="Always 'consent'")
    consent_type: ConsentType = Field(description="Type of consent")
    
    # Metadata
    title: str = Field(description="Consent form title")
    version: str = Field(description="Consent version (e.g., 'v1.0', 'v2.1')")
    effective_date: datetime = Field(
        default_factory=datetime.now,
        description="When this consent version became effective"
    )
    
    # Study information
    study_id: str = Field(description="Associated study ID")
    study_title: str = Field(description="Full study title")
    principal_investigator: str = Field(description="PI name")
    institution: str = Field(description="Institution/organization")
    
    # Contact information
    contact_name: str = Field(description="Contact person for questions")
    contact_email: str = Field(description="Contact email")
    contact_phone: Optional[str] = None
    
    # Consent content
    sections: List[ConsentSection] = Field(
        description="Structured sections of consent form"
    )
    
    # Requirements
    signature_required: bool = Field(
        default=True,
        description="Require typed signature (full name)"
    )
    date_required: bool = Field(
        default=True,
        description="Require date of consent"
    )
    witness_required: bool = Field(
        default=False,
        description="Require witness signature (for some studies)"
    )
    
    # Additional options
    allow_download: bool = Field(
        default=True,
        description="Allow participant to download copy"
    )
    require_scroll_through: bool = Field(
        default=True,
        description="Require scrolling through entire document"
    )
    
    def get_hash(self) -> str:
        """
        Generate unique hash of consent content.
        
        Used to detect if consent has changed (requiring re-consent).
        """
        # Create deterministic string of key content
        content_str = json.dumps({
            "version": self.version,
            "sections": [s.model_dump() for s in self.sections],
            "study_id": self.study_id
        }, sort_keys=True)
        
        return hashlib.sha256(content_str.encode()).hexdigest()


class ConsentRecord(BaseModel):
    """
    Record of a participant's consent acceptance.
    
    This is the audit trail - who consented, when, to what version.
    """
    record_id: str = Field(description="Unique record ID")
    
    # Who
    participant_id: str = Field(description="Participant who consented")
    participant_name: Optional[str] = None  # If collected
    
    # What
    consent_form_id: str = Field(description="Which consent form")
    consent_version: str = Field(description="Version of consent")
    consent_hash: str = Field(description="Hash of consent content")
    
    # When
    accepted_at: datetime = Field(
        default_factory=datetime.now,
        description="When consent was given"
    )
    
    # How
    signature: str = Field(description="Participant's typed signature")
    signature_date: datetime = Field(
        default_factory=datetime.now,
        description="Date participant signed"
    )
    
    # Witness (if required)
    witness_signature: Optional[str] = None
    witness_name: Optional[str] = None
    witness_date: Optional[datetime] = None
    
    # Audit trail
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Status
    is_active: bool = Field(
        default=True,
        description="False if consent withdrawn"
    )
    withdrawn_at: Optional[datetime] = None
    withdrawal_reason: Optional[str] = None


class ConsentValidator:
    """
    Validates consent forms and acceptance records.
    """
    
    @staticmethod
    def validate_consent_schema(schema: ConsentSchema) -> tuple[bool, List[str]]:
        """
        Validate consent form schema for completeness.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Must have at least basic sections
        required_section_headings = [
            "purpose",
            "procedures", 
            "risks",
            "benefits"
        ]
        
        section_headings = [s.heading.lower() for s in schema.sections]
        
        for required in required_section_headings:
            if not any(required in heading for heading in section_headings):
                errors.append(
                    f"Missing required section: '{required}'. "
                    f"Ethical consent requires clear communication of study {required}."
                )
        
        # Must have contact information
        if not schema.contact_name or not schema.contact_email:
            errors.append(
                "Contact information required. Participants must know who to contact "
                "with questions or concerns."
            )
        
        # Sections must be ordered
        orders = [s.order for s in schema.sections]
        if len(orders) != len(set(orders)):
            errors.append("Section orders must be unique")
        
        # Content must not be empty
        for section in schema.sections:
            if len(section.content.strip()) < 10:
                errors.append(
                    f"Section '{section.heading}' has insufficient content. "
                    f"Provide meaningful information."
                )
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def validate_consent_acceptance(
        record: ConsentRecord,
        schema: ConsentSchema
    ) -> tuple[bool, List[str]]:
        """
        Validate that a consent acceptance is complete and valid.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Signature required
        if schema.signature_required:
            if not record.signature or len(record.signature.strip()) < 2:
                errors.append(
                    "Valid signature required. Please type your full name."
                )
        
        # Witness required
        if schema.witness_required:
            if not record.witness_signature or not record.witness_name:
                errors.append(
                    "Witness signature required for this study."
                )
        
        # Version must match
        if record.consent_version != schema.version:
            errors.append(
                f"Consent version mismatch. Expected {schema.version}, "
                f"got {record.consent_version}"
            )
        
        # Hash must match (ensures content hasn't changed)
        if record.consent_hash != schema.get_hash():
            errors.append(
                "Consent content has changed since form was displayed. "
                "Please review the updated consent form."
            )
        
        return (len(errors) == 0, errors)


class ConsentManager:
    """
    Manages consent records and access control.
    
    In-memory storage for now (will use database on Day 5).
    """
    
    def __init__(self):
        self.consent_records: Dict[str, List[ConsentRecord]] = {}
        # Key: participant_id, Value: List of consent records
    
    def add_consent_record(self, record: ConsentRecord) -> bool:
        """
        Add a consent acceptance record.
        
        Returns:
            True if added successfully
        """
        participant_id = record.participant_id
        
        if participant_id not in self.consent_records:
            self.consent_records[participant_id] = []
        
        # Add record
        self.consent_records[participant_id].append(record)
        return True
    
    def get_latest_consent(
        self,
        participant_id: str,
        study_id: Optional[str] = None
    ) -> Optional[ConsentRecord]:
        """
        Get the most recent active consent for a participant.
        
        Args:
            participant_id: Participant ID
            study_id: Optional study filter
            
        Returns:
            Latest consent record, or None if not found
        """
        if participant_id not in self.consent_records:
            return None
        
        records = self.consent_records[participant_id]
        
        # Filter by study if specified
        if study_id:
            records = [r for r in records if study_id in r.consent_form_id]
        
        # Filter active only
        active_records = [r for r in records if r.is_active]
        
        if not active_records:
            return None
        
        # Return most recent
        return max(active_records, key=lambda r: r.accepted_at)
    
    def has_consented(
        self,
        participant_id: str,
        study_id: str,
        required_version: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if participant has valid consent for a study.
        
        Args:
            participant_id: Participant ID
            study_id: Study ID
            required_version: Optional specific version required
            
        Returns:
            (has_consent, reason_if_not)
        """
        # Check for any consent record (including withdrawn)
        if participant_id not in self.consent_records:
            return False, "No consent record found"
        
        records = self.consent_records[participant_id]
        
        # Filter by study
        study_records = [r for r in records if study_id in r.consent_form_id]
        
        if not study_records:
            return False, "No consent record found"
        
        # Get latest (including withdrawn)
        latest = max(study_records, key=lambda r: r.accepted_at)
        
        # Check if withdrawn
        if not latest.is_active:
            return False, "Consent has been withdrawn"
        
        # Check version if required
        if required_version and latest.consent_version != required_version:
            return False, f"Consent version outdated. Current: {latest.consent_version}, Required: {required_version}"
        
        return True, None
    
    def withdraw_consent(
        self,
        participant_id: str,
        study_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Withdraw participant's consent.
        
        Marks all active consents for this study as inactive.
        
        Returns:
            True if withdrawal successful
        """
        if participant_id not in self.consent_records:
            return False
        
        records = self.consent_records[participant_id]
        
        # Mark all active consents for this study as withdrawn
        withdrawn_count = 0
        for record in records:
            if study_id in record.consent_form_id and record.is_active:
                record.is_active = False
                record.withdrawn_at = datetime.now()
                record.withdrawal_reason = reason
                withdrawn_count += 1
        
        return withdrawn_count > 0
    
    def get_consent_history(
        self,
        participant_id: str,
        study_id: Optional[str] = None
    ) -> List[ConsentRecord]:
        """
        Get complete consent history for a participant.
        
        Includes withdrawn consents (for audit trail).
        """
        if participant_id not in self.consent_records:
            return []
        
        records = self.consent_records[participant_id]
        
        if study_id:
            records = [r for r in records if study_id in r.consent_form_id]
        
        # Sort by date (most recent first)
        return sorted(records, key=lambda r: r.accepted_at, reverse=True)


# === UTILITY FUNCTIONS ===

def create_standard_consent(
    study_id: str,
    study_title: str,
    pi_name: str,
    institution: str,
    purpose: str,
    procedures: str,
    risks: str,
    benefits: str,
    contact_name: str,
    contact_email: str,
    version: str = "v1.0"
) -> ConsentSchema:
    """
    Helper to create a standard consent form with common sections.
    
    Example:
        consent = create_standard_consent(
            study_id="STUDY_001",
            study_title="Effects of Exercise on Mood",
            pi_name="Dr. Jane Smith",
            institution="University Medical Center",
            purpose="To understand how exercise affects mood...",
            procedures="You will be asked to complete daily surveys...",
            risks="Risks are minimal. You may experience...",
            benefits="There may be no direct benefit to you...",
            contact_name="Dr. Jane Smith",
            contact_email="jane.smith@university.edu"
        )
    """
    sections = [
        ConsentSection(
            heading="Study Purpose",
            content=purpose,
            order=1
        ),
        ConsentSection(
            heading="Study Procedures",
            content=procedures,
            order=2
        ),
        ConsentSection(
            heading="Risks and Discomforts",
            content=risks,
            order=3
        ),
        ConsentSection(
            heading="Benefits",
            content=benefits,
            order=4
        ),
        ConsentSection(
            heading="Confidentiality",
            content=(
                "Your information will be kept confidential. Data will be stored securely "
                "and only authorized research personnel will have access. Your identity will "
                "not be revealed in any publications or presentations resulting from this study."
            ),
            order=5
        ),
        ConsentSection(
            heading="Voluntary Participation",
            content=(
                "Your participation in this study is completely voluntary. You may refuse to "
                "participate or withdraw at any time without penalty or loss of benefits to "
                "which you are otherwise entitled."
            ),
            order=6
        ),
        ConsentSection(
            heading="Questions and Contacts",
            content=(
                f"If you have questions about this study, please contact {contact_name} "
                f"at {contact_email}."
            ),
            order=7
        )
    ]
    
    return ConsentSchema(
        form_id=f"consent_{study_id}",
        consent_type=ConsentType.INITIAL,
        title=f"Informed Consent: {study_title}",
        version=version,
        study_id=study_id,
        study_title=study_title,
        principal_investigator=pi_name,
        institution=institution,
        contact_name=contact_name,
        contact_email=contact_email,
        sections=sections
    )


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    print("=" * 60)
    print("INFORMED CONSENT MODULE - EXAMPLES")
    print("=" * 60)
    
    # Example 1: Create consent form
    print("\n1. CREATE CONSENT FORM")
    print("-" * 60)
    
    consent = create_standard_consent(
        study_id="STUDY_001",
        study_title="Daily Mood and Exercise Study",
        pi_name="Dr. Jane Smith",
        institution="University Medical Center",
        purpose="This study aims to understand the relationship between daily exercise and mood.",
        procedures="You will complete a daily survey about your exercise and mood for 30 days.",
        risks="Risks are minimal. You may experience minor discomfort from self-reflection.",
        benefits="You may gain insights into your own mood patterns. The study may contribute to scientific understanding.",
        contact_name="Dr. Jane Smith",
        contact_email="jane.smith@university.edu",
        version="v1.0"
    )
    
    print(f"Created consent: {consent.form_id}")
    print(f"Version: {consent.version}")
    print(f"Sections: {len(consent.sections)}")
    print(f"Hash: {consent.get_hash()[:16]}...")
    
    # Example 2: Validate consent form
    print("\n2. VALIDATE CONSENT FORM")
    print("-" * 60)
    
    validator = ConsentValidator()
    is_valid, errors = validator.validate_consent_schema(consent)
    
    if is_valid:
        print("✅ Consent form is valid")
    else:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Example 3: Participant accepts consent
    print("\n3. PARTICIPANT ACCEPTS CONSENT")
    print("-" * 60)
    
    record = ConsentRecord(
        record_id="REC_001",
        participant_id="PARTICIPANT_001",
        participant_name="John Doe",
        consent_form_id=consent.form_id,
        consent_version=consent.version,
        consent_hash=consent.get_hash(),
        signature="John Doe",
        ip_address="192.168.1.100"
    )
    
    # Validate acceptance
    is_valid, errors = validator.validate_consent_acceptance(record, consent)
    
    if is_valid:
        print("✅ Consent acceptance valid")
        print(f"   Participant: {record.participant_name}")
        print(f"   Signed at: {record.accepted_at}")
        print(f"   Signature: {record.signature}")
    else:
        print("❌ Acceptance errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Example 4: Consent management
    print("\n4. CONSENT MANAGEMENT")
    print("-" * 60)
    
    manager = ConsentManager()
    
    # Add consent record
    manager.add_consent_record(record)
    print(f"✅ Added consent record for {record.participant_id}")
    
    # Check if participant has consented
    has_consent, reason = manager.has_consented("PARTICIPANT_001", "STUDY_001")
    print(f"   Has consent: {has_consent}")
    
    # Get latest consent
    latest = manager.get_latest_consent("PARTICIPANT_001")
    print(f"   Latest consent: {latest.consent_version}")
    
    # Withdraw consent
    withdrawn = manager.withdraw_consent(
        "PARTICIPANT_001",
        "STUDY_001",
        reason="Changed mind"
    )
    print(f"   Withdrawn: {withdrawn}")
    
    # Check again
    has_consent, reason = manager.has_consented("PARTICIPANT_001", "STUDY_001")
    print(f"   Has consent after withdrawal: {has_consent}")
    print(f"   Reason: {reason}")
    
    print("\n" + "=" * 60)
    print("✅ Consent module working!")
    print("=" * 60)