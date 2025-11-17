"""
Form Designer Agent
===================

This agent converts natural language descriptions into JSON form schemas!

Example:
  Input: "I need a daily mood tracker with happiness scale and sleep quality"
  Output: Complete JSON form with proper field types, validation, etc.

NOW WITH EDGE CASE HANDLING:
  - Detects ambiguous phase descriptions
  - Asks clarifying questions when needed
  - Handles time-based requirements intelligently
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
    from agents.metadata_validator import MetadataEdgeCaseHandler
else:
    # Running as module - use relative import
    from .base_agent import BaseAgent
    from .metadata_validator import MetadataEdgeCaseHandler


class FormDesignerAgent(BaseAgent):
    """
    Specialized agent for designing clinical research forms
    
    Converts researcher descriptions into structured JSON forms
    WITH intelligent edge case handling!
    """
    
    def __init__(self):
        system_prompt = """You are an expert clinical research form designer with metadata intelligence. Convert the user's description into a valid JSON response with TWO parts:
1. Clean form schema (research questions ONLY - NO metadata fields)
2. Intelligent metadata suggestions (captured programmatically, NOT as form fields)

OUTPUT RULES:
1. Return ONLY valid JSON - no markdown, no explanations, no code blocks
2. Follow this EXACT structure:

{
  "study_classification": {
    "study_type": "clinical_trial|observational_study|survey|personal_tracker",
    "risk_level": "high|medium|low",
    "has_phases": true,
    "phase_names": ["Screening", "Treatment", "Follow-up"],
    "recommended_tier": 3
  },
  "form_schema": {
    "form_id": "lowercase_with_underscores",
    "form_name": "Human Readable Name",
    "description": "Brief description",
    "fields": [
      {
        "field_id": "field_name",
        "field_name": "Question Label",
        "field_type": "text|number|radio|checkbox|date|time|scale|textarea",
        "description": "What this measures",
        "required": true,
        "validation": {"min": 0, "max": 10},
        "options": ["Option 1", "Option 2"]
      }
    ]
  },
  "metadata_suggestions": {
    "required": [
      {
        "field": "submission_timestamp",
        "why": "Essential for tracking when data was collected",
        "how": "Auto-captured on form submission",
        "privacy": "Timestamp only, no personal identifiers"
      }
    ],
    "recommended": [
      {
        "field": "study_day",
        "why": "Tracks progress through study timeline",
        "how": "Calculated from enrollment date",
        "example": "Day 15 of 30",
        "user_benefit": "See your progress through the study"
      }
    ],
    "optional": [
      {
        "field": "device_type",
        "why": "Helps identify if device affects data quality",
        "how": "Detected from browser",
        "example": "iPhone 14, Chrome Browser",
        "privacy": "Device model only, no unique identifiers",
        "user_choice": true
      }
    ]
  }
}

CRITICAL RULES:
1. NEVER add metadata fields to form_schema.fields[] - metadata is captured programmatically
2. Do NOT create fields like "Assessment Date", "Study Day", "Phase", "Completion Time"
3. form_schema.fields[] should ONLY contain actual research/clinical questions
4. Classify study type based on description keywords
5. Recommend metadata tier: 1 (minimal), 2 (scientific), 3 (clinical trial), 4 (regulated)

STUDY TYPE CLASSIFICATION:
- "clinical_trial": Mentions phases, interventions, baseline, treatment, follow-up, regulatory
- "observational_study": Mentions tracking, monitoring, cohort, longitudinal
- "survey": Mentions survey, questionnaire, one-time, feedback
- "personal_tracker": Mentions "my", "personal", "track myself", daily habits

METADATA TIERS:
- Tier 1 (Personal Tracker): submission_timestamp only
- Tier 2 (Survey/Study): + study_day, form_version
- Tier 3 (Clinical Trial): + phase_name, visit_number, compliance_window
- Tier 4 (Regulated): + audit_trail, device_info, geolocation (with consent)

