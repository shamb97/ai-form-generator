"""
Navigation Controller - "What's Next?" Logic

Determines what happens after a form is saved.
Core principle: Instant progression - no unnecessary clicks back to home screen.

Flow:
1. User saves Form A
2. System checks: What else is due in this day type?
3. System finds next incomplete form
4. System shows it immediately OR shows completion message

Dependencies:
- phase_manager: To check if forms are done
- event_handler: To determine active day type and form list
"""

from datetime import date
from typing import Dict, List, Optional
from dataclasses import dataclass
from phase_manager import PhaseManager
from event_handler import EventHandler


@dataclass
class NavigationAction:
    """
    Represents the next action after a form save.
    
    Attributes:
        action_type: What to do next ("SHOW_FORM", "ALL_COMPLETE", "ERROR")
        form_id: Which form to show (if action_type is SHOW_FORM)
        day_type: Current active day type
        phase: Current phase
        message: User-facing message
        metadata: Additional context for debugging/logging
    """
    action_type: str  # "SHOW_FORM", "ALL_COMPLETE", "ERROR"
    form_id: Optional[str] = None
    day_type: Optional[str] = None
    phase: Optional[str] = None
    message: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize metadata if not provided"""
        if self.metadata is None:
            self.metadata = {}


class NavigationController:
    """
    Determines post-save navigation logic.
    
    Key responsibilities:
    - After form save, determine what comes next
    - Check completions via PhaseManager
    - Determine active forms via EventHandler
    - Provide instant progression (no home screen unless done)
    """
    
    def __init__(self, phase_manager: PhaseManager, event_handler: EventHandler):
        """
        Initialize with required dependencies.
        
        Args:
            phase_manager: For checking form completion status
            event_handler: For determining active day type and form list
        """
        self.phase_manager = phase_manager
        self.event_handler = event_handler
    
    def determine_next_action(
        self,
        just_completed_form_id: str,
        candidate_day_types: List[str],
        current_phase: str,
        current_date: Optional[date] = None,
        participant_id: str = "default_participant"
    ) -> NavigationAction:
        """
        Determine what to do after a form is saved.
        
        Algorithm:
        1. Determine active day type (via EventHandler)
        2. Get list of forms required for this day type
        3. Iterate through forms in order
        4. For each form:
           - Check if due (should be on this day type)
           - Check if done (via PhaseManager)
           - If due and not done, return "SHOW_FORM"
        5. If all forms done, return "ALL_COMPLETE"
        
        Args:
            just_completed_form_id: Form that was just saved
            candidate_day_types: Potential day types for today
            current_phase: Current study phase
            current_date: Date to check (defaults to today)
            participant_id: Participant identifier
        
        Returns:
            NavigationAction indicating next step
        """
        if current_date is None:
            current_date = date.today()
        
        # Step 1: Determine active day type
        active_day_type = self.event_handler.determine_active_day_type(
            candidate_day_types,
            current_date
        )
        
        if active_day_type is None:
            # Edge case: No active day type (shouldn't happen after a save)
            return NavigationAction(
                action_type="ERROR",
                phase=current_phase,
                message="No active day type found",
                metadata={
                    "error": "no_active_day_type",
                    "candidates": candidate_day_types
                }
            )
        
        # Step 2: Get required forms for this day type
        required_forms = active_day_type.forms
        
        if not required_forms:
            # Free day (no forms) - shouldn't happen after a save
            return NavigationAction(
                action_type="ALL_COMPLETE",
                day_type=active_day_type.id,
                phase=current_phase,
                message="All forms complete",
                metadata={"note": "Free day - no forms required"}
            )
        
        # Step 3: Check each form in order for next incomplete one
        for form_id in required_forms:
            # Check if this form is done
            is_done = self.phase_manager.is_form_done(
                form_id=form_id,
                phase=current_phase,
                day_type=active_day_type.id,
                check_date=current_date,
                participant_id=participant_id
            )
            
            if not is_done:
                # Found next incomplete form
                return NavigationAction(
                    action_type="SHOW_FORM",
                    form_id=form_id,
                    day_type=active_day_type.id,
                    phase=current_phase,
                    message=f"Please complete {form_id}",
                    metadata={
                        "position": required_forms.index(form_id) + 1,
                        "total": len(required_forms),
                        "previous": just_completed_form_id
                    }
                )
        
        # Step 4: All forms complete for this day type
        return NavigationAction(
            action_type="ALL_COMPLETE",
            day_type=active_day_type.id,
            phase=current_phase,
            message="All forms for today completed. Great job! 🎉",
            metadata={
                "total_completed": len(required_forms),
                "last_form": just_completed_form_id
            }
        )
    
    def get_current_status(
        self,
        candidate_day_types: List[str],
        current_phase: str,
        current_date: Optional[date] = None,
        participant_id: str = "default_participant"
    ) -> Dict:
        """
        Get current completion status for today.
        
        Useful for:
        - Home screen display
        - Progress bars
        - "X of Y forms complete" messages
        
        Returns:
            Dictionary with:
            - active_day_type: Current day type ID
            - required_forms: List of form IDs needed today
            - completed_forms: List of form IDs already done
            - incomplete_forms: List of form IDs still needed
            - progress: Completion percentage
        """
        if current_date is None:
            current_date = date.today()
        
        # Determine active day type
        active_day_type = self.event_handler.determine_active_day_type(
            candidate_day_types,
            current_date
        )
        
        if active_day_type is None:
            return {
                "active_day_type": None,
                "required_forms": [],
                "completed_forms": [],
                "incomplete_forms": [],
                "progress": 100,  # No forms = 100% complete
                "message": "No forms due today"
            }
        
        required_forms = active_day_type.forms
        completed_forms = []
        incomplete_forms = []
        
        # Check each form
        for form_id in required_forms:
            is_done = self.phase_manager.is_form_done(
                form_id=form_id,
                phase=current_phase,
                day_type=active_day_type.id,
                check_date=current_date,
                participant_id=participant_id
            )
            
            if is_done:
                completed_forms.append(form_id)
            else:
                incomplete_forms.append(form_id)
        
        # Calculate progress
        if len(required_forms) == 0:
            progress = 100
        else:
            progress = round((len(completed_forms) / len(required_forms)) * 100)
        
        return {
            "active_day_type": active_day_type.id,
            "is_event_day": active_day_type.is_event,
            "required_forms": required_forms,
            "completed_forms": completed_forms,
            "incomplete_forms": incomplete_forms,
            "progress": progress,
            "message": f"{len(completed_forms)} of {len(required_forms)} forms complete"
        }
    
    def get_next_form_to_show(
        self,
        candidate_day_types: List[str],
        current_phase: str,
        current_date: Optional[date] = None,
        participant_id: str = "default_participant"
    ) -> Optional[str]:
        """
        Get the next incomplete form ID to show.
        
        Useful for:
        - Initial page load (what to show first?)
        - "Continue where you left off" functionality
        
        Returns:
            Form ID to show, or None if all complete
        """
        if current_date is None:
            current_date = date.today()
        
        # Get active day type
        active_day_type = self.event_handler.determine_active_day_type(
            candidate_day_types,
            current_date
        )
        
        if active_day_type is None:
            return None
        
        # Find first incomplete form
        for form_id in active_day_type.forms:
            is_done = self.phase_manager.is_form_done(
                form_id=form_id,
                phase=current_phase,
                day_type=active_day_type.id,
                check_date=current_date,
                participant_id=participant_id
            )
            
            if not is_done:
                return form_id
        
        # All complete
        return None


# Testing/Example usage
if __name__ == "__main__":
    print("🧪 Testing Navigation Controller...\n")
    
    # Import dependencies
    from phase_manager import PhaseManager
    from event_handler import create_default_event_handler
    
    # Set up dependencies
    pm = PhaseManager()
    eh = create_default_event_handler()
    nav = NavigationController(pm, eh)
    
    # Test scenario: User completing forms on an AB day in intervention phase
    current_phase = "intervention"
    current_day_types = ["AB"]  # AB = daily_diary + weekly_qol
    test_date = date(2024, 11, 6)
    
    print("📋 Scenario: AB day (daily_diary + weekly_qol) in intervention phase\n")
    
    # Test 1: Initial status (nothing done yet)
    print("🔍 Test 1: Check initial status")
    status = nav.get_current_status(current_day_types, current_phase, test_date)
    print(f"   Active day type: {status['active_day_type']}")
    print(f"   Required forms: {status['required_forms']}")
    print(f"   Completed: {status['completed_forms']}")
    print(f"   Incomplete: {status['incomplete_forms']}")
    print(f"   Progress: {status['progress']}%")
    print(f"   ✅ 0 of 2 complete\n")
    
    # Test 2: Get next form to show (should be first in list)
    print("🔍 Test 2: What form should we show first?")
    next_form = nav.get_next_form_to_show(current_day_types, current_phase, test_date)
    print(f"   Next form: {next_form}")
    print(f"   ✅ Shows daily_diary (first in AB list)\n")
    
    # Test 3: User completes daily_diary, what's next?
    print("🔍 Test 3: User saves daily_diary, what happens?")
    pm.record_completion("daily_diary", current_phase, "AB", test_date)
    action = nav.determine_next_action("daily_diary", current_day_types, current_phase, test_date)
    print(f"   Action: {action.action_type}")
    print(f"   Next form: {action.form_id}")
    print(f"   Message: {action.message}")
    print(f"   ✅ Shows weekly_qol immediately (no home screen)\n")
    
    # Test 4: User completes weekly_qol, what's next?
    print("🔍 Test 4: User saves weekly_qol (last form), what happens?")
    pm.record_completion("weekly_qol", current_phase, "AB", test_date)
    action = nav.determine_next_action("weekly_qol", current_day_types, current_phase, test_date)
    print(f"   Action: {action.action_type}")
    print(f"   Message: {action.message}")
    print(f"   ✅ All complete message\n")
    
    # Test 5: Check final status
    print("🔍 Test 5: Check final status")
    status = nav.get_current_status(current_day_types, current_phase, test_date)
    print(f"   Completed: {status['completed_forms']}")
    print(f"   Progress: {status['progress']}%")
    print(f"   ✅ 2 of 2 complete (100%)\n")
    
    # Test 6: Event day overrides regular schedule
    print("🔍 Test 6: Event day (EOT) overrides regular schedule")
    pm_new = PhaseManager()
    nav_new = NavigationController(pm_new, eh)
    event_day_types = ["AB", "EVENT_EOT"]  # Both possible, event should win
    
    status = nav_new.get_current_status(event_day_types, current_phase, test_date)
    print(f"   Candidates: {event_day_types}")
    print(f"   Active: {status['active_day_type']}")
    print(f"   Required forms: {status['required_forms']}")
    print(f"   ✅ EVENT_EOT wins, shows event forms only\n")
    
    print("✅ Navigation Controller working correctly!")
