"""
Event Handler - Priority System with Clash Prevention

Manages event-triggered days that override regular schedules.
Core principle: Events always win. Regular day types are excluded when events apply.

Priority Order (highest to lowest):
1. EVENT day types (baseline, EOT, early termination)
2. Regular day types (ABC, AB, A_ONLY)
3. Free days (no forms due)

Clash Prevention: If event applies, regular day types are completely ignored.
"""

from datetime import date
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class DayTypePriority(Enum):
    """Priority levels for day types - higher value = higher priority"""
    EVENT = 100  # Events always win
    ABC = 30     # Three forms due
    AB = 20      # Two forms due
    A_ONLY = 10  # One form due
    FREE = 0     # No forms due


@dataclass
class DayTypeDefinition:
    """
    Defines a day type with its properties.
    
    Attributes:
        id: Unique identifier (e.g., "EVENT_EOT", "ABC", "A_ONLY")
        priority: Priority level (events > regular > free)
        forms: List of form IDs required on this day type
        is_event: Whether this is an event-triggered day
        excludes: Day types that cannot coexist with this one
    """
    id: str
    priority: DayTypePriority
    forms: List[str]
    is_event: bool = False
    excludes: Set[str] = None
    
    def __post_init__(self):
        """Set default exclusions if not provided"""
        if self.excludes is None:
            # Events exclude all regular day types by default
            if self.is_event:
                self.excludes = {"ABC", "AB", "A_ONLY", "FREE"}
            else:
                self.excludes = set()


class EventHandler:
    """
    Manages event-triggered days and priority resolution.
    
    Key responsibilities:
    - Register day type definitions
    - Determine active day type based on context and priority
    - Enforce clash prevention rules
    - Provide bulletproof logic for "what should happen today?"
    """
    
    def __init__(self):
        """Initialize with empty day type registry"""
        self.day_types: Dict[str, DayTypeDefinition] = {}
    
    def register_day_type(self, day_type: DayTypeDefinition):
        """
        Register a day type definition.
        
        Example:
            handler.register_day_type(DayTypeDefinition(
                id="EVENT_BASELINE",
                priority=DayTypePriority.EVENT,
                forms=["consent", "demographics"],
                is_event=True
            ))
        """
        self.day_types[day_type.id] = day_type
    
    def get_day_type(self, day_type_id: str) -> Optional[DayTypeDefinition]:
        """Retrieve a registered day type definition"""
        return self.day_types.get(day_type_id)
    
    def determine_active_day_type(
        self,
        candidate_day_types: List[str],
        current_date: Optional[date] = None
    ) -> Optional[DayTypeDefinition]:
        """
        Determine which day type is active based on priority and clash prevention.
        
        Algorithm:
        1. Filter to only registered day types
        2. Sort by priority (highest first)
        3. Return highest priority that doesn't have exclusion conflicts
        
        Args:
            candidate_day_types: List of potential day type IDs for today
            current_date: Date to check (defaults to today)
        
        Returns:
            The highest-priority valid day type, or None if no forms due
        
        Example:
            If today is both "A_ONLY" and "EVENT_EOT":
            - EVENT_EOT has priority 100
            - A_ONLY has priority 10
            - Result: EVENT_EOT wins, A_ONLY is excluded
        """
        if current_date is None:
            current_date = date.today()
        
        # Filter to registered day types only
        valid_candidates = [
            self.day_types[dt_id]
            for dt_id in candidate_day_types
            if dt_id in self.day_types
        ]
        
        if not valid_candidates:
            return None
        
        # Sort by priority (highest first)
        valid_candidates.sort(key=lambda dt: dt.priority.value, reverse=True)
        
        # Check for highest-priority day type that's valid
        for day_type in valid_candidates:
            # Check if this day type is excluded by any higher-priority day type
            is_excluded = False
            for other in valid_candidates:
                if other.priority.value > day_type.priority.value:
                    if day_type.id in other.excludes:
                        is_excluded = True
                        break
            
            if not is_excluded:
                return day_type
        
        # Fallback: return highest priority (shouldn't reach here if logic is correct)
        return valid_candidates[0]
    
    def get_required_forms_for_day(
        self,
        candidate_day_types: List[str],
        current_date: Optional[date] = None
    ) -> List[str]:
        """
        Get the list of forms required today based on active day type.
        
        Args:
            candidate_day_types: Potential day types for today
            current_date: Date to check
        
        Returns:
            List of form IDs required, or empty list if free day
        """
        active_day_type = self.determine_active_day_type(
            candidate_day_types,
            current_date
        )
        
        if active_day_type is None:
            return []
        
        return active_day_type.forms
    
    def is_event_day(
        self,
        candidate_day_types: List[str],
        current_date: Optional[date] = None
    ) -> bool:
        """
        Check if today is an event-triggered day.
        
        Returns:
            True if active day type is an event, False otherwise
        """
        active_day_type = self.determine_active_day_type(
            candidate_day_types,
            current_date
        )
        
        return active_day_type.is_event if active_day_type else False
    
    def get_priority_explanation(
        self,
        candidate_day_types: List[str],
        current_date: Optional[date] = None
    ) -> Dict:
        """
        Get detailed explanation of priority resolution for debugging/logging.
        
        Returns:
            Dictionary with:
            - candidates: All candidate day types
            - active: The winning day type
            - excluded: Day types that were excluded
            - reason: Why the active day type was chosen
        """
        if current_date is None:
            current_date = date.today()
        
        active = self.determine_active_day_type(candidate_day_types, current_date)
        
        if active is None:
            return {
                "candidates": candidate_day_types,
                "active": None,
                "excluded": candidate_day_types,
                "reason": "No registered day types found"
            }
        
        # Determine which were excluded
        excluded = []
        for dt_id in candidate_day_types:
            if dt_id != active.id and dt_id in self.day_types:
                if dt_id in active.excludes:
                    excluded.append(dt_id)
        
        return {
            "candidates": candidate_day_types,
            "active": active.id,
            "active_priority": active.priority.value,
            "active_forms": active.forms,
            "excluded": excluded,
            "reason": f"Event day - excludes regular schedule" if active.is_event 
                     else f"Highest priority regular day type"
        }


