"""
Form Designer Agent
===================

This agent converts natural language descriptions into JSON form schemas!

Example:
  Input: "I need a daily mood tracker with happiness scale and sleep quality"
  Output: Complete JSON form with proper field types, validation, etc.
"""

from typing import Dict, Any
import json
import sys
import os

# Handle imports whether running as module or script
if __name__ == "__main__":
    # Running as script - add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agents.base_agent import BaseAgent
else:
    # Running as module - use relative import
    from .base_agent import BaseAgent


class FormDesignerAgent(BaseAgent):
    """
    Specialized agent for designing clinical research forms
    
    Converts researcher descriptions into structured JSON forms
    """
    
    def __init__(self):
        system_prompt = """You are an expert clinical research form designer.

Your job is to convert natural language descriptions into valid JSON form schemas.

RULES:
1. ALWAYS output valid JSON only - no explanations before or after
2. Use these field types: text, number, radio, checkbox, date, time, scale, textarea
3. Include proper validation rules
4. Add helpful descriptions for each field
5. Consider clinical research best practices

OUTPUT FORMAT (JSON only):
{
  "form_id": "unique_id",
  "form_name": "Form Name",
  "description": "What this form measures",
  "fields": [
    {
      "field_id": "field_1",
      "field_name": "Field Name",
      "field_type": "text|number|radio|checkbox|date|time|scale|textarea",
      "description": "What this field measures",
      "required": true,
      "validation": {
        "min": 0,
        "max": 10
      },
      "options": ["option1", "option2"]
    }
  ]
}

IMPORTANT: Output ONLY the JSON, nothing else! No markdown code blocks, no ```json markers!"""
        
        super().__init__(
            name="Form Designer Agent",
            role="Converts natural language to JSON form schemas",
            system_prompt=system_prompt
        )
    
    def design_form(self, description: str) -> Dict[str, Any]:
        """
        Design a form from natural language description
        
        Args:
            description: What the researcher wants (e.g., "daily mood tracker")
            
        Returns:
            Dictionary containing the form schema
        """
        print(f"\n🎨 Designing form from: '{description}'...")
        
        # Ask the agent to design the form
        response = self.think(f"Design a clinical research form for: {description}")
        
        try:
            # Clean the response (remove markdown code blocks if present)
            response_clean = response.strip()
            
            # Remove markdown code blocks
            if response_clean.startswith("```"):
                lines = response_clean.split("\n")
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_clean = "\n".join(lines).strip()
            
            # Parse the JSON response
            form_schema = json.loads(response_clean)
            print(f"✅ Form created: {form_schema.get('form_name', 'Unknown')}")
            print(f"   Fields: {len(form_schema.get('fields', []))}")
            return form_schema
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            print(f"Response was: {response[:200]}...")
            return {
                "error": "Failed to parse form schema",
                "raw_response": response
            }
    
    def refine_form(self, form_schema: Dict[str, Any], refinement: str) -> Dict[str, Any]:
        """
        Refine an existing form based on feedback
        
        Args:
            form_schema: The current form schema
            refinement: What to change (e.g., "add age field")
            
        Returns:
            Updated form schema
        """
        print(f"\n🔧 Refining form: '{refinement}'...")
        
        prompt = f"""Here's the current form:
{json.dumps(form_schema, indent=2)}

Please modify it to: {refinement}

Output the complete updated JSON form. No markdown code blocks!"""
        
        response = self.think(prompt)
        
        try:
            # Clean the response
            response_clean = response.strip()
            if response_clean.startswith("```"):
                lines = response_clean.split("\n")
                lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_clean = "\n".join(lines).strip()
            
            updated_schema = json.loads(response_clean)
            print(f"✅ Form refined successfully!")
            return updated_schema
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing refined JSON: {e}")
            return form_schema  # Return original if refinement failed


# Test the agent if run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING FORM DESIGNER AGENT")
    print("="*60)
    
    # Create the agent
    designer = FormDesignerAgent()
    
    # Test 1: Simple form
    print("\n--- Test 1: Simple Daily Mood Tracker ---")
    mood_form = designer.design_form(
        "A simple daily mood tracker with happiness scale 1-10 and sleep quality"
    )
    print("\nResult:")
    print(json.dumps(mood_form, indent=2))
    
    # Test 2: Refine the form
    print("\n--- Test 2: Add a field ---")
    refined_form = designer.refine_form(
        mood_form,
        "Add a text field for notes about the day"
    )
    print("\nRefined Result:")
    print(json.dumps(refined_form, indent=2))
    
    print("\n" + "="*60)
    print("✅ FORM DESIGNER AGENT TEST COMPLETE!")
    print("="*60 + "\n")