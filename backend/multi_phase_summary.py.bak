"""
Multi-Phase Summary - View completions across all phases
Shows cross-phase progress and phase transitions
"""

from typing import Dict, List
from datetime import date
from dataclasses import dataclass
from completion_tracker import CompletionTracker, Completion


@dataclass
class PhaseCompletionStats:
    """Statistics for a single phase"""
    phase: str
    completion_count: int
    forms_completed: List[str]


@dataclass
class MultiPhaseSummary:
    """Summary across multiple phases"""
    date: date
    phases: List[PhaseCompletionStats]
    total_completions: int
    phases_active: int


class MultiPhaseSummaryGenerator:
    """Generate summaries that span multiple phases."""
    
    def __init__(self, completion_tracker: CompletionTracker):
        """Initialize with a completion tracker."""
        self.tracker = completion_tracker
    
    def get_summary_for_date(self, target_date: date, 
                            phases: List[str]) -> MultiPhaseSummary:
        """Generate multi-phase summary for a date."""
        phase_stats = []
        total = 0
        active_phases = 0
        
        for phase in phases:
            completions = self.tracker.get_completions_for_date(target_date, phase)
            count = len(completions)
            form_ids = [c.form_id for c in completions]
            
            if count > 0:
                active_phases += 1
            
            total += count
            
            phase_stats.append(PhaseCompletionStats(
                phase=phase,
                completion_count=count,
                forms_completed=form_ids
            ))
        
        return MultiPhaseSummary(
            date=target_date,
            phases=phase_stats,
            total_completions=total,
            phases_active=active_phases
        )
    
    def get_summary_message(self, target_date: date, 
                           phases: List[str]) -> str:
        """Generate human-readable multi-phase summary."""
        summary = self.get_summary_for_date(target_date, phases)
        
        if summary.total_completions == 0:
            return "No forms completed today in any phase"
        
        parts = []
        for stats in summary.phases:
            if stats.completion_count > 0:
                parts.append(f"{stats.completion_count} {stats.phase}")
        
        phase_text = ", ".join(parts)
        return f"✅ Today: {phase_text} ({summary.total_completions} total)"
    
    def get_detailed_summary(self, target_date: date, 
                            phases: List[str]) -> str:
        """Generate detailed multi-phase summary with form lists."""
        summary = self.get_summary_for_date(target_date, phases)
        
        if summary.total_completions == 0:
            return "No completions to show"
        
        lines = []
        for stats in summary.phases:
            if stats.completion_count > 0:
                form_list = ", ".join(stats.forms_completed)
                lines.append(f"{stats.phase.capitalize()}: {form_list}")
        
        return "\n".join(lines)
    
    def compare_phases(self, target_date: date, 
                       phases: List[str]) -> Dict[str, int]:
        """Compare completion counts across phases."""
        summary = self.get_summary_for_date(target_date, phases)
        return {stats.phase: stats.completion_count for stats in summary.phases}
    
    def get_most_active_phase(self, target_date: date, 
                              phases: List[str]) -> str:
        """Find which phase had most completions."""
        comparison = self.compare_phases(target_date, phases)
        
        if not comparison or all(v == 0 for v in comparison.values()):
            return "none"
        
        return max(comparison.items(), key=lambda x: x[1])[0]


if __name__ == "__main__":
    from datetime import datetime
    
    # Setup
    tracker = CompletionTracker()
    
    # Record completions in different phases
    tracker.record_completion('consent', 'baseline_screening', 'screening', 
                             date(2024, 11, 6), datetime(2024, 11, 6, 9, 0, 0))
    tracker.record_completion('eligibility', 'baseline_screening', 'screening',
                             date(2024, 11, 6), datetime(2024, 11, 6, 9, 30, 0))
    tracker.record_completion('daily_diary', 'a_day_intervention', 'intervention',
                             date(2024, 11, 6), datetime(2024, 11, 6, 10, 0, 0))
    tracker.record_completion('weekly_qol', 'a_day_intervention', 'intervention',
                             date(2024, 11, 6), datetime(2024, 11, 6, 11, 0, 0))
    tracker.record_completion('pain_scale', 'a_day_intervention', 'intervention',
                             date(2024, 11, 6), datetime(2024, 11, 6, 14, 0, 0))
    
    # Generate multi-phase summary
    generator = MultiPhaseSummaryGenerator(tracker)
    phases = ['screening', 'intervention', 'followup']
    
    print("Summary Message:")
    print(generator.get_summary_message(date(2024, 11, 6), phases))
    print()
    
    print("Detailed Summary:")
    print(generator.get_detailed_summary(date(2024, 11, 6), phases))
    print()
    
    print("Most Active Phase:")
    print(f"  {generator.get_most_active_phase(date(2024, 11, 6), phases)}")