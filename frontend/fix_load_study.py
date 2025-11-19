import re

with open('design-studio.html', 'r') as f:
    content = f.read()

# Backup
with open('design-studio.html.backup_before_final_fix', 'w') as f:
    f.write(content)
print("✅ Backup created: design-studio.html.backup_before_final_fix")

# Find and replace the entire loadStudyIntoStudio function
old_function = r'function loadStudyIntoStudio\(studyData\) \{[^}]*\}(?=\s*// ===== INITIALIZATION)'

new_function = '''function loadStudyIntoStudio(studyData) {
            console.log('📊 Loading study into Design Studio:', studyData);
            
            // The studyData from create-study contains the database_study_id
            const studyId = studyData.database_study_id || studyData.study_id;
            
            if (!studyId) {
                console.error('❌ No study ID found in response');
                alert('Error: Could not load study - no ID returned');
                return;
            }
            
            console.log(`🔍 Fetching study ${studyId} from database...`);
            
            // Fetch the full study from the database
            fetch(`${API_BASE_URL}/api/v1/studies/${studyId}`)
                .then(response => response.json())
                .then(data => {
                    console.log('✅ Study fetched from database:', data);
                    
                    if (!data.success || !data.study) {
                        throw new Error('Study not found in database');
                    }
                    
                    const study = data.study;
                    
                    // Update sidebar subtitle
                    document.getElementById('study-subtitle').textContent = study.name;
                    
                    // Hide AI hero, show study overview
                    document.querySelector('.ai-hero').style.display = 'none';
                    document.getElementById('study-overview-content').style.display = 'block';
                    
                    // Populate study details
                    document.getElementById('study-name').textContent = study.name;
                    document.getElementById('study-forms-count').textContent = study.form_count || 0;
                    
                    // Calculate duration from schedule if available
                    const duration = studyData.schedule?.recommended_lcm 
                        ? studyData.schedule.recommended_lcm 
                        : 30;
                    document.getElementById('study-duration').textContent = duration + ' days';
                    
                    // Show phases or default
                    const phasesCount = studyData.phases?.length || 0;
                    document.getElementById('study-phases-count').textContent = phasesCount > 0 
                        ? phasesCount 
                        : '1 (No phases)';
                    
                    // Show status
                    document.getElementById('study-status').innerHTML = 
                        `<span style="color: #27ae60;">✅ ${study.status} (ID: ${study.id})</span>`;
                    
                    console.log('✅ Study loaded into Design Studio!');
                    console.log(`   Name: ${study.name}`);
                    console.log(`   Forms: ${study.form_count}`);
                    console.log(`   Status: ${study.status}`);
                    
                    // Show success notification
                    alert(`🎉 SUCCESS!\\n\\nYour AI-generated study is ready!\\n\\nStudy: ${study.name}\\nForms: ${study.form_count}\\nStatus: ${study.status}\\nID: ${study.id}\\n\\nReview the forms, schedule, and settings in the panels on the left.`);
                })
                .catch(error => {
                    console.error('❌ Error loading study:', error);
                    alert(`Error loading study: ${error.message}\\n\\nThe study was created (ID: ${studyId}) but could not be loaded. Try refreshing the page.`);
                });
        }'''

# Replace the function
content = re.sub(old_function, new_function, content, flags=re.DOTALL)

# Write back
with open('design-studio.html', 'w') as f:
    f.write(content)

print("✅ loadStudyIntoStudio() function updated!")
print("\n📋 What changed:")
print("   1. Now fetches study from /api/v1/studies/{id}")
print("   2. Uses correct field names (name, form_count, status)")
print("   3. Shows study ID and status")
print("   4. Better error handling")
print("\n🎉 Ready to test!")
