import re

with open('main.py', 'r') as f:
    content = f.read()

print("🔧 Updating main.py endpoints to include status field...")

# Fix 1: Update list_studies to include status
old_list = '''                "id": s.id,
                "name": s.name,
                "description": s.description,
                "created_at": s.created_at.isoformat(),
                "form_count": len(s.forms)'''

new_list = '''                "id": s.id,
                "name": s.name,
                "description": s.description,
                "status": s.status,
                "created_at": s.created_at.isoformat(),
                "form_count": len(s.forms)'''

if old_list in content:
    content = content.replace(old_list, new_list)
    print("✅ Updated list_studies endpoint")
else:
    print("⚠️  list_studies already updated or pattern not found")

# Fix 2: Update get_study_details_endpoint to include status
old_get = '''            "id": study.id,
            "name": study.name,
            "description": study.description,
            "created_at": study.created_at.isoformat(),'''

new_get = '''            "id": study.id,
            "name": study.name,
            "description": study.description,
            "status": study.status,
            "created_at": study.created_at.isoformat(),'''

if old_get in content:
    content = content.replace(old_get, new_get)
    print("✅ Updated get_study_details_endpoint")
else:
    print("⚠️  get_study_details_endpoint already updated or pattern not found")

# Write back
with open('main.py', 'w') as f:
    f.write(content)

print("\n🎉 main.py updated to include status in responses!")
