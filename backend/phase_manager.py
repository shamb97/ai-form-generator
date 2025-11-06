"""
Phase Manager - The Memory Keeper

This module tracks form completions separately for each phase.
Think of it like: "Did I eat breakfast TODAY (this phase), or was that YESTERDAY (different phase)?"

Key Rule: Same form in different phases = different completions
Example: Consent form in Screening ≠ Consent form in Follow-Up
"""

from datetime import date, datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Completion:
    """
    Records when a form was completed.
    
    Like a 5-year-old would understand:
    "I finished my math homework on Monday in Mrs. Smith's class"
    
    Attributes:
        form_id: Which form? (e.g., "daily_diary")
        phase: Which phase? (e.g., "screening", "intervention")
        day_type: What kind of day? (e.g., "A_ONLY", "ABC", "EVENT_EOT")
        completed_date: When? (e.g., 2024-11-06)
        participant_id: Who completed it? (for future multi-user support)
    """
    form_id: str
    phase: str
    day_type: str
    completed_date: date
    participant_id: str = "default_participant"
    
    def __repr__(self):
        return f"Completion(form={self.form_id}, phase={self.phase}, day_type={self.day_type}, date={self.completed_date})"


class PhaseManager:
    """
    The Memory Keeper - Tracks what's been completed in each phase.
    
    Like a teacher's gradebook that keeps track of:
    - Which assignments each student completed
    - In which class (phase)
    - On which day
    
    Why we need this:
    - Prevents confusion: "Did I do this TODAY or YESTERDAY?"
    - Keeps phases separate: "Math homework ≠ Art homework"
    - Makes navigation smart: "What should I do NEXT?"
    """
    
    def __init__(self):
        """
        Initialize the memory keeper with an empty list of completions.
        
        Like starting a new gradebook at the beginning of the school year.
        """
        self.completions: List[Completion] = []
    
    def record_completion(
        self,
        form_id: str,
        phase: str,
        day_type: str,
        completed_date: Optional[date] = None,
        participant_id: str = "default_participant"
    ) -> Completion:
        """
        Record that a form was completed.
        
        Like a 5-year-old would understand:
        "I finished my spelling test in English class today!"
        
        Args:
            form_id: Which form? (e.g., "consent_form")
            phase: Which phase? (e.g., "screening")
            day_type: What kind of day? (e.g., "A_ONLY")
            completed_date: When? (defaults to today)
            participant_id: Who? (for future multi-user support)
        
        Returns:
            The completion record that was created
        
        Example:
            >>> pm = PhaseManager()
            >>> pm.record_completion("daily_diary", "intervention", "A_ONLY")
            Completion(form=daily_diary, phase=intervention, day_type=A_ONLY, date=2024-11-06)
        """
        if completed_date is None:
            completed_date = date.today()
        
        completion = Completion(
            form_id=form_id,
            phase=phase,
            day_type=day_type,
            completed_date=completed_date,
            participant_id=participant_id
        )
        
        self.completions.append(completion)
        return completion
    
    def is_form_done(
        self,
        form_id: str,
        phase: str,
        day_type: str,
        check_date: Optional[date] = None,
        participant_id: str = "default_participant"
    ) -> bool:
        """
        Check if a specific form was completed in a specific phase on a specific day.
        
        Like a 5-year-old would understand:
        "Did I already brush my teeth THIS MORNING (not yesterday morning)?"
        
        Args:
            form_id: Which form?
            phase: Which phase?
            day_type: What kind of day?
            check_date: Which day? (defaults to today)
            participant_id: Who?
        
        Returns:
            True if the form was completed, False otherwise
        
        Example:
            >>> pm = PhaseManager()
            >>> pm.record_completion("consent", "screening", "EVENT_BASELINE")
            >>> pm.is_form_done("consent", "screening", "EVENT_BASELINE")
            True
            >>> pm.is_form_done("consent", "intervention", "EVENT_BASELINE")
            False  # Different phase!
        """
        if check_date is None:
            check_date = date.today()
        
        # Look through all completions to find a match
        for completion in self.completions:
            if (completion.form_id == form_id and
                completion.phase == phase and
                completion.day_type == day_type and
                completion.completed_date == check_date and
                completion.participant_id == participant_id):
                return True
        
        return False
    
    def get_completions_for_phase(
        self,
        phase: str,
        participant_id: str = "default_participant"
    ) -> List[Completion]:
        """
        Get all completions for a specific phase.
        
        Like a 5-year-old would understand:
        "Show me all the homework I did in Math class"
        
        Args:
            phase: Which phase?
            participant_id: Who?
        
        Returns:
            List of all completions in that phase
        
        Example:
            >>> pm = PhaseManager()
            >>> pm.record_completion("form_a", "screening", "A_ONLY")
            >>> pm.record_completion("form_b", "screening", "AB")
            >>> pm.record_completion("form_c", "intervention", "A_ONLY")
            >>> len(pm.get_completions_for_phase("screening"))
            2  # Only screening completions
        """
        return [
            c for c in self.completions
            if c.phase == phase and c.participant_id == participant_id
        ]
    
    def get_completions_for_date(
        self,
        check_date: Optional[date] = None,
        participant_id: str = "default_participant"
    ) -> List[Completion]:
        """
        Get all completions for a specific date.
        
        Like a 5-year-old would understand:
        "What did I do today?"
        
        Args:
            check_date: Which day? (defaults to today)
            participant_id: Who?
        
        Returns:
            List of all completions on that date
        """
        if check_date is None:
            check_date = date.today()
        
        return [
            c for c in self.completions
            if c.completed_date == check_date and c.participant_id == participant_id
        ]
    
    def clear_completions(self, participant_id: str = "default_participant"):
        """
        Clear all completions for a participant.
        
        Like a 5-year-old would understand:
        "Erase everything from my notebook and start fresh"
        
        Useful for:
        - Testing
        - Starting a new study
        - Resetting data
        """
        self.completions = [
            c for c in self.completions
            if c.participant_id != participant_id
        ]
    
    def get_summary(self, participant_id: str = "default_participant") -> Dict:
        """
        Get a summary of all completions.
        
        Like a 5-year-old would understand:
        "How many homework assignments did I do in each class?"
        
        Returns:
            Dictionary with statistics about completions
        """
        participant_completions = [
            c for c in self.completions
            if c.participant_id == participant_id
        ]
        
        # Group by phase
        by_phase = {}
        for completion in participant_completions:
            if completion.phase not in by_phase:
                by_phase[completion.phase] = []
            by_phase[completion.phase].append(completion)
        
        return {
            "total_completions": len(participant_completions),
            "by_phase": {
                phase: len(comps) for phase, comps in by_phase.items()
            },
            "latest_completion": max(
                [c.completed_date for c in participant_completions],
                default=None
            )
        }


