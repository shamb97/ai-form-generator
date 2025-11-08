"""
Progress Tracker - Shows completion status for current day
Answers: "How many forms done? How many left?"
"""

from typing import Dict, List, Optional
from datetime import date
from dataclasses import dataclass


@dataclass
class FormProgress:
    """Progress for a single form"""
    form_id: str
    status: str  # 'pending', 'complete', 'skipped'
    required: bool


@dataclass
class DayProgress:
    """Overall progress for a day"""
    day_type_id: str
    phase: str
    date: date
    total_forms: int
    completed_forms: int
    skipped_forms: int
    pending_forms: int
    required_pending: int
    percentage_complete: float
    form_details: List[FormProgress]


class ProgressTracker:
    """Tracks completion progress for forms within a day type."""
    
    def __init__(self, completions: Dict, skips: Dict):
        """Initialize with completion and skip data."""
        self.completions = completions
        self.skips = skips
    
    def get_progress(self, day_type_id: str, phase: str, 
                    forms: List[Dict], target_date: date) -> DayProgress:
        """Calculate progress for a specific day type."""
        form_details = []
        completed = 0
        skipped = 0
        pending = 0
        required_pending = 0
        
        for form_dict in forms:
            form_id = form_dict['id']
            required = form_dict.get('required', True)
            
            comp_key = (form_id, day_type_id, phase, target_date)
            is_complete = self.completions.get(comp_key, False)
            
            skip_key = (form_id, day_type_id, phase, target_date)
            is_skipped = skip_key in self.skips
            
            if is_complete:
                status = 'complete'
                completed += 1
            elif is_skipped:
                status = 'skipped'
                skipped += 1
            else:
                status = 'pending'
                pending += 1
                if required:
                    required_pending += 1
            
            form_details.append(FormProgress(
                form_id=form_id,
                status=status,
                required=required
            ))
        
        total = len(forms)
        done_count = completed + skipped
        percentage = (done_count / total * 100) if total > 0 else 0.0
        
        return DayProgress(
            day_type_id=day_type_id,
            phase=phase,
            date=target_date,
            total_forms=total,
            completed_forms=completed,
            skipped_forms=skipped,
            pending_forms=pending,
            required_pending=required_pending,
            percentage_complete=round(percentage, 1),
            form_details=form_details
        )
    
    def is_day_complete(self, day_type_id: str, phase: str, 
                       forms: List[Dict], target_date: date,
                       require_all: bool = False) -> bool:
        """Check if all forms for a day are complete."""
        progress = self.get_progress(day_type_id, phase, forms, target_date)
        
        if require_all:
            return progress.completed_forms == progress.total_forms
        else:
            return progress.required_pending == 0
    
    def get_next_required_form(self, day_type_id: str, phase: str,
                              forms: List[Dict], target_date: date) -> Optional[str]:
        """Get the next required form that's still pending."""
        progress = self.get_progress(day_type_id, phase, forms, target_date)
        
        for detail in progress.form_details:
            if detail.required and detail.status == 'pending':
                return detail.form_id
        
        return None
    
    def get_summary_message(self, day_type_id: str, phase: str,
                           forms: List[Dict], target_date: date) -> str:
        """Generate a human-readable progress message."""
        progress = self.get_progress(day_type_id, phase, forms, target_date)
        
        done = progress.completed_forms + progress.skipped_forms
        total = progress.total_forms
        pct = progress.percentage_complete
        
        if done == total:
            return f"✅ All {total} forms complete! Great job! 🎉"
        elif progress.required_pending == 0:
            optional_left = progress.pending_forms
            return f"✅ All required forms complete! ({optional_left} optional remaining)"
        else:
            return f"📝 Completed {done}/{total} forms ({pct}% done)"


if __name__ == "__main__":
    # Test
    completions = {
        ('form_a', 'ab_day_intervention', 'intervention', date(2024, 11, 6)): True,
    }
    
    skips = {
        ('form_b', 'ab_day_intervention', 'intervention', date(2024, 11, 6)): "Not feeling well"
    }
    
    forms = [
        {'id': 'form_a', 'required': True},
        {'id': 'form_b', 'required': False},
        {'id': 'form_c', 'required': True},
    ]
    
    tracker = ProgressTracker(completions, skips)
    
    progress = tracker.get_progress(
        'ab_day_intervention',
        'intervention',
        forms,
        date(2024, 11, 6)
    )
    
    print(f"Total forms: {progress.total_forms}")
    print(f"Completed: {progress.completed_forms}")
    print(f"Skipped: {progress.skipped_forms}")
    print(f"Pending: {progress.pending_forms}")
    print(f"Progress: {progress.percentage_complete}%")
    print()
    print(tracker.get_summary_message(
        'ab_day_intervention',
        'intervention',
        forms,
        date(2024, 11, 6)
    ))