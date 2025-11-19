import re

with open('database.py', 'r') as f:
    content = f.read()

# Find the Study class and check if status already exists
if 'status = Column' in content:
    print("✅ Status field already in Study model!")
else:
    print("📝 Adding status field to Study model...")
    
    # Find the Study class definition
    old_pattern = r'(class Study\(Base\):.*?created_at = Column\(DateTime, default=datetime\.utcnow\))'
    
    replacement = r'\1\n    status = Column(String, default="draft")  # draft, active, archived'
    
    content = re.sub(old_pattern, replacement, content, flags=re.DOTALL)
    
    with open('database.py', 'w') as f:
        f.write(content)
    
    print("✅ Status field added to Study model!")
    print("   Statuses: draft → active → archived")

print("\n💡 Study lifecycle:")
print("   draft    → Can edit everything")
print("   active   → Locked (subjects enrolled)")
print("   archived → Soft deleted")
