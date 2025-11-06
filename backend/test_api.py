#!/usr/bin/env python3
"""Quick test script for the AI Form Generator API"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*60)
print("🧪 Testing AI Form Generator API")
print("="*60)

# Test 1: Health Check
print("\n1️⃣ Health Check...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.json()}")

# Test 2: Schedule Generation
print("\n2️⃣ Generating Schedule (Daily + Weekly)...")
schedule_request = {
    "study_id": "demo_study",
    "study_duration_days": 14,
    "forms": [
        {"form_id": "daily_diary", "frequency_days": 1, "frequency_label": "Daily"},
        {"form_id": "weekly_assessment", "frequency_days": 7, "frequency_label": "Weekly"}
    ]
}

response = requests.post(
    f"{BASE_URL}/api/v1/schedule/generate",
    json=schedule_request
)

result = response.json()

if result["success"]:
    print(f"   ✅ Success!")
    print(f"   Anchor Cycle: {result['anchor_cycle_days']} days")
    print(f"   Total Days: {result['statistics']['total_days']}")
    print(f"   Coverage: {result['statistics']['coverage_percentage']:.1f}%")
    print(f"\n   First 7 days of schedule:")
    for day in range(1, 8):
        forms = result['schedule'].get(str(day), [])
        print(f"      Day {day}: {', '.join(forms)}")
else:
    print(f"   ❌ Failed: {result['error']}")

print("\n" + "="*60)
print("✅ All tests complete!")
print("="*60 + "\n")
