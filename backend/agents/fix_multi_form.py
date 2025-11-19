import re

with open('form_designer_agent.py', 'r') as f:
    content = f.read()

# Backup
with open('form_designer_agent.py.before_multifix', 'w') as f:
    f.write(content)
print("✅ Backup created")

# Find and update the system prompt
old_instruction = '"form_schema": {'

new_instruction = '''IMPORTANT: If the description mentions MULTIPLE distinct tracking needs, frequencies, or purposes, create MULTIPLE forms!

Examples requiring multiple forms:
- "Daily X and weekly Y" → 2 forms (different frequencies)
- "Track A and track B" → 2 forms (different purposes)

When creating multiple forms, use this structure:
{
  "study_classification": {...},
  "forms": [
    {"form_schema": {...}, "frequency_days": 1},
    {"form_schema": {...}, "frequency_days": 7}
  ],
  "metadata_suggestions": {...}
}

For a SINGLE form, use original structure.

"form_schema": {'''

content = content.replace(old_instruction, new_instruction, 1)

# Update return handling
old_return = '            return form_data'
new_return = '''            # Handle both single form and multiple forms
            if "forms" in form_data:
                print(f"   Created {len(form_data['forms'])} forms")
            
            return form_data'''

content = content.replace(old_return, new_return)

with open('form_designer_agent.py', 'w') as f:
    f.write(content)

print("✅ Multi-form support added!")
