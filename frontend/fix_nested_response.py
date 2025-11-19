with open('design-studio.html', 'r') as f:
    content = f.read()

# Find the line where we extract studyId
old_line = "const studyId = studyData.database_study_id || studyData.study_id;"

new_line = "const studyId = studyData.data?.database_study_id || studyData.database_study_id || studyData.study_id;"

if old_line in content:
    content = content.replace(old_line, new_line)
    print("✅ Fixed nested response handling")
else:
    print("⚠️ Line not found - may already be fixed")

with open('design-studio.html', 'w') as f:
    f.write(content)

print("🎉 Frontend updated to handle nested response!")
