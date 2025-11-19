with open('main.py', 'r') as f:
    content = f.read()

# Find the save logic section
old_logic = '''        # SAVE TO DATABASE! ← NEW SECTION
        if result.get('success') and result.get('forms'):'''

new_logic = '''        # SAVE TO DATABASE! ← NEW SECTION
        # Extract forms from orchestrator result (handle nested structure)
        forms_list = []
        if result.get('forms'):
            for item in result.get('forms', []):
                # Check if this item has nested 'forms' array
                if isinstance(item, dict) and 'forms' in item:
                    forms_list.extend(item['forms'])
                else:
                    forms_list.append(item)
        
        if forms_list and len(forms_list) > 0:'''

content = content.replace(old_logic, new_logic)

# Also update the reference to forms_list
old_forms = '''            forms_list = result.get('forms', [])'''
new_forms = '''            # forms_list already extracted above'''

content = content.replace(old_forms, new_forms)

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Fixed save parsing logic!")
print("Now handles both flat and nested form structures")
