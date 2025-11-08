"""
Skip Manager - Handle skipping optional forms
Allows users to skip non-required forms with a reason
"""

from typing import Dict, Optional, List, Tuple
from datetime import date, datetime
from dataclasses import dataclass


@dataclass
class Skip:
    """Record of a skipped form"""
    form_id: str
    day_type_id: str
    phase: str
    skip_date: date
    skip_reason: str
    timestamp: datetime


class SkipManager:
    """Manages form skipping functionality."""
    
    def __init__(self):
        """Initialize with empty skip storage."""
        self.skips: Dict[tuple, Skip] = {}
    
    def can_skip_form(self, form_dict: Dict) -> Tuple[bool, Optional[str]]:
        """Check if a form can be skipped."""
        required = form_dict.get('required', True)
        
        if required:
            return False, "Cannot skip required forms"
        
        return True, None
    
    def skip_form(self, form_id: str, day_type_id: str, phase: str,
                  skip_date: date, reason: str, 
                  form_config: Dict) -> Tuple[bool, str]:
        """Skip a form."""
        can_skip, error = self.can_skip_form(form_config)
        if not can_skip:
            return False, error
        
        if not reason or not reason.strip():
            return False, "Skip reason is required"
        
        key = (form_id, day_type_id, phase, skip_date)
        if key in self.skips:
            return False, f"Form '{form_id}' already skipped for this day"
        
        skip = Skip(
            form_id=form_id,
            day_type_id=day_type_id,
            phase=phase,
            skip_date=skip_date,
            skip_reason=reason.strip(),
            timestamp=datetime.now()
        )
        
        self.skips[key] = skip
        
        return True, f"Form '{form_id}' skipped successfully"
    
    def unskip_form(self, form_id: str, day_type_id: str, 
                    phase: str, skip_date: date) -> Tuple[bool, str]:
        """Remove a skip (user changes their mind)."""
        key = (form_id, day_type_id, phase, skip_date)
        
        if key not in self.skips:
            return False, f"Form '{form_id}' was not skipped"
        
        del self.skips[key]
        return True, f"Skip removed - form '{form_id}' is now pending"
    
    def is_skipped(self, form_id: str, day_type_id: str, 
                   phase: str, skip_date: date) -> bool:
        """Check if a form is skipped."""
        key = (form_id, day_type_id, phase, skip_date)
        return key in self.skips
    
    def get_skip(self, form_id: str, day_type_id: str,
                 phase: str, skip_date: date) -> Optional[Skip]:
        """Get skip details if form is skipped."""
        key = (form_id, day_type_id, phase, skip_date)
        return self.skips.get(key)
    
    def get_skips_for_day(self, day_type_id: str, phase: str,
                          skip_date: date) -> List[Skip]:
        """Get all skips for a specific day."""
        result = []
        for key, skip in self.skips.items():
            _, dt_id, p, sd = key
            if dt_id == day_type_id and p == phase and sd == skip_date:
                result.append(skip)
        return result
    
    def get_skip_count(self, day_type_id: str, phase: str,
                       skip_date: date) -> int:
        """Count skips for a day."""
        return len(self.get_skips_for_day(day_type_id, phase, skip_date))
    
    def get_skip_summary(self, day_type_id: str, phase: str,
                         skip_date: date) -> str:
        """Generate human-readable skip summary."""
        skips = self.get_skips_for_day(day_type_id, phase, skip_date)
        
        if not skips:
            return "No forms skipped today"
        
        count = len(skips)
        form_list = ", ".join([s.form_id for s in skips])
        
        return f"⏭️ {count} form(s) skipped: {form_list}"


if __name__ == "__main__":
    manager = SkipManager()
    
    # Form configs
    required_form = {'id': 'form_a', 'required': True}
    optional_form = {'id': 'form_b', 'required': False}
    
    # Try to skip required form (should fail)
    success, msg = manager.skip_form(
        'form_a',
        'ab_day_intervention',
        'intervention',
        date(2024, 11, 6),
        "Not feeling well",
        required_form
    )
    print(f"Skip required: {success} - {msg}")
    
    # Skip optional form (should succeed)
    success, msg = manager.skip_form(
        'form_b',
        'ab_day_intervention',
        'intervention',
        date(2024, 11, 6),
        "Not feeling well",
        optional_form
    )
    print(f"Skip optional: {success} - {msg}")
    
    # Check if skipped
    is_skipped = manager.is_skipped(
        'form_b',
        'ab_day_intervention',
        'intervention',
        date(2024, 11, 6)
    )
    print(f"Form B skipped: {is_skipped}")
    
    # Get skip details
    skip = manager.get_skip(
        'form_b',
        'ab_day_intervention',
        'intervention',
        date(2024, 11, 6)
    )
    if skip:
        print(f"Skip reason: {skip.skip_reason}")
    
    # Summary
    summary = manager.get_skip_summary(
        'ab_day_intervention',
        'intervention',
        date(2024, 11, 6)
    )
    print(summary)