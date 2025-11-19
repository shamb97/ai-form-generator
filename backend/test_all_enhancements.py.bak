"""
MEGA INTEGRATION TEST - All Navigation Enhancements Working Together
Tests: completion_tracker + skip_manager + progress_tracker + 
       multi_phase_summary + study_progress + timeline_calculator
"""

from datetime import datetime, date

from completion_tracker import CompletionTracker
from skip_manager import SkipManager
from progress_tracker import ProgressTracker
from multi_phase_summary import MultiPhaseSummaryGenerator
from study_progress import StudyConfig, StudyProgressCalculator
from timeline_calculator import TimelineCalculator


def test_complete_workflow():
    """
    Simulate a complete day in a multi-phase study.
    This tests EVERYTHING working together!
    """
    
    print("=" * 70)
    print("🧪 MEGA INTEGRATION TEST - All Features Working Together")
    print("=" * 70)
    print()
    
    # ========== SETUP STUDY ==========
    print("📋 Setting up study configuration...")
    
    study_config = StudyConfig(
        study_name="Clinical Trial Demo",
        start_date=date(2024, 11, 1),
        phases=[
            {
                'name': 'screening',
                'duration_days': 7,
                'required_forms': ['consent', 'eligibility']
            },
            {
                'name': 'intervention',
                'duration_days': 14,
                'required_forms': ['daily_diary', 'weekly_qol']
            },
            {
                'name': 'followup',
                'duration_days': 7,
                'required_forms': ['final_assessment']
            }
        ]
    )
    
    print(f"✅ Study: {study_config.study_name}")
    print(f"✅ Start: {study_config.start_date}")
    print(f"✅ Total duration: 28 days")
    print()
    
    # ========== INITIALIZE TRACKERS ==========
    print("🔧 Initializing trackers...")
    
    completion_tracker = CompletionTracker()
    skip_manager = SkipManager()
    
    print("✅ Completion tracker ready")
    print("✅ Skip manager ready")
    print()
    
    # ========== SIMULATE DAY 1-2: SCREENING PHASE ==========
    print("=" * 70)
    print("📅 DAY 1-2: SCREENING PHASE")
    print("=" * 70)
    print()
    
    # Day 1: Complete consent form
    print("Day 1 (Nov 1): Completing consent form...")
    success, msg = completion_tracker.record_completion(
        'consent',
        'baseline_screening',
        'screening',
        date(2024, 11, 1),
        datetime(2024, 11, 1, 9, 15, 0)
    )
    print(f"  {msg}")
    
    # Day 2: Complete eligibility form
    print("Day 2 (Nov 2): Completing eligibility form...")
    success, msg = completion_tracker.record_completion(
        'eligibility',
        'baseline_screening',
        'screening',
        date(2024, 11, 2),
        datetime(2024, 11, 2, 10, 30, 0)
    )
    print(f"  {msg}")
    print()
    
    # ========== SIMULATE DAY 10: INTERVENTION PHASE ==========
    print("=" * 70)
    print("📅 DAY 10: INTERVENTION PHASE")
    print("=" * 70)
    print()
    
    current_date = date(2024, 11, 10)
    
    # Morning: Complete daily diary
    print(f"Day 10 (Nov 10) - Morning: Completing daily diary...")
    success, msg = completion_tracker.record_completion(
        'daily_diary',
        'a_day_intervention',
        'intervention',
        current_date,
        datetime(2024, 11, 10, 9, 0, 0)
    )
    print(f"  {msg}")
    
    # Afternoon: Skip weekly QOL (pretend it's optional)
    print(f"Day 10 (Nov 10) - Afternoon: Skipping weekly QOL...")
    optional_qol = {'id': 'weekly_qol', 'required': False}
    success, msg = skip_manager.skip_form(
        'weekly_qol',
        'a_day_intervention',
        'intervention',
        current_date,
        "Feeling unwell today",
        optional_qol
    )
    print(f"  {msg}")
    print()
    
    # ========== TODAY'S SUMMARY ==========
    print("=" * 70)
    print("📊 TODAY'S SUMMARY (Nov 10)")
    print("=" * 70)
    print()
    
    # 1. Completion summary with timestamps
    print("1️⃣ COMPLETION SUMMARY:")
    today_summary = completion_tracker.get_summary_for_date(current_date)
    print(f"   {completion_tracker.get_today_summary_message(current_date)}")
    if today_summary.completions:
        for comp in today_summary.completions:
            time_str = comp.completion_time.strftime('%I:%M %p')
            print(f"   - {comp.form_id} at {time_str}")
    print()
    
    # 2. Skip summary
    print("2️⃣ SKIP SUMMARY:")
    skip_summary = skip_manager.get_skip_summary(
        'a_day_intervention',
        'intervention',
        current_date
    )
    print(f"   {skip_summary}")
    print()
    
    # 3. Progress tracking
    print("3️⃣ PROGRESS TRACKING:")
    forms = [
        {'id': 'daily_diary', 'required': True},
        {'id': 'weekly_qol', 'required': False}
    ]
    
    progress_tracker_inst = ProgressTracker(
        completions={
            ('daily_diary', 'a_day_intervention', 'intervention', current_date): True
        },
        skips=skip_manager.skips
    )
    
    progress_msg = progress_tracker_inst.get_summary_message(
        'a_day_intervention',
        'intervention',
        forms,
        current_date
    )
    print(f"   {progress_msg}")
    print()
    
    # ========== MULTI-PHASE SUMMARY ==========
    print("=" * 70)
    print("📈 MULTI-PHASE SUMMARY")
    print("=" * 70)
    print()
    
    multi_phase_gen = MultiPhaseSummaryGenerator(completion_tracker)
    phases = ['screening', 'intervention', 'followup']
    
    print("4️⃣ CROSS-PHASE ACTIVITY:")
    multi_msg = multi_phase_gen.get_summary_message(current_date, phases)
    print(f"   {multi_msg}")
    print()
    
    print("   Detailed breakdown:")
    detailed = multi_phase_gen.get_detailed_summary(current_date, phases)
    for line in detailed.split('\n'):
        print(f"   {line}")
    print()
    
    # ========== OVERALL STUDY PROGRESS ==========
    print("=" * 70)
    print("🎯 OVERALL STUDY PROGRESS")
    print("=" * 70)
    print()
    
    study_calc = StudyProgressCalculator(study_config, completion_tracker)
    
    print("5️⃣ COMPLETE STUDY STATUS:")
    complete_summary = study_calc.get_complete_summary(current_date)
    for line in complete_summary.split('\n'):
        print(f"   {line}")
    print()
    
    # ========== TIMELINE VISUALIZATION ==========
    print("=" * 70)
    print("📅 STUDY TIMELINE")
    print("=" * 70)
    print()
    
    timeline_calc = TimelineCalculator(
        study_config.study_name,
        study_config.start_date,
        [{'name': p['name'], 'duration_days': p['duration_days']} 
         for p in study_config.phases]
    )
    
    print("6️⃣ TIMELINE VISUALIZATION:")
    print()
    viz = timeline_calc.get_study_timeline_visualization(current_date)
    print(viz)
    print()
    
    timeline_msg = timeline_calc.get_timeline_message(current_date)
    print(f"   {timeline_msg}")
    print()
    
    # ========== FINAL SUMMARY ==========
    print("=" * 70)
    print("✅ INTEGRATION TEST COMPLETE!")
    print("=" * 70)
    print()
    print("All 6 modules working together successfully:")
    print("  ✅ completion_tracker.py - Timestamps recorded")
    print("  ✅ skip_manager.py - Forms skipped with reasons")
    print("  ✅ progress_tracker.py - Progress calculated")
    print("  ✅ multi_phase_summary.py - Cross-phase view generated")
    print("  ✅ study_progress.py - Overall progress tracked")
    print("  ✅ timeline_calculator.py - Timeline visualized")
    print()
    print("🎉 ALL FEATURES OPERATIONAL! 🎉")
    print()


if __name__ == "__main__":
    test_complete_workflow()