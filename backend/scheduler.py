from math import gcd
from functools import reduce
from typing import List, Dict
from pydantic import BaseModel

class FormSchedule(BaseModel):
    form_id: str
    frequency_days: int
    frequency_label: str = ""

class ScheduleRequest(BaseModel):
    study_id: str
    study_duration_days: int
    forms: List[FormSchedule]

class ScheduleResponse(BaseModel):
    success: bool
    study_id: str
    anchor_cycle_days: int
    schedule: Dict[int, List[str]]
    statistics: Dict[str, float]
    error: str | None = None

def lcm(a: int, b: int) -> int:
    """Calculate Lowest Common Multiple of two numbers."""
    return abs(a * b) // gcd(a, b)


def calculate_lcm_schedule(request: ScheduleRequest) -> ScheduleResponse:
    """
    Calculate LCM-based schedule for multiple forms.
    
    Algorithm:
    1. Calculate LCM of all form frequencies
    2. For each day in the anchor cycle, determine which forms appear
    3. Generate complete schedule for study duration
    4. Return day-by-day mapping of forms
    """
    
    # Extract frequencies
    frequencies = [form.frequency_days for form in request.forms]
    
    # Calculate LCM of all frequencies (anchor cycle)
    anchor_cycle = reduce(lcm, frequencies)
    
    # Safety check: prevent extremely long cycles
    MAX_CYCLE = 365
    if anchor_cycle > MAX_CYCLE:
        return ScheduleResponse(
            success=False,
            study_id=request.study_id,
            anchor_cycle_days=anchor_cycle,
            schedule={},
            statistics={},
            error=f"Anchor cycle too long ({anchor_cycle} days). Maximum allowed: {MAX_CYCLE} days."
        )
    
    # Build schedule for each day
    schedule = {}
    
    for day in range(1, request.study_duration_days + 1):
        # Determine which forms appear on this day
        forms_today = []
        
        for form in request.forms:
            # Form appears if: (day - 1) mod frequency == 0
            if (day - 1) % form.frequency_days == 0:
                forms_today.append(form.form_id)
        
        # Only store days with forms (skip empty days)
        if forms_today:
            schedule[day] = forms_today
    
    # Calculate statistics
    total_forms_scheduled = sum(len(forms) for forms in schedule.values())
    days_with_forms = len(schedule)
    days_without_forms = request.study_duration_days - days_with_forms
    
    statistics = {
        "anchor_cycle_days": anchor_cycle,
        "total_days": request.study_duration_days,
        "days_with_forms": days_with_forms,
        "days_without_forms": days_without_forms,
        "total_form_instances": total_forms_scheduled,
        "avg_forms_per_day": total_forms_scheduled / request.study_duration_days if request.study_duration_days > 0 else 0,
        "coverage_percentage": (days_with_forms / request.study_duration_days * 100) if request.study_duration_days > 0 else 0
    }
    
    return ScheduleResponse(
        success=True,
        study_id=request.study_id,
        anchor_cycle_days=anchor_cycle,
        schedule=schedule,
        statistics=statistics
    )# Example usage / testing
if __name__ == "__main__":
    # Test case 1: Daily + Weekly
    print("Test Case 1: Daily + Weekly")
    print("-" * 50)
    
    request1 = ScheduleRequest(
        study_id="test_001",
        study_duration_days=14,
        forms=[
            FormSchedule(form_id="daily_diary", frequency_days=1, frequency_label="Daily"),
            FormSchedule(form_id="weekly_assessment", frequency_days=7, frequency_label="Weekly")
        ]
    )
    
    result1 = calculate_lcm_schedule(request1)
    
    if result1.success:
        print(f"Anchor Cycle: {result1.anchor_cycle_days} days")
        print(f"\nSchedule for first 14 days:")
        for day in range(1, 15):
            forms = result1.schedule.get(day, [])
            if forms:
                print(f"Day {day:2d}: {', '.join(forms)}")
            else:
                print(f"Day {day:2d}: (no forms)")
        
        print(f"\nStatistics:")
        for key, value in result1.statistics.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 50 + "\n")
    
    # Test case 2: Complex frequencies
    print("Test Case 2: Every 3, 6, and 9 days")
    print("-" * 50)
    
    request2 = ScheduleRequest(
        study_id="test_002",
        study_duration_days=20,
        forms=[
            FormSchedule(form_id="form_a", frequency_days=3, frequency_label="Every 3 days"),
            FormSchedule(form_id="form_b", frequency_days=6, frequency_label="Every 6 days"),
            FormSchedule(form_id="form_c", frequency_days=9, frequency_label="Every 9 days")
        ]
    )
    
    result2 = calculate_lcm_schedule(request2)
    
    if result2.success:
        print(f"Anchor Cycle: {result2.anchor_cycle_days} days")
        print(f"\nSchedule for first 20 days:")
        for day in range(1, 21):
            forms = result2.schedule.get(day, [])
            if forms:
                print(f"Day {day:2d}: {', '.join(forms)}")
            else:
                print(f"Day {day:2d}: (FREE DAY - no forms)")
        
        print(f"\nStatistics:")
        for key, value in result2.statistics.items():
            print(f"  {key}: {value}")
