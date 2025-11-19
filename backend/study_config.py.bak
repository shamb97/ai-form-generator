"""
Study Configuration Module
Controls frontend display options and feature enablement.

This module determines what participants see vs what investigators see,
balancing functionality with simplicity for a better user experience.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ParticipantUIConfig(BaseModel):
    """
    Controls what participants see in the frontend.
    
    Philosophy: Participants should see only what helps them complete
    their tasks. Overwhelming them with metadata reduces compliance.
    """
    
    # === PROGRESS INDICATORS ===
    show_progress_bar: bool = Field(
        default=True,
        description="Show visual progress bar (recommended for all studies)"
    )
    show_completion_percentage: bool = Field(
        default=False,
        description="Show percentage complete (e.g., '47%'). Can be stressful."
    )
    show_forms_remaining: bool = Field(
        default=False,
        description="Show count of remaining forms today (e.g., '2 forms left')"
    )
    show_overall_progress: bool = Field(
        default=False,
        description="Show overall study progress (e.g., 'Day 15 of 90')"
    )
    
    # === STUDY METADATA (Usually hide from participants) ===
    show_study_duration: bool = Field(
        default=False,
        description="Show total study duration (can feel overwhelming)"
    )
    show_phase_name: bool = Field(
        default=False,
        description="Show current phase name (e.g., 'Intervention Phase 2')"
    )
    show_day_type: bool = Field(
        default=False,
        description="Show day type (e.g., 'abc_day_intervention'). Technical."
    )
    show_cycle_info: bool = Field(
        default=False,
        description="Show cycle position (e.g., 'Day 7 of 21-day cycle')"
    )
    
    # === NAVIGATION & GUIDANCE ===
    show_next_form_preview: bool = Field(
        default=True,
        description="Show name of next form before starting (helpful context)"
    )
    show_completion_message: bool = Field(
        default=True,
        description="Show success message when all forms complete (motivating!)"
    )
    show_skip_option: bool = Field(
        default=False,
        description="Allow participants to skip optional forms"
    )
    
    # === TIMELINE & SCHEDULE ===
    show_upcoming_forms: bool = Field(
        default=False,
        description="Show calendar of upcoming forms (useful for planning)"
    )
    show_missed_forms: bool = Field(
        default=True,
        description="Highlight missed/overdue forms (important for compliance)"
    )
    show_future_schedule: bool = Field(
        default=False,
        description="Show future scheduled forms (can be overwhelming)"
    )
    
    def get_display_summary(self) -> str:
        """Get human-readable summary of what participant will see."""
        enabled = []
        if self.show_progress_bar:
            enabled.append("progress bar")
        if self.show_completion_percentage:
            enabled.append("completion %")
        if self.show_phase_name:
            enabled.append("phase name")
        if self.show_next_form_preview:
            enabled.append("next form")
        
        if not enabled:
            return "Minimal UI (no optional elements)"
        return f"Showing: {', '.join(enabled)}"


class StudyFeatures(BaseModel):
    """
    Core study features that can be enabled/disabled.
    
    These control functional capabilities, not just display.
    """
    
    # === FORM FEATURES ===
    enable_skip_logic: bool = Field(
        default=True,
        description="Enable conditional questions within forms (if Q1=Yes, show Q2-Q5)"
    )
    enable_form_validation: bool = Field(
        default=True,
        description="Enable field validation (required fields, min/max, patterns)"
    )
    enable_help_text: bool = Field(
        default=True,
        description="Show help text and tooltips for questions"
    )
    
    # === STUDY WORKFLOW ===
    require_informed_consent: bool = Field(
        default=True,
        description="Require consent form before participation (ethical requirement)"
    )
    enable_eligibility_check: bool = Field(
        default=False,
        description="Run automated eligibility screening (future feature)"
    )
    enable_re_consent: bool = Field(
        default=False,
        description="Require periodic consent renewal (future feature)"
    )
    
    # === ADVANCED FEATURES (Day 3 Extensions) ===
    enable_progress_tracking: bool = Field(
        default=True,
        description="Track and display detailed progress (Day 3 extension)"
    )
    enable_form_skipping: bool = Field(
        default=False,
        description="Allow skipping forms with reason tracking"
    )
    
    def get_enabled_features(self) -> list[str]:
        """Get list of enabled feature names."""
        features = []
        if self.enable_skip_logic:
            features.append("Skip Logic")
        if self.enable_form_validation:
            features.append("Validation")
        if self.require_informed_consent:
            features.append("Informed Consent")
        if self.enable_progress_tracking:
            features.append("Progress Tracking")
        if self.enable_form_skipping:
            features.append("Form Skipping")
        return features


class StudyConfiguration(BaseModel):
    """
    Complete study configuration.
    
    Combines UI settings and feature flags to create a tailored
    experience for each study type.
    """
    
    # === CORE STUDY INFO ===
    study_id: str = Field(description="Unique study identifier")
    study_name: str = Field(description="Human-readable study name")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When this configuration was created"
    )
    
    # === CONFIGURATION SECTIONS ===
    participant_ui: ParticipantUIConfig = Field(
        default_factory=ParticipantUIConfig,
        description="Controls what participants see"
    )
    features: StudyFeatures = Field(
        default_factory=StudyFeatures,
        description="Feature enablement flags"
    )
    
    # === PRESET FACTORY METHODS ===
    
    @classmethod
    def simple_survey(cls, study_id: str, study_name: str) -> "StudyConfiguration":
        """
        Preset: Simple survey with minimal UI.
        
        Use for: Short surveys, questionnaires, one-time assessments
        
        Philosophy: Keep it simple! Participants just want to answer questions
        and be done. Don't overwhelm with metadata.
        """
        return cls(
            study_id=study_id,
            study_name=study_name,
            participant_ui=ParticipantUIConfig(
                show_progress_bar=True,           # ✅ Helpful
                show_completion_percentage=False,  # ❌ Unnecessary pressure
                show_forms_remaining=False,        # ❌ Just one form usually
                show_study_duration=False,         # ❌ Irrelevant for surveys
                show_phase_name=False,             # ❌ No phases
                show_next_form_preview=True,       # ✅ Good context
                show_completion_message=True,      # ✅ Positive reinforcement
                show_skip_option=False,            # ❌ Complete all questions
                show_upcoming_forms=False,         # ❌ No schedule
                show_missed_forms=False            # ❌ One-time survey
            ),
            features=StudyFeatures(
                enable_skip_logic=True,            # ✅ Common in surveys
                enable_form_validation=True,       # ✅ Data quality
                enable_help_text=True,             # ✅ Clarity
                require_informed_consent=True,     # ✅ Ethical requirement
                enable_eligibility_check=False,    # ❌ Usually open enrollment
                enable_progress_tracking=False,    # ❌ Overkill for simple survey
                enable_form_skipping=False         # ❌ Complete everything
            )
        )
    
    @classmethod
    def clinical_trial(cls, study_id: str, study_name: str) -> "StudyConfiguration":
        """
        Preset: Clinical trial with full features.
        
        Use for: Longitudinal studies, complex protocols, multi-phase trials
        
        Philosophy: Participants need more context and guidance for long-term
        commitment. Show helpful metadata and progress tracking.
        """
        return cls(
            study_id=study_id,
            study_name=study_name,
            participant_ui=ParticipantUIConfig(
                show_progress_bar=True,           # ✅ Essential
                show_completion_percentage=True,  # ✅ Motivating
                show_forms_remaining=True,        # ✅ Helpful planning
                show_study_duration=True,         # ✅ Context matters
                show_phase_name=True,             # ✅ Where am I in the study?
                show_next_form_preview=True,      # ✅ What's coming
                show_completion_message=True,     # ✅ Celebrate milestones
                show_skip_option=False,           # ❌ Compliance critical
                show_upcoming_forms=True,         # ✅ Calendar helpful
                show_missed_forms=True            # ✅ Catch up reminders
            ),
            features=StudyFeatures(
                enable_skip_logic=True,           # ✅ Complex forms need this
                enable_form_validation=True,      # ✅ Data quality critical
                enable_help_text=True,            # ✅ Complex questions
                require_informed_consent=True,    # ✅ Regulatory requirement
                enable_eligibility_check=True,    # ✅ Strict inclusion criteria
                enable_progress_tracking=True,    # ✅ Long-term engagement
                enable_form_skipping=False        # ❌ Protocol compliance
            )
        )
    
    @classmethod
    def minimal(cls, study_id: str, study_name: str) -> "StudyConfiguration":
        """
        Preset: Absolute minimum UI.
        
        Use for: Very short assessments, single-question forms
        
        Philosophy: Get out of the participant's way. Show nothing extra.
        """
        return cls(
            study_id=study_id,
            study_name=study_name,
            participant_ui=ParticipantUIConfig(
                show_progress_bar=False,
                show_completion_percentage=False,
                show_forms_remaining=False,
                show_study_duration=False,
                show_phase_name=False,
                show_next_form_preview=False,
                show_completion_message=True,     # ✅ At least say thanks!
                show_skip_option=False,
                show_upcoming_forms=False,
                show_missed_forms=False
            ),
            features=StudyFeatures(
                enable_skip_logic=False,
                enable_form_validation=True,      # ✅ Always validate
                enable_help_text=False,
                require_informed_consent=True,    # ✅ Always get consent
                enable_progress_tracking=False,
                enable_form_skipping=False
            )
        )
    
    # === UTILITY METHODS ===
    
    def get_participant_view_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data for participant view based on configuration.
        
        Only includes fields that are enabled in the configuration.
        This is what the frontend will render.
        
        Args:
            context: Full study context (all available data)
            
        Returns:
            Filtered context containing only enabled fields
        """
        view = {}
        
        # Progress indicators
        if self.participant_ui.show_progress_bar:
            view['progress_bar'] = context.get('progress_bar')
        
        if self.participant_ui.show_completion_percentage:
            view['completion_pct'] = context.get('completion_pct')
        
        if self.participant_ui.show_forms_remaining:
            view['forms_remaining'] = context.get('forms_remaining')
        
        if self.participant_ui.show_overall_progress:
            view['current_day'] = context.get('current_day')
            view['total_days'] = context.get('total_days')
        
        # Study metadata
        if self.participant_ui.show_study_duration:
            view['study_duration'] = context.get('study_duration')
        
        if self.participant_ui.show_phase_name:
            view['phase_name'] = context.get('phase_name')
        
        if self.participant_ui.show_day_type:
            view['day_type'] = context.get('day_type')
        
        if self.participant_ui.show_cycle_info:
            view['cycle_day'] = context.get('cycle_day')
            view['cycle_length'] = context.get('cycle_length')
        
        # Navigation
        if self.participant_ui.show_next_form_preview:
            view['next_form'] = context.get('next_form')
        
        if self.participant_ui.show_upcoming_forms:
            view['upcoming_forms'] = context.get('upcoming_forms')
        
        if self.participant_ui.show_missed_forms:
            view['missed_forms'] = context.get('missed_forms')
        
        return view
    
    def summary(self) -> str:
        """Get human-readable summary of configuration."""
        ui_summary = self.participant_ui.get_display_summary()
        features = self.features.get_enabled_features()
        
        return (
            f"Study: {self.study_name}\n"
            f"UI: {ui_summary}\n"
            f"Features: {', '.join(features) if features else 'None'}"
        )


