"""
Comprehensive tests for Informed Consent Module
"""

import pytest
from datetime import datetime, timedelta
from consent import (
    ConsentSchema,
    ConsentSection,
    ConsentRecord,
    ConsentValidator,
    ConsentManager,
    ConsentType,
    create_standard_consent
)


class TestConsentSchema:
    """Test consent form schema creation and validation."""
    
    def test_create_standard_consent(self):
        """Test standard consent creation."""
        consent = create_standard_consent(
            study_id="TEST_001",
            study_title="Test Study",
            pi_name="Dr. Test",
            institution="Test University",
            purpose="Testing purposes",
            procedures="Test procedures",
            risks="Test risks",
            benefits="Test benefits",
            contact_name="Dr. Test",
            contact_email="test@test.com"
        )
        
        assert consent.form_id == "consent_TEST_001"
        assert consent.study_id == "TEST_001"
        assert consent.consent_type == ConsentType.INITIAL
        assert len(consent.sections) == 7
        assert consent.signature_required is True
    
    def test_consent_sections_ordered(self):
        """Test that consent sections are properly ordered."""
        consent = create_standard_consent(
            study_id="TEST_001",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test Uni",
            purpose="Test",
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com"
        )
        
        orders = [s.order for s in consent.sections]
        assert orders == sorted(orders)  # Properly ordered
        assert len(set(orders)) == len(orders)  # No duplicates
    
    def test_consent_hash_generation(self):
        """Test consent hash generation."""
        consent = create_standard_consent(
            study_id="TEST_001",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test Uni",
            purpose="Test",
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com"
        )
        
        hash1 = consent.get_hash()
        assert len(hash1) == 64  # SHA256 produces 64 char hex
        
        # Same content should produce same hash
        hash2 = consent.get_hash()
        assert hash1 == hash2
    
    def test_consent_hash_changes_with_content(self):
        """Test that hash changes when content changes."""
        consent1 = create_standard_consent(
            study_id="TEST_001",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test Uni",
            purpose="Test purpose A",
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com",
            version="v1.0"
        )
        
        consent2 = create_standard_consent(
            study_id="TEST_001",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test Uni",
            purpose="Test purpose B",  # Different content
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com",
            version="v2.0"  # Different version
        )
        
        assert consent1.get_hash() != consent2.get_hash()


