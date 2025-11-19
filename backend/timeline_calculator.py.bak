"""
Timeline Calculator - Calculate days remaining and study timeline
Provides time-based insights into study progress
"""

from typing import List, Optional
from datetime import date, timedelta
from dataclasses import dataclass


@dataclass
class PhaseTimeline:
    """Timeline info for a single phase"""
    name: str
    start_date: date
    end_date: date
    duration_days: int
    current: bool
    completed: bool


@dataclass
class StudyTimeline:
    """Complete study timeline"""
    study_start: date
    study_end: date
    total_duration: int
    phases: List[PhaseTimeline]
    current_phase: Optional[str]
    days_since_start: int
    days_until_end: int


class TimelineCalculator:
    """Calculate study timeline and remaining days."""
    
    def __init__(self, study_name: str, start_date: date, 
                 phases: List[dict]):
        """Initialize with study configuration."""
        self.study_name = study_name
        self.start_date = start_date
        self.phases = phases
        self.total_duration = sum(p['duration_days'] for p in phases)
        self.end_date = start_date + timedelta(days=self.total_duration - 1)
    
    def get_timeline(self, current_date: date) -> StudyTimeline:
        """Generate complete study timeline."""
        phase_timelines = []
        phase_start = self.start_date
        current_phase = None
        
        for phase_config in self.phases:
            duration = phase_config['duration_days']
            phase_end = phase_start + timedelta(days=duration - 1)
            
            is_current = phase_start <= current_date <= phase_end
            is_completed = current_date > phase_end
            
            if is_current:
                current_phase = phase_config['name']
            
            phase_timelines.append(PhaseTimeline(
                name=phase_config['name'],
                start_date=phase_start,
                end_date=phase_end,
                duration_days=duration,
                current=is_current,
                completed=is_completed
            ))
            
            phase_start = phase_end + timedelta(days=1)
        
        days_since_start = (current_date - self.start_date).days
        days_until_end = (self.end_date - current_date).days
        
        return StudyTimeline(
            study_start=self.start_date,
            study_end=self.end_date,
            total_duration=self.total_duration,
            phases=phase_timelines,
            current_phase=current_phase,
            days_since_start=days_since_start,
            days_until_end=max(0, days_until_end)
        )
    
    def get_phase_days_remaining(self, phase_name: str, 
                                 current_date: date) -> Optional[int]:
        """Calculate days remaining in a specific phase."""
        timeline = self.get_timeline(current_date)
        
        for phase in timeline.phases:
            if phase.name == phase_name and phase.current:
                return (phase.end_date - current_date).days + 1
        
        return None
    
    def get_current_phase_info(self, current_date: date) -> Optional[PhaseTimeline]:
        """Get timeline info for current phase."""
        timeline = self.get_timeline(current_date)
        
        for phase in timeline.phases:
            if phase.current:
                return phase
        
        return None
    
    def get_upcoming_phases(self, current_date: date) -> List[PhaseTimeline]:
        """Get list of phases that haven't started yet."""
        timeline = self.get_timeline(current_date)
        return [p for p in timeline.phases if not p.completed and not p.current]
    
    def get_timeline_message(self, current_date: date) -> str:
        """Generate timeline summary message."""
        current_phase = self.get_current_phase_info(current_date)
        
        if not current_phase:
            return "Study not yet started or already completed"
        
        days_left = (current_phase.end_date - current_date).days + 1
        end_str = current_phase.end_date.strftime('%b %d')
        
        upcoming = self.get_upcoming_phases(current_date)
        next_phase = upcoming[0].name.capitalize() if upcoming else "None"
        
        return (f"📅 {current_phase.name.capitalize()} phase: "
                f"{days_left} days remaining (ends {end_str}). Next: {next_phase}")
    
    def get_study_timeline_visualization(self, current_date: date) -> str:
        """Generate ASCII visualization of study timeline."""
        timeline = self.get_timeline(current_date)
        lines = []
        
        for phase in timeline.phases:
            bar_width = 12
            if phase.completed:
                bar = "=" * bar_width
                status = "DONE"
            elif phase.current:
                days_in = (current_date - phase.start_date).days + 1
                progress = days_in / phase.duration_days
                filled = int(progress * bar_width)
                bar = "=" * filled + ">" + " " * (bar_width - filled - 1)
                status = f"Day {days_in} of {phase.duration_days}"
            else:
                bar = " " * bar_width
                status = f"{phase.duration_days} days"
            
            marker = " ← YOU ARE HERE" if phase.current else ""
            line = f"{phase.name.capitalize():15} [{bar}] ({status}){marker}"
            lines.append(line)
        
        return "\n".join(lines)


if __name__ == "__main__":
    phases = [
        {'name': 'screening', 'duration_days': 7},
        {'name': 'baseline', 'duration_days': 3},
        {'name': 'intervention', 'duration_days': 14},
        {'name': 'followup', 'duration_days': 6}
    ]
    
    calculator = TimelineCalculator(
        "Clinical Trial",
        date(2024, 11, 1),
        phases
    )
    
    current_date = date(2024, 11, 6)
    
    print("Timeline Message:")
    print(calculator.get_timeline_message(current_date))
    print()
    
    print("Study Timeline Visualization:")
    print(calculator.get_study_timeline_visualization(current_date))