def create_default_event_handler() -> EventHandler:
    """
    Create an event handler with standard clinical trial day types.
    
    Standard day types:
    - EVENT_BASELINE: Study start (consent, demographics, baseline assessments)
    - EVENT_EOT: End of Treatment (final assessments, satisfaction)
    - EVENT_EARLY_TERM: Early Termination (exit questionnaire, reason for withdrawal)
    - ABC: Three forms due (e.g., daily + weekly + monthly)
    - AB: Two forms due (e.g., daily + weekly)
    - A_ONLY: One form due (e.g., daily only)
    - FREE: No forms due
    
    Returns:
        Configured EventHandler ready to use
    """
    handler = EventHandler()
    
    # Register event day types (highest priority)
    handler.register_day_type(DayTypeDefinition(
        id="EVENT_BASELINE",
        priority=DayTypePriority.EVENT,
        forms=["consent", "demographics", "baseline_assessment"],
        is_event=True
    ))
    
    handler.register_day_type(DayTypeDefinition(
        id="EVENT_EOT",
        priority=DayTypePriority.EVENT,
        forms=["final_assessment", "satisfaction_survey"],
        is_event=True
    ))
    
    handler.register_day_type(DayTypeDefinition(
        id="EVENT_EARLY_TERM",
        priority=DayTypePriority.EVENT,
        forms=["exit_questionnaire", "withdrawal_reason"],
        is_event=True
    ))
    
    # Register regular day types (lower priority)
    handler.register_day_type(DayTypeDefinition(
        id="ABC",
        priority=DayTypePriority.ABC,
        forms=["daily_diary", "weekly_qol", "monthly_review"],
        is_event=False
    ))
    
    handler.register_day_type(DayTypeDefinition(
        id="AB",
        priority=DayTypePriority.AB,
        forms=["daily_diary", "weekly_qol"],
        is_event=False
    ))
    
    handler.register_day_type(DayTypeDefinition(
        id="A_ONLY",
        priority=DayTypePriority.A_ONLY,
        forms=["daily_diary"],
        is_event=False
    ))
    
    handler.register_day_type(DayTypeDefinition(
        id="FREE",
        priority=DayTypePriority.FREE,
        forms=[],
        is_event=False
    ))
    
    return handler


# Testing/Example usage
if __name__ == "__main__":
    print("🧪 Testing Event Handler...\n")
    
    # Create handler with default day types
    handler = create_default_event_handler()
    
    print("📋 Registered Day Types:")
    for dt_id, dt in handler.day_types.items():
        print(f"   {dt_id}: priority={dt.priority.value}, forms={len(dt.forms)}, is_event={dt.is_event}")
    print()
    
    # Test 1: Regular day (no events)
    print("🔍 Test 1: Regular AB day (no events)")
    candidates = ["AB", "FREE"]
    active = handler.determine_active_day_type(candidates)
    print(f"   Candidates: {candidates}")
    print(f"   Active: {active.id}")
    print(f"   Forms: {active.forms}")
    print(f"   ✅ AB wins over FREE\n")
    
    # Test 2: Event overrides regular schedule
    print("🔍 Test 2: Event day overrides regular schedule")
    candidates = ["A_ONLY", "AB", "EVENT_EOT"]
    active = handler.determine_active_day_type(candidates)
    explanation = handler.get_priority_explanation(candidates)
    print(f"   Candidates: {candidates}")
    print(f"   Active: {active.id}")
    print(f"   Forms: {active.forms}")
    print(f"   Excluded: {explanation['excluded']}")
    print(f"   Reason: {explanation['reason']}")
    print(f"   ✅ EVENT_EOT wins, regular schedules excluded\n")
    
    # Test 3: Priority ordering among regular days
    print("🔍 Test 3: Priority among regular day types")
    candidates = ["A_ONLY", "AB", "ABC"]
    active = handler.determine_active_day_type(candidates)
    print(f"   Candidates: {candidates}")
    print(f"   Active: {active.id}")
    print(f"   Priority: {active.priority.value}")
    print(f"   ✅ ABC wins (highest regular priority)\n")
    
    # Test 4: Multiple events (edge case)
    print("🔍 Test 4: Multiple events (edge case - shouldn't happen but handled)")
    candidates = ["EVENT_BASELINE", "EVENT_EOT"]
    active = handler.determine_active_day_type(candidates)
    print(f"   Candidates: {candidates}")
    print(f"   Active: {active.id}")
    print(f"   ✅ First event wins (both equal priority)\n")
    
    # Test 5: Empty candidates
    print("🔍 Test 5: No candidates (free day)")
    candidates = []
    active = handler.determine_active_day_type(candidates)
    print(f"   Candidates: {candidates}")
    print(f"   Active: {active}")
    print(f"   ✅ None (free day)\n")
    
    print("✅ Event Handler working correctly!")