class TestConsentValidator:
    """Test consent validation logic."""
    
    def test_valid_consent_passes(self):
        """Test that valid consent passes validation."""
        consent = create_standard_consent(
            study_id="TEST_001",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test Uni",
            purpose="Test purpose with enough content to pass validation",
            procedures="Test procedures with enough content",
            risks="Test risks with enough content",
            benefits="Test benefits with enough content",
            contact_name="Dr. Test",
            contact_email="test@test.com"
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_schema(consent)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_required_sections(self):
        """Test that missing required sections fail validation."""
        # Create consent with missing sections
        consent = ConsentSchema(
            form_id="test",
            consent_type=ConsentType.INITIAL,
            title="Test",
            version="v1.0",
            study_id="TEST",
            study_title="Test",
            principal_investigator="Dr. Test",
            institution="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com",
            sections=[
                ConsentSection(
                    heading="Purpose",
                    content="Test purpose",
                    order=1
                )
                # Missing other required sections
            ]
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_schema(consent)
        
        assert is_valid is False
        assert len(errors) > 0
        # Should mention missing sections
        error_text = " ".join(errors).lower()
        assert "procedures" in error_text or "risks" in error_text or "benefits" in error_text
    
    def test_empty_section_content_fails(self):
        """Test that empty section content fails validation."""
        consent = ConsentSchema(
            form_id="test",
            consent_type=ConsentType.INITIAL,
            title="Test",
            version="v1.0",
            study_id="TEST",
            study_title="Test",
            principal_investigator="Dr. Test",
            institution="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com",
            sections=[
                ConsentSection(heading="Purpose", content="", order=1),
                ConsentSection(heading="Procedures", content="", order=2),
                ConsentSection(heading="Risks", content="", order=3),
                ConsentSection(heading="Benefits", content="", order=4)
            ]
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_schema(consent)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_missing_contact_info_fails(self):
        """Test that missing contact info fails validation."""
        consent = create_standard_consent(
            study_id="TEST",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test",
            purpose="Test",
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="",  # Empty
            contact_email=""  # Empty
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_schema(consent)
        
        assert is_valid is False
        error_text = " ".join(errors).lower()
        assert "contact" in error_text


class TestConsentAcceptance:
    """Test consent acceptance validation."""
    
    def test_valid_acceptance(self):
        """Test that valid acceptance passes."""
        consent = create_standard_consent(
            study_id="TEST",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test",
            purpose="Test purpose",
            procedures="Test procedures",
            risks="Test risks",
            benefits="Test benefits",
            contact_name="Dr. Test",
            contact_email="test@test.com"
        )
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id=consent.form_id,
            consent_version=consent.version,
            consent_hash=consent.get_hash(),
            signature="John Doe"
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_acceptance(record, consent)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_signature_fails(self):
        """Test that missing signature fails."""
        consent = create_standard_consent(
            study_id="TEST",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test",
            purpose="Test",
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com"
        )
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id=consent.form_id,
            consent_version=consent.version,
            consent_hash=consent.get_hash(),
            signature=""  # Empty signature
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_acceptance(record, consent)
        
        assert is_valid is False
        assert any("signature" in e.lower() for e in errors)
    
    def test_version_mismatch_fails(self):
        """Test that version mismatch fails."""
        consent = create_standard_consent(
            study_id="TEST",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test",
            purpose="Test",
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com",
            version="v2.0"
        )
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id=consent.form_id,
            consent_version="v1.0",  # Wrong version
            consent_hash=consent.get_hash(),
            signature="John Doe"
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_acceptance(record, consent)
        
        assert is_valid is False
        assert any("version" in e.lower() for e in errors)
    
    def test_hash_mismatch_fails(self):
        """Test that hash mismatch fails (content changed)."""
        consent = create_standard_consent(
            study_id="TEST",
            study_title="Test",
            pi_name="Dr. Test",
            institution="Test",
            purpose="Test",
            procedures="Test",
            risks="Test",
            benefits="Test",
            contact_name="Dr. Test",
            contact_email="test@test.com"
        )
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id=consent.form_id,
            consent_version=consent.version,
            consent_hash="wrong_hash_12345",  # Wrong hash
            signature="John Doe"
        )
        
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_acceptance(record, consent)
        
        assert is_valid is False
        assert any("content" in e.lower() or "changed" in e.lower() for e in errors)


class TestConsentManager:
    """Test consent management and access control."""
    
    def test_add_and_retrieve_consent(self):
        """Test adding and retrieving consent records."""
        manager = ConsentManager()
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id="consent_TEST_001",
            consent_version="v1.0",
            consent_hash="test_hash",
            signature="John Doe"
        )
        
        # Add record
        success = manager.add_consent_record(record)
        assert success is True
        
        # Retrieve record
        latest = manager.get_latest_consent("P001")
        assert latest is not None
        assert latest.participant_id == "P001"
        assert latest.signature == "John Doe"
    
    def test_has_consented(self):
        """Test checking if participant has consented."""
        manager = ConsentManager()
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id="consent_STUDY_001",
            consent_version="v1.0",
            consent_hash="test_hash",
            signature="John Doe"
        )
        
        manager.add_consent_record(record)
        
        # Should have consent
        has_consent, reason = manager.has_consented("P001", "STUDY_001")
        assert has_consent is True
        assert reason is None
        
        # Different study - should not have consent
        has_consent, reason = manager.has_consented("P001", "STUDY_002")
        assert has_consent is False
    
    def test_withdraw_consent(self):
        """Test withdrawing consent."""
        manager = ConsentManager()
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id="consent_STUDY_001",
            consent_version="v1.0",
            consent_hash="test_hash",
            signature="John Doe"
        )
        
        manager.add_consent_record(record)
        
        # Verify has consent
        has_consent, _ = manager.has_consented("P001", "STUDY_001")
        assert has_consent is True
        
        # Withdraw consent
        success = manager.withdraw_consent("P001", "STUDY_001", "Changed mind")
        assert success is True
        
        # Should no longer have consent
        has_consent, reason = manager.has_consented("P001", "STUDY_001")
        assert has_consent is False
        assert "withdrawn" in reason.lower()
    
    def test_consent_history(self):
        """Test getting consent history."""
        manager = ConsentManager()
        
        # Add multiple consents
        record1 = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id="consent_STUDY_001",
            consent_version="v1.0",
            consent_hash="hash1",
            signature="John Doe"
        )
        
        record2 = ConsentRecord(
            record_id="REC_002",
            participant_id="P001",
            consent_form_id="consent_STUDY_001",
            consent_version="v2.0",
            consent_hash="hash2",
            signature="John Doe"
        )
        
        manager.add_consent_record(record1)
        manager.add_consent_record(record2)
        
        # Get history
        history = manager.get_consent_history("P001", "STUDY_001")
        assert len(history) == 2
        
        # Should be sorted by date (most recent first)
        assert history[0].consent_version == "v2.0"
        assert history[1].consent_version == "v1.0"
    
    def test_version_requirement(self):
        """Test that specific version can be required."""
        manager = ConsentManager()
        
        record = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id="consent_STUDY_001",
            consent_version="v1.0",
            consent_hash="test_hash",
            signature="John Doe"
        )
        
        manager.add_consent_record(record)
        
        # Has v1.0 consent
        has_consent, _ = manager.has_consented("P001", "STUDY_001", "v1.0")
        assert has_consent is True
        
        # Does not have v2.0 consent
        has_consent, reason = manager.has_consented("P001", "STUDY_001", "v2.0")
        assert has_consent is False
        assert "outdated" in reason.lower() or "version" in reason.lower()