IMPORTANT: Output ONLY the JSON, nothing else! No markdown code blocks, no ```json markers!"""
        
        super().__init__(
            name="Form Designer Agent",
            role="Converts natural language to JSON form schemas",
            system_prompt=system_prompt
        )
        
        # Initialize the edge case validator
        self.validator = MetadataEdgeCaseHandler()
        print("✅ Form Designer Agent initialized with Edge Case Validator")
    
    def design_form(self, description: str) -> Dict[str, Any]:
        """
        Design a form from natural language description
        
        NOW WITH EDGE CASE VALIDATION!
        
        Args:
            description: What the researcher wants (e.g., "daily mood tracker")
            
        Returns:
            Dictionary containing the form schema + any clarification questions
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
            form_data = json.loads(response_clean)
            
            # NEW: Validate and enhance with edge case handler
            if "study_classification" in form_data:
                print("🔍 Running edge case validation...")
                
                enhanced_classification = self.validator.validate_and_enhance_metadata(
                    form_data["study_classification"],
                    description
                )
                
                # Update the classification with enhanced version
                form_data["study_classification"] = enhanced_classification
                
                # Check for time-sensitive requirements
                time_requirements = self.validator.detect_time_sensitive_requirements(description)
                if time_requirements.get("has_time_requirements"):
                    print(f"⏰ Detected time requirements: {time_requirements['requirements']}")
                    form_data["time_requirements"] = time_requirements
            
            # Get form name for logging
            form_name = "Unknown"
            if "form_schema" in form_data:
                form_name = form_data["form_schema"].get("form_name", "Unknown")
            elif "form_name" in form_data:
                form_name = form_data.get("form_name", "Unknown")
            
            print(f"✅ Form created: {form_name}")
            
            # Count fields
            field_count = 0
            if "form_schema" in form_data and "fields" in form_data["form_schema"]:
                field_count = len(form_data["form_schema"]["fields"])
            elif "fields" in form_data:
                field_count = len(form_data["fields"])
            
            print(f"   Fields: {field_count}")
            
            # Check if clarification is needed
            if enhanced_classification.get("needs_clarification"):
                print("❓ Clarification needed from user")
            
            return form_data
            
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
            
            # Check if AI returned full structure or just form fields
            if "form_schema" in updated_schema:
                # AI returned full structure - use it but preserve original metadata
                result = {
                    "form_schema": updated_schema.get("form_schema"),
                    "metadata_suggestions": form_schema.get("metadata_suggestions", {}),
                    "study_classification": form_schema.get("study_classification", {})
                }
            else:
                # AI returned just form fields - wrap it properly
                result = {
                    "form_schema": updated_schema,
                    "metadata_suggestions": form_schema.get("metadata_suggestions", {}),
                    "study_classification": form_schema.get("study_classification", {})
                }
            return result
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing refined JSON: {e}")
            return form_schema  # Return original if refinement failed


# Test the agent if run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING FORM DESIGNER AGENT WITH EDGE CASE VALIDATION")
    print("="*60)
    
    # Create the agent
    designer = FormDesignerAgent()
    
    # Test 1: Simple form (no edge cases)
    print("\n--- Test 1: Simple Daily Mood Tracker ---")
    mood_form = designer.design_form(
        "A simple daily mood tracker with happiness scale 1-10 and sleep quality"
    )
    print("\nResult (classification):")
    if "study_classification" in mood_form:
        print(json.dumps(mood_form["study_classification"], indent=2))
    
    # Test 2: Ambiguous single phase
    print("\n\n--- Test 2: Ambiguous Phase Detection ---")
    phase_form = designer.design_form(
        "30-day mindfulness tracker during my Awakening Phase"
    )
    print("\nResult (classification):")
    if "study_classification" in phase_form:
        classification = phase_form["study_classification"]
        print(json.dumps(classification, indent=2))
        if classification.get("needs_clarification"):
            print("\n⚠️ NEEDS CLARIFICATION:")
            print(f"Question: {classification.get('clarification_question')}")
    
    # Test 3: Multiple phases
    print("\n\n--- Test 3: Multiple Phases ---")
    trial_form = designer.design_form(
        "Clinical trial with baseline, treatment, and follow-up phases"
    )
    print("\nResult (classification):")
    if "study_classification" in trial_form:
        print(json.dumps(trial_form["study_classification"], indent=2))
    
    # Test 4: Time requirements
    print("\n\n--- Test 4: Time-Based Requirements ---")
    time_form = designer.design_form(
        "Daily check-in after 7pm for 25 days"
    )
    print("\nResult (time requirements):")
    if "time_requirements" in time_form:
        print(json.dumps(time_form["time_requirements"], indent=2))
    
    print("\n" + "="*60)
    print("✅ FORM DESIGNER AGENT TEST COMPLETE!")
    print("="*60 + "\n")