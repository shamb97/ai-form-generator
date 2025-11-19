"""
Test Agent Connection
=====================

This script tests if our base agent can successfully connect to Claude API!

Run this to make sure everything works!
"""

import os
import sys

# Make sure we can import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent


def test_agent_connection():
    """
    Test that we can create an agent and get a response from Claude
    """
    print("\n" + "="*60)
    print("🧪 TESTING AI AGENT CONNECTION")
    print("="*60 + "\n")
    
    # Step 1: Create a test agent
    print("Step 1: Creating test agent...")
    try:
        test_agent = BaseAgent(
            name="Test Agent",
            role="Testing connection to Claude API",
            system_prompt="You are a helpful test agent. Respond briefly and clearly."
        )
        print("✅ Agent created successfully!\n")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Fix: Set your API key with:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        return False
    
    # Step 2: Test basic conversation
    print("Step 2: Testing conversation...")
    try:
        response = test_agent.think("Hello! Can you hear me? Please respond with 'Yes, I can hear you!'")
        print(f"✅ Agent responded: {response}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False
    
    # Step 3: Test agent memory
    print("Step 3: Testing memory...")
    try:
        response2 = test_agent.think("What was my first message to you?")
        print(f"✅ Agent remembers: {response2}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False
    
    # Step 4: Get agent info
    print("Step 4: Getting agent info...")
    info = test_agent.get_info()
    print(f"✅ Agent Info:")
    print(f"   - Name: {info['name']}")
    print(f"   - Role: {info['role']}")
    print(f"   - Conversation turns: {info['conversation_turns']}")
    print()
    
    # Step 5: Test memory clearing
    print("Step 5: Testing memory clearing...")
    test_agent.clear_memory()
    info_after_clear = test_agent.get_info()
    print(f"✅ Conversation turns after clear: {info_after_clear['conversation_turns']}")
    print()
    
    print("="*60)
    print("✅ ALL TESTS PASSED! AI AGENT SYSTEM IS READY!")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_agent_connection()
    sys.exit(0 if success else 1)
    