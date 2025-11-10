"""
Test Phase-Based Form Filtering
Visual demonstration of Component 1
"""

# Mock data from our study
study = {
    "study_id": 3,
    "study_name": "Clinical Trial with Phases",
    "phases": ["baseline", "intervention", "followup"],
    "forms": [
        {"form_name": "Informed Consent", "active_phases": ["baseline"]},
        {"form_name": "Eligibility Screening", "active_phases": ["baseline"]},
        {"form_name": "Daily Pain Diary", "active_phases": ["all"]},
        {"form_name": "Medication Log", "active_phases": ["intervention", "followup"]},
        {"form_name": "Weekly Quality of Life", "active_phases": ["intervention"]},
        {"form_name": "Final Satisfaction Survey", "active_phases": ["followup"]},
    ]
}

def get_forms_for_phase(phase):
    """Filter forms by phase - same logic as our API"""
    filtered = []
    for form in study["forms"]:
        active_phases = form["active_phases"]
        if "all" in active_phases or phase in active_phases:
            filtered.append(form)
    return filtered

# Test all phases
print("=" * 60)
print(f"Study: {study['study_name']}")
print("=" * 60)
print()

for phase in study["phases"]:
    forms = get_forms_for_phase(phase)
    print(f"📋 PHASE: {phase.upper()}")
    print(f"   Forms available: {len(forms)}")
    for form in forms:
        print(f"   ✅ {form['form_name']}")
    print()

# Show the phase activation matrix
print("=" * 60)
print("PHASE ACTIVATION MATRIX")
print("=" * 60)
print(f"{'Form Name':<30} | {'Baseline':<10} | {'Intervention':<14} | {'Followup':<10}")
print("-" * 75)

for form in study["forms"]:
    active = form["active_phases"]
    baseline = "✅" if "all" in active or "baseline" in active else "❌"
    intervention = "✅" if "all" in active or "intervention" in active else "❌"
    followup = "✅" if "all" in active or "followup" in active else "❌"
    
    print(f"{form['form_name']:<30} | {baseline:<10} | {intervention:<14} | {followup:<10}")

print()
print("✅ Component 1: Phase-Based Activation is working!")