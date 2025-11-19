"""
Tests for Study Configuration Module
"""

import pytest
from study_config import (
    StudyConfiguration,
    ParticipantUIConfig,
    StudyFeatures,
    validate_configuration
)


class TestPresets:
    """Test preset configurations."""
    
    def test_simple_survey_preset(self):
        """Simple survey should have minimal UI."""
        config = StudyConfiguration.simple_survey("TEST_001", "Test Survey")
        
        assert config.study_id == "TEST_001"
        assert config.study_name == "Test Survey"
        
        # Should show
        assert config.participant_ui.show_progress_bar is True
        assert config.participant_ui.show_next_form_preview is True
        assert config.participant_ui.show_completion_message is True
        
        # Should hide
        assert config.participant_ui.show_phase_name is False
        assert config.participant_ui.show_completion_percentage is False
        assert config.participant_ui.show_forms_remaining is False
        
        # Features
        assert config.features.enable_skip_logic is True
        assert config.features.require_informed_consent is True
        assert config.features.enable_eligibility_check is False
    
    def test_clinical_trial_preset(self):
        """Clinical trial should have full UI."""
        config = StudyConfiguration.clinical_trial("TRIAL_001", "Test Trial")
        
        # Should show more elements
        assert config.participant_ui.show_progress_bar is True
        assert config.participant_ui.show_completion_percentage is True
        assert config.participant_ui.show_phase_name is True
        assert config.participant_ui.show_forms_remaining is True
        assert config.participant_ui.show_upcoming_forms is True
        
        # More features enabled
        assert config.features.enable_eligibility_check is True
        assert config.features.enable_progress_tracking is True
    
    def test_minimal_preset(self):
        """Minimal should show almost nothing."""
        config = StudyConfiguration.minimal("MIN_001", "Minimal")
        
        # Should hide everything except completion message
        assert config.participant_ui.show_progress_bar is False
        assert config.participant_ui.show_completion_percentage is False
        assert config.participant_ui.show_phase_name is False
        
        # But still show completion message
        assert config.participant_ui.show_completion_message is True
        
        # Still require basics
        assert config.features.enable_form_validation is True
        assert config.features.require_informed_consent is True


class TestValidation:
    """Test configuration validation."""
    
    def test_valid_configurations_pass(self):
        """Valid configs should pass validation."""
        configs = [
            StudyConfiguration.simple_survey("S1", "S1"),
            StudyConfiguration.clinical_trial("S2", "S2"),
            StudyConfiguration.minimal("S3", "S3")
        ]
        
        for config in configs:
            is_valid, errors = validate_configuration(config)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_completion_percentage_requires_progress_bar(self):
        """Can't show completion % without progress bar."""
        config = StudyConfiguration(
            study_id="TEST",
            study_name="Test",
            participant_ui=ParticipantUIConfig(
                show_progress_bar=False,
                show_completion_percentage=True  # Invalid!
            )
        )
        
        is_valid, errors = validate_configuration(config)
        assert is_valid is False
        assert len(errors) > 0
        assert "completion_percentage" in errors[0]
        assert "progress_bar" in errors[0]
    
    def test_upcoming_forms_requires_next_form(self):
        """Can't show upcoming forms without next form preview."""
        config = StudyConfiguration(
            study_id="TEST",
            study_name="Test",
            participant_ui=ParticipantUIConfig(
                show_next_form_preview=False,
                show_upcoming_forms=True  # Invalid!
            )
        )
        
        is_valid, errors = validate_configuration(config)
        assert is_valid is False
        assert "upcoming_forms" in errors[0]
    
    def test_form_skipping_requires_ui_option(self):
        """Can't enable skipping without UI option."""
        config = StudyConfiguration(
            study_id="TEST",
            study_name="Test",
            participant_ui=ParticipantUIConfig(
                show_skip_option=False
            ),
            features=StudyFeatures(
                enable_form_skipping=True  # Invalid!
            )
        )
        
        is_valid, errors = validate_configuration(config)
        assert is_valid is False
        assert "form_skipping" in errors[0]
    
    def test_eligibility_requires_consent(self):
        """Eligibility check requires informed consent."""
        config = StudyConfiguration(
            study_id="TEST",
            study_name="Test",
            features=StudyFeatures(
                require_informed_consent=False,
                enable_eligibility_check=True  # Invalid!
            )
        )
        
        is_valid, errors = validate_configuration(config)
        assert is_valid is False
        assert "eligibility" in errors[0]


class TestParticipantView:
    """Test participant view filtering."""
    
    def test_simple_survey_filters_correctly(self):
        """Simple survey should filter out most fields."""
        config = StudyConfiguration.simple_survey("TEST", "Test")
        
        context = {
            'progress_bar': 50,
            'completion_pct': 50,
            'forms_remaining': 2,
            'phase_name': 'Intervention',
            'next_form': 'Daily Diary',
            'study_duration': 90
        }
        
        view = config.get_participant_view_data(context)
        
        # Should include
        assert 'progress_bar' in view
        assert 'next_form' in view
        
        # Should exclude
        assert 'completion_pct' not in view
        assert 'forms_remaining' not in view
        assert 'phase_name' not in view
        assert 'study_duration' not in view
    
    def test_clinical_trial_shows_more(self):
        """Clinical trial should show more fields."""
        config = StudyConfiguration.clinical_trial("TEST", "Test")
        
        context = {
            'progress_bar': 50,
            'completion_pct': 50,
            'forms_remaining': 2,
            'phase_name': 'Intervention',
            'next_form': 'Daily Diary'
        }
        
        view = config.get_participant_view_data(context)
        
        # Should include most/all
        assert 'progress_bar' in view
        assert 'completion_pct' in view
        assert 'forms_remaining' in view
        assert 'phase_name' in view
        assert 'next_form' in view
    
    def test_minimal_shows_almost_nothing(self):
        """Minimal config should filter out almost everything."""
        config = StudyConfiguration.minimal("TEST", "Test")
        
        context = {
            'progress_bar': 50,
            'completion_pct': 50,
            'phase_name': 'Intervention',
            'next_form': 'Daily Diary'
        }
        
        view = config.get_participant_view_data(context)
        
        # Should be mostly empty
        assert len(view) <= 2  # Maybe completion message


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_summary_method(self):
        """Summary should return readable string."""
        config = StudyConfiguration.simple_survey("TEST", "Test Study")
        summary = config.summary()
        
        assert "Test Study" in summary
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_get_enabled_features(self):
        """Should list enabled features."""
        config = StudyConfiguration.clinical_trial("TEST", "Test")
        features = config.features.get_enabled_features()
        
        assert isinstance(features, list)
        assert "Skip Logic" in features
        assert "Validation" in features
        assert "Informed Consent" in features


if __name__ == "__main__":
    # Run with: python test_study_config.py
    pytest.main([__file__, "-v", "--tb=short"])