import sys

# Read the file
with open('main.py', 'r') as f:
    content = f.read()

# Find the list_studies function and add debug print
old_code = '''    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "studies": []
        }'''

new_code = '''    except Exception as e:
        print(f"❌ ERROR in list_studies: {e}")
        print(f"   Type: {type(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "studies": []
        }'''

content = content.replace(old_code, new_code)

# Write back
with open('main.py', 'w') as f:
    f.write(content)

print("✅ Debug logging added to list_studies endpoint")
