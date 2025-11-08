"""
Study Progress Calculator - Track overall study completion
Shows big-picture progress: "You're 40% through the study"
"""

from typing import Dict, List, Optional
from datetime import date, timedelta
from dataclasses import dataclass
from completion_tracker import CompletionTracker


@dataclass
class StudyConfig:
    """Configuration for a study"""
    study_name: str
    start_date: date
    phases: List[Dict]


@dataclass
class StudyProgress:
    """Overall study progress metrics"""
    study_name: str
    current_day: int
    total_days: int
    days_completed: int
    days_remaining: int
    current_phase: str
    phase_day: int
    overall_percentage: float
    forms_completed: int
    forms_total: int
    forms_percentage: float
    estimated_completion_date: date


class StudyProgressCalculator:
    """Calculate overall study progress."""
    
    def __init__(self, study_config: StudyConfig, 
                 completion_tracker: CompletionTracker):
        """Initialize with study configuration and completion tracker."""
        self.config = study_config
        self.tracker = completion_tracker
        
        self.total_days = sum(p['duration_days'] for p in study_config.phases)
        self.total_forms = sum(
            len(p.get('required_forms', [])) for p in study_config.phases
        )
    
    def get_study_day(self, current_date: date) -> int:
        """Calculate which day of the study we're on."""
        delta = current_date - self.config.start_date
        return delta.days + 1
    
    def get_current_phase(self, current_date: date) -> tuple[str, int]:
        """Determine which phase we're in and which day of that phase."""
        study_day = self.get_study_day(current_date)
        
        day_counter = 0
        for phase in self.config.phases:
            phase_duration = phase['duration_days']
            
            if study_day <= day_counter + phase_duration:
                day_in_phase = study_day - day_counter
                return phase['name'], day_in_phase
            
            day_counter += phase_duration
        
        last_phase = self.config.phases[-1]['name']
        return last_phase, study_day - day_counter
    
    def get_progress(self, current_date: date) -> StudyProgress:
        """Calculate comprehensive study progress."""
        study_day = self.get_study_day(current_date)
        days_completed = study_day - 1
        days_remaining = max(0, self.total_days - study_day + 1)
        
        current_phase, phase_day = self.get_current_phase(current_date)
        
        overall_pct = (days_completed / self.total_days * 100) if self.total_days > 0 else 0.0
        
        forms_completed = len(self.tracker.completions)
        forms_pct = (forms_completed / self.total_forms * 100) if self.total_forms > 0 else 0.0
        
        estimated_completion = self.config.start_date + timedelta(days=self.total_days)
        
        return StudyProgress(
            study_name=self.config.study_name,
            current_day=study_day,
            total_days=self.total_days,
            days_completed=days_completed,
            days_remaining=days_remaining,
            current_phase=current_phase,
            phase_day=phase_day,
            overall_percentage=round(overall_pct, 1),
            forms_completed=forms_completed,
            forms_total=self.total_forms,
            forms_percentage=round(forms_pct, 1),
            estimated_completion_date=estimated_completion
        )
    
    def get_progress_message(self, current_date: date) -> str:
        """Generate human-readable progress message."""
        progress = self.get_progress(current_date)
        
        return (f"📅 Day {progress.current_day} of {progress.total_days} "
                f"({progress.overall_percentage}% complete). "
                f"Currently in {progress.current_phase.capitalize()} phase, day {progress.phase_day}.")
    
    def get_forms_message(self, current_date: date) -> str:
        """Generate forms completion message."""
        progress = self.get_progress(current_date)
        
        return (f"📝 You've completed {progress.forms_completed} of {progress.forms_total} "
                f"forms ({progress.forms_percentage}%)")
    
    def get_timeline_message(self, current_date: date) -> str:
        """Generate timeline message."""
        progress = self.get_progress(current_date)
        
        completion_str = progress.estimated_completion_date.strftime('%B %d, %Y')
        
        return f"⏰ {progress.days_remaining} days remaining. Estimated completion: {completion_str}"
    
    def get_complete_summary(self, current_date: date) -> str:
        """Generate complete study progress summary."""
        lines = [
            self.get_progress_message(current_date),
            self.get_forms_message(current_date),
            self.get_timeline_message(current_date)
        ]
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Define study configuration
    study_config = StudyConfig(
        study_name="Clinical Trial Phase 2",
        start_date=date(2024, 11, 1),
        phases=[
            {
                'name': 'screening',
                'duration_days': 7,
                'required_forms': ['consent', 'eligibility', 'medical_history']
            },
            {
                'name': 'intervention',
                'duration_days': 14,
                'required_forms': ['daily_diary', 'weekly_qol', 'pain_scale']
            }
        ]
    )
    
    tracker = CompletionTracker()
    calculator = StudyProgressCalculator(study_config, tracker)
    
    # Simulate some completions
    from datetime import datetime
    tracker.record_completion('consent', 'baseline_screening', 'screening', date(2024, 11, 1))
    tracker.record_completion('eligibility', 'baseline_screening', 'screening', date(2024, 11, 2))
    
    current_date = date(2024, 11, 6)
    
    print("Complete Summary:")
    print(calculator.get_complete_summary(current_date))
    