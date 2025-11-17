"""
Study Type Classifier
Intelligently determines study type from natural language description
Used by LangGraph orchestrator for intelligent agent routing
"""

import anthropic
import os
import json
from typing import Dict, Literal
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv('backend/.env')

StudyType = Literal["personal_tracker", "simple_survey", "clinical_trial"]

CLASSIFICATION_PROMPT = """You are a clinical research expert. Analyze the study description and classify it.

STUDY TYPES:

1. **personal_tracker**: Individual self-tracking
   - Keywords: "I want to track", "monitor my", "personal", "daily mood", "habit tracking"
   - Characteristics: Single user, simple tracking, minimal complexity
   - Examples: "Track my sleep quality", "Monitor my anxiety levels"

2. **simple_survey**: Survey or questionnaire research
   - Keywords: "survey", "questionnaire", "ask participants", "collect responses"
   - Characteristics: Multiple participants, one-time or repeated surveys, data collection
   - Examples: "Survey employees about job satisfaction", "Collect feedback from customers"

3. **clinical_trial**: Clinical research study
   - Keywords: "clinical trial", "phase", "patients", "treatment", "medication", "screening"
   - Characteristics: Multiple phases, medical compliance, complex protocols
   - Examples: "Phase 2 trial for diabetes drug", "Test new hypertension treatment"

DECISION RULES:
- If mentions "phase", "clinical", "trial", "treatment", "medication", "patients" → clinical_trial
- If mentions "survey", "questionnaire", multiple participants → simple_survey  
- If mentions "I", "my", "track", "monitor" for self → personal_tracker
- When ambiguous, prefer simpler classification

Analyze this study description:
{description}

Respond ONLY with valid JSON:
{{
    "study_type": "personal_tracker" | "simple_survey" | "clinical_trial",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "key_indicators": ["list", "of", "keywords"]
}}"""


class StudyClassifier:
    """Classifies study descriptions into types for intelligent routing"""
    
    def __init__(self):
        """Initialize classifier with Anthropic client"""
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
    
    def classify(self, description: str) -> Dict:
        """
        Classify a study description
        
        Args:
            description: Natural language study description
            
        Returns:
            Dictionary with:
            - study_type: One of "personal_tracker", "simple_survey", "clinical_trial"
            - confidence: Float 0-1
            - reasoning: String explanation
            - key_indicators: List of keywords that influenced decision
        """
        
        # Create the prompt
        prompt = CLASSIFICATION_PROMPT.format(description=description)
        
        # Call Claude
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            result_text = response.content[0].text.strip()
            
            # Handle markdown code blocks
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            
            # Validate study_type
            valid_types = ["personal_tracker", "simple_survey", "clinical_trial"]
            if result["study_type"] not in valid_types:
                raise ValueError(f"Invalid study type: {result['study_type']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            # Default to simple_survey as middle ground
            return {
                "study_type": "simple_survey",
                "confidence": 0.3,
                "reasoning": f"Error occurred: {str(e)}, defaulting to simple_survey",
                "key_indicators": []
            }
    
    def get_agent_requirements(self, study_type: StudyType) -> Dict:
        """
        Get which agents are needed for a study type
        
        Args:
            study_type: Classified study type
            
        Returns:
            Dictionary with agent requirements
        """
        
        requirements = {
            "personal_tracker": {
                "agents": ["form_designer", "schedule_optimizer"],
                "optional_agents": [],
                "requires_compliance": False,
                "requires_policies": False,
                "complexity": "low"
            },
            "simple_survey": {
                "agents": ["form_designer", "schedule_optimizer", "policy_recommender"],
                "optional_agents": ["reflection_qa"],
                "requires_compliance": False,
                "requires_policies": True,
                "complexity": "medium"
            },
            "clinical_trial": {
                "agents": ["form_designer", "schedule_optimizer", "policy_recommender", 
                          "clinical_compliance", "reflection_qa"],
                "optional_agents": [],
                "requires_compliance": True,
                "requires_policies": True,
                "complexity": "high"
            }
        }
        
        return requirements.get(study_type, requirements["simple_survey"])


def test_classifier():
    """Test the classifier with sample descriptions"""
    
    classifier = StudyClassifier()
    
    test_cases = [
        "I want to track my mood daily for the next 30 days",
        "Survey employees about workplace satisfaction once a week for 2 months",
        "Phase 2 clinical trial for new hypertension medication with screening, baseline, treatment, and follow-up phases"
    ]
    
    for i, description in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}")
        print('='*60)
        print(f"Description: {description}\n")
        
        result = classifier.classify(description)
        requirements = classifier.get_agent_requirements(result["study_type"])
        
        print(f"📊 Classification Results:")
        print(f"   Type: {result['study_type']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Reasoning: {result['reasoning']}")
        print(f"   Key Indicators: {', '.join(result['key_indicators'])}")
        
        print(f"\n🤖 Agent Requirements:")
        print(f"   Required Agents: {len(requirements['agents'])}")
        print(f"   Agents: {', '.join(requirements['agents'])}")
        print(f"   Complexity: {requirements['complexity']}")
        
        input("\n👉 Press Enter to continue to next test...")


if __name__ == "__main__":
    print("\n🚀 Testing Study Classifier...\n")
    test_classifier()
    print("\n✅ All tests complete!\n")