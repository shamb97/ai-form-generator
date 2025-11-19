with open('design-studio.html', 'r') as f:
    content = f.read()

# Find and fix the trigger condition
old_line = "if (message.toLowerCase().includes('yes') || message.toLowerCase().includes('generate'))"
new_line = "if (message.toLowerCase().includes('yes') || message.toLowerCase().includes('generate') || message.toLowerCase().includes('create'))"

if old_line in content:
    content = content.replace(old_line, new_line)
    with open('design-studio.html', 'w') as f:
        f.write(content)
    print("✅ Fixed! Now 'create study' will trigger generation!")
else:
    print("⚠️ Line not found")
