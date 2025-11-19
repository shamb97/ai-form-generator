"""
Metadata Edge Case Validator
=============================

Handles tricky edge cases in metadata collection:
1. Phase detection (is "Awakening Phase" one phase or many?)
2. Midnight crossover (started 11:55pm, finished 12:10am - which day?)
3. Timezone travel (enrolled in London, submitting from New York)

This validator ensures metadata suggestions are intelligent and accurate.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re


class MetadataEdgeCaseHandler:
    """
    Handles edge cases in metadata collection and validation
    
    Ensures intelligent metadata suggestions that handle real-world complexity
    """
    
    def __init__(self):
        """Initialize the edge case handler"""
        self.phase_keywords = [
            'baseline', 'screening', 'treatment', 'intervention', 
            'follow-up', 'followup', 'washout', 'maintenance',
            'phase', 'period', 'stage'
        ]
    
    def validate_and_enhance_metadata(self, 
                                      study_classification: Dict[str, Any],
                                      description: str) -> Dict[str, Any]:
        """
        Main entry point: validate and enhance metadata suggestions
        
        Args:
            study_classification: The AI's initial classification
            description: Original user description
            
        Returns:
            Enhanced classification with edge case handling
        """
        print("🔍 Validating metadata suggestions...")
        
        # Check phase detection
        phase_validation = self.validate_phase_suggestion(
            study_classification, 
            description
        )
        
        # Update classification based on validation
        if phase_validation['action'] == 'ask_user':
            study_classification['needs_clarification'] = True
            study_classification['clarification_question'] = phase_validation['question']
            study_classification['clarification_options'] = phase_validation['options']
        elif phase_validation['action'] == 'disable_phase_tracking':
            study_classification['has_phases'] = False
            study_classification['phase_names'] = []
        
        print(f"✅ Validation complete: {phase_validation['action']}")
        return study_classification
    
    def validate_phase_suggestion(self, 
                                   study_classification: Dict[str, Any],
                                   description: str) -> Dict[str, Any]:
        """
        Ensure phase metadata makes logical sense
        
        Handles the tricky case: Is "Awakening Phase" a label or Phase 1 of many?
        
        Args:
            study_classification: AI's classification
            description: User's description
            
        Returns:
            Validation result with action to take
        """
        has_phases = study_classification.get('has_phases', False)
        phase_names = study_classification.get('phase_names', [])
        
        # Count how many phases detected
        phase_count = len(phase_names) if phase_names else 0
        
        print(f"   📊 Detected {phase_count} phases: {phase_names}")
        
        # Case 1: No phases detected
        if phase_count == 0:
            return {
                "action": "disable_phase_tracking",
                "reason": "No phases detected in description",
                "suggest_metadata": False
            }
        
        # Case 2: Exactly ONE phase name detected
        # This is ambiguous! Could be:
        # - Option A: A label for the entire study ("My Awakening Phase")
        # - Option B: The first of multiple phases ("Baseline phase")
        elif phase_count == 1:
            phase_name = phase_names[0]
            
            # Check if description suggests it's just a label
            label_indicators = [
                'my', 'personal', 'called', 'named', 'in my', 
                'during my', 'throughout'
            ]
            
            description_lower = description.lower()
            seems_like_label = any(
                indicator in description_lower 
                for indicator in label_indicators
            )
            
            # Check if description suggests multiple phases will exist
            multiple_phase_indicators = [
                'then', 'followed by', 'after', 'before',
                'next', 'subsequent', 'later'
            ]
            
            seems_like_multiple = any(
                indicator in description_lower
                for indicator in multiple_phase_indicators
            )
            
            if seems_like_multiple:
                # Likely multiple phases - ask what the other phases are
                return {
                    "action": "ask_user",
                    "reason": f"Single phase '{phase_name}' detected but description suggests more",
                    "question": f"I detected '{phase_name}' as a study phase. Will there be other phases in this study?",
                    "options": {
                        "yes": {
                            "followup": f"What are all the phases? (e.g., '{phase_name}, Follow-up, Completion')",
                            "action": "enable_multi_phase_tracking"
                        },
                        "no": {
                            "followup": f"Got it! I'll use '{phase_name}' as a constant label for the entire study.",
                            "action": "use_as_constant_label"
                        }
                    }
                }
            elif seems_like_label:
                # Probably just a label
                return {
                    "action": "ask_user",
                    "reason": f"Phase name '{phase_name}' seems like a study label",
                    "question": f"I see you mentioned '{phase_name}'. Is this:",
                    "options": {
                        "label": {
                            "description": f"A name for the entire study period",
                            "action": "use_as_constant_label"
                        },
                        "first_phase": {
                            "description": f"The first of multiple phases",
                            "followup": "What are the other phases?",
                            "action": "enable_multi_phase_tracking"
                        }
                    }
                }
            else:
                # Unclear - ask user to clarify
                return {
                    "action": "ask_user",
                    "reason": "Ambiguous single phase detection",
                    "question": f"You mentioned '{phase_name}'. Quick question:",
                    "options": {
                        "only_phase": {
                            "description": f"This is the only phase/period (entire study)",
                            "action": "disable_phase_tracking"
                        },
                        "multiple_phases": {
                            "description": f"There will be multiple phases",
                            "followup": "What are all the phases?",
                            "action": "enable_multi_phase_tracking"
                        }
                    }
                }
        
        # Case 3: Multiple phases detected (2+)
        else:
            # Definitely multiple phases - but ask if there are MORE
            return {
                "action": "ask_user",
                "reason": f"Multiple phases detected: {phase_names}",
                "question": f"I detected these phases: {', '.join(phase_names)}. Are there any other phases I should know about?",
                "options": {
                    "complete": {
                        "description": "That's all the phases",
                        "action": "enable_multi_phase_tracking"
                    },
                    "more_phases": {
                        "description": "There are additional phases",
                        "followup": "What are the complete list of all phases?",
                        "action": "enable_multi_phase_tracking"
                    }
                },
                "suggest_metadata": True
            }
    
    def handle_midnight_crossover(self, 
                                  started_time: datetime, 
                                  submitted_time: datetime) -> Dict[str, Any]:
        """
        Determine which study day when form crosses midnight
        
        Example:
            Started: 2025-11-11 23:55:00 (Day 5)
            Submitted: 2025-11-12 00:10:00 (Day 6?)
            Answer: Day 5 (use start date)
        
        Args:
            started_time: When user started the form
            submitted_time: When user submitted the form
            
        Returns:
            Decision on which day to assign + metadata to capture
        """
        # Check if dates differ
        if started_time.date() != submitted_time.date():
            duration = submitted_time - started_time
            
            return {
                "crossed_midnight": True,
                "study_day_basis": "started_date",
                "study_day_date": started_time.date(),
                "rationale": "Form submission counted for the day it was started",
                "metadata_to_capture": {
                    "form_started_at": started_time.isoformat(),
                    "form_submitted_at": submitted_time.isoformat(),
                    "crossed_midnight": True,
                    "completion_duration_minutes": int(duration.total_seconds() / 60)
                },
                "user_message": f"Started {started_time.strftime('%I:%M %p')}, completed {submitted_time.strftime('%I:%M %p')} next day. Counted for {started_time.strftime('%B %d')}."
            }
        else:
            # Same day - no special handling needed
            return {
                "crossed_midnight": False,
                "study_day_basis": "same_day",
                "study_day_date": started_time.date()
            }
    
    def handle_timezone_travel(self, 
                               enrollment_timezone: str,
                               current_timezone: str,
                               current_time: datetime) -> Dict[str, Any]:
        """
        Handle timezone changes during study (e.g., international travel)
        
        Example:
            Enrolled: London (GMT)
            Submitting from: New York (EST, -5 hours)
            Question: What time is it "really"?
        
        Args:
            enrollment_timezone: Timezone at enrollment (e.g., "Europe/London")
            current_timezone: Current timezone (e.g., "America/New_York")
            current_time: Current local time
            
        Returns:
            Decision on how to calculate study day + metadata
        """
        if enrollment_timezone != current_timezone:
            return {
                "timezone_changed": True,
                "study_day_calculation": "use_enrollment_timezone",
                "rationale": "Study days calculated in enrollment timezone for consistency",
                "metadata_to_capture": {
                    "enrollment_timezone": enrollment_timezone,
                    "submission_timezone": current_timezone,
                    "submission_time_local": current_time.isoformat(),
                    "submission_time_utc": current_time.utcnow().isoformat(),
                    "timezone_offset_hours": "calculated_from_timezones"
                },
                "user_message": f"You're in {current_timezone}, but study days are calculated in {enrollment_timezone} for consistency.",
                "calculation_note": "Convert submission time to enrollment timezone before calculating study day"
            }
        else:
            # Same timezone - no special handling
            return {
                "timezone_changed": False,
                "study_day_calculation": "use_local_time"
            }
    
    def detect_time_sensitive_requirements(self, description: str) -> Dict[str, Any]:
        """
        Detect if study has time-based requirements (e.g., "after 7pm", "morning only")
        
        Args:
            description: User's study description
            
        Returns:
            Time requirements detected
        """
        description_lower = description.lower()
        
        # Time window patterns
        time_patterns = {
            'after_time': r'after (\d+)(pm|am|:)',
            'before_time': r'before (\d+)(pm|am|:)',
            'between_times': r'between (\d+).{0,5}and (\d+)',
            'morning': r'morning|am only',
            'evening': r'evening|night|pm only',
            'daily_time': r'(each|every) (morning|evening|night|day)'
        }
        
        detected_requirements = []
        
        for requirement_type, pattern in time_patterns.items():
            if re.search(pattern, description_lower):
                detected_requirements.append(requirement_type)
        
        if detected_requirements:
            return {
                "has_time_requirements": True,
                "requirements": detected_requirements,
                "suggest_metadata": [
                    "submission_time",
                    "within_compliance_window",
                    "time_window_status"
                ],
                "validation_needed": True
            }
        else:
            return {
                "has_time_requirements": False
            }
    
    def suggest_compliance_metadata(self, 
                                    study_type: str,
                                    has_time_requirements: bool,
                                    has_phases: bool) -> List[Dict[str, str]]:
        """
        Suggest compliance-related metadata based on study characteristics
        
        Args:
            study_type: Type of study
            has_time_requirements: Whether study has time windows
            has_phases: Whether study has multiple phases
            
        Returns:
            List of compliance metadata suggestions
        """
        suggestions = []
        
        # Always suggest for clinical trials
        if study_type == "clinical_trial":
            suggestions.append({
                "field": "protocol_compliance_status",
                "why": "Track adherence to study protocol",
                "how": "Auto-calculated based on submission timing and requirements"
            })
        
        # Time-based compliance
        if has_time_requirements:
            suggestions.append({
                "field": "submission_window_status",
                "why": "Verify submission within required time window",
                "how": "Compare submission time to protocol requirements",
                "example": "On-time / Early / Late"
            })
        
        # Phase-based compliance
        if has_phases:
            suggestions.append({
                "field": "correct_phase_verification",
                "why": "Ensure form submitted in correct study phase",
                "how": "Compare current date to phase schedule"
            })
        
        return suggestions


# Test the validator if run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING METADATA EDGE CASE HANDLER")
    print("="*60)
    
    validator = MetadataEdgeCaseHandler()
    
    # Test 1: Single phase (ambiguous)
    print("\n--- Test 1: Single Phase Detection ---")
    classification1 = {
        "study_type": "personal_tracker",
        "has_phases": True,
        "phase_names": ["Awakening Phase"]
    }
    result1 = validator.validate_phase_suggestion(
        classification1,
        "30-day tracker during my Awakening Phase"
    )
    print(f"Action: {result1['action']}")
    print(f"Question: {result1.get('question', 'N/A')}")
    
    # Test 2: Multiple phases
    print("\n--- Test 2: Multiple Phases ---")
    classification2 = {
        "study_type": "clinical_trial",
        "has_phases": True,
        "phase_names": ["Baseline", "Treatment"]
    }
    result2 = validator.validate_phase_suggestion(
        classification2,
        "Clinical trial with baseline and treatment phases"
    )
    print(f"Action: {result2['action']}")
    print(f"Question: {result2.get('question', 'N/A')}")
    
    # Test 3: Midnight crossover
    print("\n--- Test 3: Midnight Crossover ---")
    started = datetime(2025, 11, 11, 23, 55, 0)
    submitted = datetime(2025, 11, 12, 0, 10, 0)
    result3 = validator.handle_midnight_crossover(started, submitted)
    print(f"Crossed midnight: {result3['crossed_midnight']}")
    print(f"Use date: {result3['study_day_date']}")
    print(f"Message: {result3.get('user_message', 'N/A')}")
    
    # Test 4: Timezone travel
    print("\n--- Test 4: Timezone Travel ---")
    result4 = validator.handle_timezone_travel(
        "Europe/London",
        "America/New_York",
        datetime.now()
    )
    print(f"Timezone changed: {result4['timezone_changed']}")
    print(f"Calculation: {result4['study_day_calculation']}")
    
    # Test 5: Time requirements
    print("\n--- Test 5: Time Requirements Detection ---")
    result5 = validator.detect_time_sensitive_requirements(
        "Daily check-in after 7pm"
    )
    print(f"Has requirements: {result5['has_time_requirements']}")
    print(f"Requirements: {result5.get('requirements', [])}")
    
    print("\n" + "="*60)
    print("✅ VALIDATOR TEST COMPLETE!")
    print("="*60 + "\n")
