with open('main.py', 'r') as f:
    content = f.read()

# Find and replace the conversation/message endpoint
old_endpoint = '''@app.post("/api/v1/conversation/message")
async def send_conversation_message(
    message: dict
):
    """Send a message in the conversation"""
    try:
        msg = message.get("message", "")
        
        if not msg:
            raise HTTPException(status_code=400, detail="Message is required")
        
        user_id = message.get("user_id", "anonymous_user")
        result = conversation_manager.send_message(user_id, msg)
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''

new_endpoint = '''@app.post("/api/v1/conversation/message")
async def send_conversation_message(
    message: dict
):
    """Send a message in the conversation"""
    try:
        print(f"🔍 Received conversation message request: {message}")
        
        msg = message.get("message", "")
        
        if not msg:
            raise HTTPException(status_code=400, detail="Message is required")
        
        user_id = message.get("user_id", "anonymous_user")
        print(f"📤 Sending message to conversation_manager for user: {user_id}")
        print(f"💬 Message: {msg}")
        
        result = conversation_manager.send_message(user_id, msg)
        
        print(f"✅ Conversation manager returned: {result}")
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ ERROR in send_conversation_message: {str(e)}")
        print(f"   Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))'''

if old_endpoint in content:
    content = content.replace(old_endpoint, new_endpoint)
    with open('main.py', 'w') as f:
        f.write(content)
    print("✅ Added comprehensive error logging to conversation/message endpoint")
else:
    print("⚠️ Could not find exact endpoint - may need manual edit")