# === VALIDATION LOGIC ===

def validate_configuration(config: StudyConfiguration) -> tuple[bool, list[str]]:
    """
    Validate configuration for logical consistency.
    
    Catches common mistakes like enabling dependent features without
    their prerequisites.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Rule 1: Can't show completion % without progress bar
    if config.participant_ui.show_completion_percentage and \
       not config.participant_ui.show_progress_bar:
        errors.append(
            "Cannot show completion_percentage without progress_bar. "
            "Enable show_progress_bar or disable show_completion_percentage."
        )
    
    # Rule 2: Can't show upcoming forms without next form preview
    if config.participant_ui.show_upcoming_forms and \
       not config.participant_ui.show_next_form_preview:
        errors.append(
            "Cannot show upcoming_forms without next_form_preview. "
            "Enable show_next_form_preview or disable show_upcoming_forms."
        )
    
    # Rule 3: Form skipping requires UI option
    if config.features.enable_form_skipping and \
       not config.participant_ui.show_skip_option:
        errors.append(
            "Cannot enable form_skipping without show_skip_option in UI. "
            "Enable show_skip_option or disable enable_form_skipping."
        )
    
    # Rule 4: Eligibility check should have informed consent
    if config.features.enable_eligibility_check and \
       not config.features.require_informed_consent:
        errors.append(
            "Cannot enable eligibility_check without informed_consent. "
            "Enable require_informed_consent or disable enable_eligibility_check."
        )
    
    # Rule 5: Cycle info requires phase name (they go together)
    if config.participant_ui.show_cycle_info and \
       not config.participant_ui.show_phase_name:
        errors.append(
            "Cannot show cycle_info without phase_name. "
            "Cycle info is meaningless without phase context."
        )
    
    return (len(errors) == 0, errors)


# === EXAMPLE USAGE (for testing) ===

if __name__ == "__main__":
    print("=" * 60)
    print("STUDY CONFIGURATION MODULE - EXAMPLES")
    print("=" * 60)
    
    # Example 1: Simple survey
    print("\n1. SIMPLE SURVEY PRESET")
    print("-" * 60)
    simple = StudyConfiguration.simple_survey(
        study_id="SURVEY_001",
        study_name="User Experience Survey"
    )
    print(simple.summary())
    print(f"\nValidation: ", end="")
    is_valid, errors = validate_configuration(simple)
    print("✅ PASS" if is_valid else f"❌ FAIL: {errors}")
    
    # Example 2: Clinical trial
    print("\n2. CLINICAL TRIAL PRESET")
    print("-" * 60)
    trial = StudyConfiguration.clinical_trial(
        study_id="TRIAL_001",
        study_name="Phase 3 Drug Trial"
    )
    print(trial.summary())
    print(f"\nValidation: ", end="")
    is_valid, errors = validate_configuration(trial)
    print("✅ PASS" if is_valid else f"❌ FAIL: {errors}")
    
    # Example 3: Minimal
    print("\n3. MINIMAL PRESET")
    print("-" * 60)
    minimal = StudyConfiguration.minimal(
        study_id="MIN_001",
        study_name="Quick Assessment"
    )
    print(minimal.summary())
    
    # Example 4: Custom (with validation error)
    print("\n4. CUSTOM CONFIG (INVALID - shows validation)")
    print("-" * 60)
    invalid = StudyConfiguration(
        study_id="CUSTOM_001",
        study_name="Invalid Config Example",
        participant_ui=ParticipantUIConfig(
            show_progress_bar=False,
            show_completion_percentage=True  # ❌ Invalid without progress bar!
        )
    )
    is_valid, errors = validate_configuration(invalid)
    print(f"Validation: ❌ FAIL")
    for error in errors:
        print(f"  - {error}")
    
    # Example 5: Participant view filtering
    print("\n5. PARTICIPANT VIEW FILTERING")
    print("-" * 60)
    config = StudyConfiguration.simple_survey("TEST", "Test Study")
    
    # Full context (everything available)
    full_context = {
        'progress_bar': 50,
        'completion_pct': 50,
        'forms_remaining': 2,
        'phase_name': 'Intervention',
        'day_type': 'ab_day_intervention',
        'next_form': 'Daily Diary',
        'current_day': 15,
        'total_days': 90
    }
    
    # Get filtered view
    participant_view = config.get_participant_view_data(full_context)
    
    print("Full context has:", list(full_context.keys()))
    print("Participant sees:", list(participant_view.keys()))
    print("\nFiltered out:", 
          set(full_context.keys()) - set(participant_view.keys()))
    
    print("\n" + "=" * 60)
    print("✅ Module working correctly!")
    print("=" * 60)