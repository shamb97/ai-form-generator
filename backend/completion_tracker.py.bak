"""
Completion Tracker - Enhanced completion tracking with timestamps
Stores WHO completed WHAT, WHEN, and WHERE in the study
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class Completion:
    """A single form completion record"""
    form_id: str
    day_type_id: str
    phase: str
    completion_date: date
    completion_time: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    

@dataclass
class CompletionSummary:
    """Summary of completions for a specific context"""
    date: date
    phase: Optional[str]
    total_completions: int
    completions: List[Completion]
    earliest_time: Optional[datetime]
    latest_time: Optional[datetime]
    

class CompletionTracker:
    """
    Enhanced completion tracking with full metadata.
    """
    
    def __init__(self):
        """Initialize with empty completion storage."""
        self.completions: Dict[Tuple, Completion] = {}
        self.by_date: Dict[date, List[Completion]] = {}
        self.by_phase: Dict[str, List[Completion]] = {}
    
    def record_completion(
        self,
        form_id: str,
        day_type_id: str,
        phase: str,
        completion_date: date,
        completion_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Record a form completion with full metadata."""
        if completion_time is None:
            completion_time = datetime.now()
        
        key = (form_id, day_type_id, phase, completion_date)
        
        if key in self.completions:
            existing = self.completions[key]
            return False, f"Form '{form_id}' already completed on {completion_date}"
        
        completion = Completion(
            form_id=form_id,
            day_type_id=day_type_id,
            phase=phase,
            completion_date=completion_date,
            completion_time=completion_time,
            user_id=user_id,
            session_id=session_id
        )
        
        self.completions[key] = completion
        
        if completion_date not in self.by_date:
            self.by_date[completion_date] = []
        self.by_date[completion_date].append(completion)
        
        if phase not in self.by_phase:
            self.by_phase[phase] = []
        self.by_phase[phase].append(completion)
        
        return True, f"Form '{form_id}' completed at {completion_time.strftime('%H:%M:%S')}"
    
    def is_complete(self, form_id: str, day_type_id: str, phase: str, 
                   completion_date: date) -> bool:
        """Check if a form is completed."""
        key = (form_id, day_type_id, phase, completion_date)
        return key in self.completions
    
    def get_completion(self, form_id: str, day_type_id: str, phase: str,
                      completion_date: date) -> Optional[Completion]:
        """Get completion details."""
        key = (form_id, day_type_id, phase, completion_date)
        return self.completions.get(key)
    
    def get_completions_for_date(self, target_date: date, 
                                 phase: Optional[str] = None) -> List[Completion]:
        """Get all completions for a date."""
        completions = self.by_date.get(target_date, [])
        if phase:
            completions = [c for c in completions if c.phase == phase]
        return sorted(completions, key=lambda c: c.completion_time)
    
    def get_summary_for_date(self, target_date: date,
                            phase: Optional[str] = None) -> CompletionSummary:
        """Generate summary for a date."""
        completions = self.get_completions_for_date(target_date, phase)
        earliest = min((c.completion_time for c in completions), default=None)
        latest = max((c.completion_time for c in completions), default=None)
        
        return CompletionSummary(
            date=target_date,
            phase=phase,
            total_completions=len(completions),
            completions=completions,
            earliest_time=earliest,
            latest_time=latest
        )
    
    def get_today_summary_message(self, target_date: date) -> str:
        """Generate human-readable summary."""
        summary = self.get_summary_for_date(target_date)
        
        if summary.total_completions == 0:
            return "No forms completed yet today"
        
        count = summary.total_completions
        earliest = summary.earliest_time.strftime('%I:%M %p')
        latest = summary.latest_time.strftime('%I:%M %p')
        
        if count == 1:
            return f"✅ You completed 1 form today at {earliest}"
        else:
            return f"✅ You completed {count} forms today between {earliest} and {latest}"


if __name__ == "__main__":
    # Test it
    tracker = CompletionTracker()
    
    success, msg = tracker.record_completion(
        'form_a', 'ab_day', 'intervention',
        date(2024, 11, 6), datetime(2024, 11, 6, 9, 15, 0)
    )
    print(msg)
    
    print(tracker.get_today_summary_message(date(2024, 11, 6)))