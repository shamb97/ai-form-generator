#!/usr/bin/env python3
"""
Fix design-studio.html to handle backend's nested response structure
This is a PERMANENT fix for the message parsing issue.
"""

import re
import sys

def fix_design_studio(filename='design-studio.html'):
    """Fix message parsing to handle data.data.message structure."""
    
    print(f"📝 Reading {filename}...")
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Backup
    backup = filename + '.before_message_fix'
    with open(backup, 'w') as f:
        f.write(content)
    print(f"✅ Backup saved: {backup}")
    
    changes_made = 0
    
    # FIX 1: startConversation - handle data.data.message
    old_pattern_1 = r"(conversationState\.conversationStarted = true;)\s*\n\s*// Add AI's greeting message\s*\n\s*addMessage\('ai', data\.message \|\| \"[^\"]+\"\);"
    
    new_code_1 = r"""\1

                // Extract message from nested structure
                const greetingMessage = data.data?.message || data.message || "Hello! I'm your AI research assistant. Tell me about the clinical research study you'd like to create.";
                addMessage('ai', greetingMessage);"""
    
    if re.search(old_pattern_1, content):
        content = re.sub(old_pattern_1, new_code_1, content)
        changes_made += 1
        print("✅ Fixed startConversation()")
    
    # FIX 2: sendMessage - handle data.data.message
    old_pattern_2 = r"(const data = await response\.json\(\);)\s*\n\s*// Add AI's response\s*\n\s*addMessage\('ai', data\.message\);\s*\n\s*// Check if study is ready to generate\s*\n\s*if \(data\.ready_to_generate \|\| data\.message\.toLowerCase\(\)\.includes\('ready to generate'\)\)"
    
    new_code_2 = r"""\1
                
                // Extract message from nested structure (FIXED!)
                const aiMessage = data.data?.message || data.message || "I received your message.";
                addMessage('ai', aiMessage);
                
                // Check if study is ready to generate
                const readyToGenerate = data.data?.ready_to_generate || data.ready_to_generate || false;
                if (readyToGenerate || aiMessage.toLowerCase().includes('ready to generate'))"""
    
    if re.search(old_pattern_2, content):
        content = re.sub(old_pattern_2, new_code_2, content)
        changes_made += 1
        print("✅ Fixed sendMessage()")
    
    # FIX 3: generateStudy - handle nested study data
    old_pattern_3 = r"(const data = await response\.json\(\);)\s*\n\s*if \(data\.success\) \{\s*\n\s*conversationState\.studyGenerated = true;\s*\n\s*conversationState\.generatedStudyId = data\.study_id;"
    
    new_code_3 = r"""\1

                // Handle nested response structure (FIXED!)
                const studyData = data.data || data;
                
                if (data.status === 'success' || data.success || studyData.success) {
                    conversationState.studyGenerated = true;
                    conversationState.generatedStudyId = studyData.study_id || studyData.database_study_id;"""
    
    if re.search(old_pattern_3, content):
        content = re.sub(old_pattern_3, new_code_3, content)
        changes_made += 1
        print("✅ Fixed generateStudy()")
    
    # Write fixed content
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"\n🎉 SUCCESS! Made {changes_made} fixes to {filename}")
    print(f"📁 Original backed up to: {backup}")
    print(f"\n🔄 Refresh your browser (Cmd+R) to see the changes!")
    print(f"🧪 Test by typing: 'track pain twice daily'")
    
    return changes_made > 0

if __name__ == "__main__":
    import os
    
    # Check if file exists
    if not os.path.exists('design-studio.html'):
        print("❌ Error: design-studio.html not found!")
        print("💡 Run this script from your frontend/ directory")
        sys.exit(1)
    
    try:
        if fix_design_studio():
            print("\n✅ All fixes applied successfully!")
        else:
            print("\n⚠️ No changes made - patterns not found")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