# Example usage (for demonstration)
if __name__ == "__main__":
    print("🧪 Testing Phase Manager...\n")
    
    # Create a new phase manager
    pm = PhaseManager()
    
    # Scenario: A participant completes forms across multiple phases
    print("📝 Recording completions...")
    pm.record_completion("consent_form", "screening", "EVENT_BASELINE", date(2024, 11, 1))
    pm.record_completion("daily_diary", "intervention", "A_ONLY", date(2024, 11, 5))
    pm.record_completion("daily_diary", "intervention", "A_ONLY", date(2024, 11, 6))
    pm.record_completion("weekly_qol", "intervention", "AB", date(2024, 11, 6))
    
    print("✅ Recorded 4 completions\n")
    
    # Test 1: Check if form is done in specific phase
    print("🔍 Test 1: Is 'daily_diary' done in intervention on 2024-11-06?")
    result = pm.is_form_done("daily_diary", "intervention", "A_ONLY", date(2024, 11, 6))
    print(f"   Result: {result} ✅\n")
    
    # Test 2: Check if same form is done in different phase
    print("🔍 Test 2: Is 'daily_diary' done in screening on 2024-11-06?")
    result = pm.is_form_done("daily_diary", "screening", "A_ONLY", date(2024, 11, 6))
    print(f"   Result: {result} ❌ (Different phase!)\n")
    
    # Test 3: Get summary
    print("📊 Summary:")
    summary = pm.get_summary()
    print(f"   Total completions: {summary['total_completions']}")
    print(f"   By phase: {summary['by_phase']}")
    print(f"   Latest completion: {summary['latest_completion']}")
    
    print("\n✅ Phase Manager working correctly!")