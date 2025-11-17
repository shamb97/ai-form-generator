"""
Agent Adapter
Adapts existing agent APIs to work with LangGraph orchestrator
"""

from typing import Dict, List, Any
from .agents.form_designer_agent import FormDesignerAgent
from .agents.schedule_optimizer_agent import ScheduleOptimizerAgent
from .agents.policy_recommender_agent import PolicyRecommenderAgent
from .agents.clinical_compliance_agent import ClinicalComplianceAgent
from .agents.reflection_qa_agent import ReflectionQAAgent


class AdaptedFormDesigner:
    """Adapts FormDesignerAgent for orchestrator"""
    
    def __init__(self):
        self.agent = FormDesignerAgent()
    
    def generate_forms(self, description: str, study_type: str) -> Dict:
        """Generate forms from description"""
        # Call the actual design_form method
        result = self.agent.design_form(description)
        
        # Ensure form has 'form_name' key for scheduler
        if isinstance(result, dict):
            if 'form_name' not in result and 'title' in result:
                result['form_name'] = result['title']
            elif 'form_name' not in result and 'form_id' in result:
                result['form_name'] = result['form_id']
            elif 'form_name' not in result:
                result['form_name'] = "Generated Form"
            
            # Add default frequency if missing
            if 'frequency' not in result:
                result['frequency'] = 1  # default to daily
        
        # Wrap in expected format
        return {
            "forms": [result] if isinstance(result, dict) else [],
            "study_config": {
                "description": description,
                "study_type": study_type
            }
        }


class AdaptedScheduleOptimizer:
    """Adapts ScheduleOptimizerAgent for orchestrator"""
    
    def __init__(self):
        self.agent = ScheduleOptimizerAgent()
    
    def optimize_schedule(self, forms: List[Dict], study_config: Dict) -> Dict:
        """Optimize schedule for forms"""
        # Extract duration from config or default to 30 days
        duration = study_config.get("duration", 30)
        
        # Call actual optimize_schedule method
        return self.agent.optimize_schedule(forms, duration)


class AdaptedPolicyRecommender:
    """Adapts PolicyRecommenderAgent for orchestrator"""
    
    def __init__(self):
        self.agent = PolicyRecommenderAgent()
    
    def recommend_policies(self, forms: List[Dict], study_type: str) -> Dict:
        """Recommend policies for forms"""
        all_policies = []
        
        # Get policies for each form
        for form in forms:
            policies = self.agent.recommend_policies(form)
            all_policies.append(policies)
        
        return {
            "policies": all_policies,
            "study_type": study_type
        }


class AdaptedClinicalCompliance:
    """Adapts ClinicalComplianceAgent for orchestrator"""
    
    def __init__(self):
        self.agent = ClinicalComplianceAgent()
    
    def check_compliance(self, forms: List[Dict], study_config: Dict) -> Dict:
        """Check clinical compliance"""
        # Build study design from config
        study_design = {
            "description": study_config.get("description", ""),
            "forms": forms,
            "study_type": study_config.get("study_type", "clinical_trial")
        }
        
        # Call actual check_compliance method
        return self.agent.check_compliance(study_design, region="US")


class AdaptedReflectionQA:
    """Adapts ReflectionQAAgent for orchestrator"""
    
    def __init__(self):
        self.agent = ReflectionQAAgent()
    
    def validate(self, forms: List[Dict], schedule: Dict, study_config: Dict) -> Dict:
        """Validate complete study configuration"""
        # Combine everything into output for review
        output = {
            "forms": forms,
            "schedule": schedule,
            "study_config": study_config
        }
        
        # Call actual review_output method
        result = self.agent.review_output(
            agent_name="orchestrator",
            output=output,
            context=study_config.get("description", "")
        )
        
        # Extract score from result
        return {
            "score": result.get("quality_score", 7),
            "feedback": result.get("suggestions", []),
            "approved": result.get("quality_score", 7) >= 7
        }