class TestConsentWorkflow:
    """Test complete consent workflows."""
    
    def test_complete_consent_workflow(self):
        """Test complete flow: create → validate → accept → check."""
        # 1. Create consent
        consent = create_standard_consent(
            study_id="WORKFLOW_001",
            study_title="Workflow Test",
            pi_name="Dr. Workflow",
            institution="Test Uni",
            purpose="Testing complete workflow with sufficient content",
            procedures="Testing procedures with sufficient content",
            risks="Testing risks with sufficient content",
            benefits="Testing benefits with sufficient content",
            contact_name="Dr. Workflow",
            contact_email="workflow@test.com"
        )
        
        # 2. Validate consent form
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_schema(consent)
        assert is_valid is True
        
        # 3. Participant accepts
        record = ConsentRecord(
            record_id="REC_WORKFLOW_001",
            participant_id="P_WORKFLOW_001",
            consent_form_id=consent.form_id,
            consent_version=consent.version,
            consent_hash=consent.get_hash(),
            signature="Workflow Participant"
        )
        
        # 4. Validate acceptance
        is_valid, errors = validator.validate_consent_acceptance(record, consent)
        assert is_valid is True
        
        # 5. Store consent
        manager = ConsentManager()
        success = manager.add_consent_record(record)
        assert success is True
        
        # 6. Check status
        has_consent, reason = manager.has_consented("P_WORKFLOW_001", "WORKFLOW_001")
        assert has_consent is True
        assert reason is None
    
    def test_re_consent_workflow(self):
        """Test re-consent when study protocol changes."""
        manager = ConsentManager()
        validator = ConsentValidator()
        
        # Original consent (v1.0)
        consent_v1 = create_standard_consent(
            study_id="RECONSENT_001",
            study_title="Re-consent Test",
            pi_name="Dr. Test",
            institution="Test",
            purpose="Original purpose",
            procedures="Original procedures",
            risks="Original risks",
            benefits="Original benefits",
            contact_name="Dr. Test",
            contact_email="test@test.com",
            version="v1.0"
        )
        
        # Participant accepts v1.0
        record_v1 = ConsentRecord(
            record_id="REC_001",
            participant_id="P001",
            consent_form_id=consent_v1.form_id,
            consent_version="v1.0",
            consent_hash=consent_v1.get_hash(),
            signature="Test Participant"
        )
        
        manager.add_consent_record(record_v1)
        
        # Study changes - new consent required (v2.0)
        consent_v2 = create_standard_consent(
            study_id="RECONSENT_001",
            study_title="Re-consent Test",
            pi_name="Dr. Test",
            institution="Test",
            purpose="Updated purpose with new information",
            procedures="Updated procedures",
            risks="Updated risks",
            benefits="Updated benefits",
            contact_name="Dr. Test",
            contact_email="test@test.com",
            version="v2.0"
        )
        
        # Participant has v1.0 but v2.0 is required
        has_consent, reason = manager.has_consented("P001", "RECONSENT_001", "v2.0")
        assert has_consent is False
        
        # Participant re-consents to v2.0
        record_v2 = ConsentRecord(
            record_id="REC_002",
            participant_id="P001",
            consent_form_id=consent_v2.form_id,
            consent_version="v2.0",
            consent_hash=consent_v2.get_hash(),
            signature="Test Participant"
        )
        
        manager.add_consent_record(record_v2)
        
        # Now has v2.0 consent
        has_consent, reason = manager.has_consented("P001", "RECONSENT_001", "v2.0")
        assert has_consent is True
        
        # History shows both consents
        history = manager.get_consent_history("P001", "RECONSENT_001")
        assert len(history) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])