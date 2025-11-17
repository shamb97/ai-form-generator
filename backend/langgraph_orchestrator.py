"""
LangGraph Orchestrator
Coordinates multiple AI agents to create complete study configurations
Uses intelligent routing based on study type classification
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Annotated
import operator
from study_classifier import StudyClassifier
import sys
import os

# Import agents using absolute imports
from agent_adapter import (
    AdaptedFormDesigner,
    AdaptedScheduleOptimizer,
    AdaptedPolicyRecommender,
    AdaptedClinicalCompliance,
    AdaptedReflectionQA
)


class StudyState(TypedDict):
    """State passed between agents in the workflow"""
    # Input
    description: str
    study_type: str
    study_config: Dict
    
    # Agent outputs (accumulated)
    messages: Annotated[List[str], operator.add]
    forms: List[Dict]
    schedule: Dict
    policies: Dict
    compliance_check: Dict
    quality_score: Dict
    
    # Workflow control
    agents_used: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    complete: bool


class LangGraphOrchestrator:
    """Orchestrates multiple AI agents using LangGraph state machine"""
    
    def __init__(self):
        """Initialize orchestrator with all agents"""
        print("🚀 Initializing LangGraph Orchestrator...")
        
        # Initialize classifier
        self.classifier = StudyClassifier()
        
        # Initialize all agents (using adapters)
        print("  → Loading Form Designer Agent...")
        self.form_designer = AdaptedFormDesigner()
        
        print("  → Loading Schedule Optimizer Agent...")
        self.scheduler = AdaptedScheduleOptimizer()
        
        print("  → Loading Policy Recommender Agent...")
        self.policy_agent = AdaptedPolicyRecommender()
        
        print("  → Loading Clinical Compliance Agent...")
        self.compliance_agent = AdaptedClinicalCompliance()
        
        print("  → Loading Reflection QA Agent...")
        self.qa_agent = AdaptedReflectionQA()
        
        # Build the graph
        self.workflow = self._build_graph()
        print("✅ Orchestrator ready!\n")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        
        # Create graph
        graph = StateGraph(StudyState)
        
        # Add nodes (agents)
        graph.add_node("classify", self._classify_study)
        graph.add_node("design_forms", self._design_forms)
        graph.add_node("optimize_schedule", self._optimize_schedule)
        graph.add_node("recommend_policies", self._recommend_policies)
        graph.add_node("check_compliance", self._check_compliance)
        graph.add_node("quality_assurance", self._quality_assurance)
        
        # Define edges (workflow)
        graph.set_entry_point("classify")
        
        # All paths start with classification
        graph.add_edge("classify", "design_forms")
        
        # All paths go through form design and schedule
        graph.add_edge("design_forms", "optimize_schedule")
        
        # Route after scheduling based on study type
        graph.add_conditional_edges(
            "optimize_schedule",
            self._route_after_scheduling,
            {
                "policies": "recommend_policies",
                "compliance": "check_compliance",
                "qa": "quality_assurance",
                "end": END
            }
        )
        
        # From policies, go to compliance or QA or end
        graph.add_conditional_edges(
            "recommend_policies",
            self._route_after_policies,
            {
                "compliance": "check_compliance",
                "qa": "quality_assurance",
                "end": END
            }
        )
        
        # From compliance, go to QA or end
        graph.add_conditional_edges(
            "check_compliance",
            self._route_after_compliance,
            {
                "qa": "quality_assurance",
                "end": END
            }
        )
        
        # QA is always the last step
        graph.add_edge("quality_assurance", END)
        
        return graph.compile()
    
    def _classify_study(self, state: StudyState) -> StudyState:
        """Step 1: Classify the study type"""
        print("\n" + "="*60)
        print("🔍 STEP 1: Classifying study type...")
        
        result = self.classifier.classify(state["description"])
        state["study_type"] = result["study_type"]
        state["messages"].append(f"Classified as: {result['study_type']}")
        
        requirements = self.classifier.get_agent_requirements(result["study_type"])
        print(f"   Type: {result['study_type']}")
        print(f"   Agents needed: {len(requirements['agents'])}")
        
        return state
    
    def _design_forms(self, state: StudyState) -> StudyState:
        """Step 2: Design forms using Form Designer Agent"""
        print("\n🎨 STEP 2: Designing forms...")
        
        try:
            # Use form designer agent
            result = self.form_designer.generate_forms(
                description=state["description"],
                study_type=state["study_type"]
            )
            
            state["forms"] = result.get("forms", [])
            state["study_config"] = result.get("study_config", {})
            state["messages"].append(f"Created {len(state['forms'])} forms")
            state["agents_used"].append("form_designer")
            
            print(f"   Created {len(state['forms'])} forms")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            state["errors"].append(f"Form design error: {str(e)}")
        
        return state
    
    def _optimize_schedule(self, state: StudyState) -> StudyState:
        """Step 3: Optimize schedule using Schedule Optimizer"""
        print("\n📅 STEP 3: Optimizing schedule...")
        
        try:
            # Use schedule optimizer agent
            result = self.scheduler.optimize_schedule(
                forms=state["forms"],
                study_config=state["study_config"]
            )
            
            state["schedule"] = result
            state["messages"].append(f"LCM: {result.get('lcm_days', 'N/A')} days")
            state["agents_used"].append("schedule_optimizer")
            
            print(f"   LCM: {result.get('lcm_days', 'N/A')} days")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            state["errors"].append(f"Schedule error: {str(e)}")
        
        return state
    
    def _recommend_policies(self, state: StudyState) -> StudyState:
        """Step 4: Recommend policies using Policy Recommender"""
        print("\n📋 STEP 4: Recommending policies...")
        
        try:
            # Use policy recommender agent
            result = self.policy_agent.recommend_policies(
                forms=state["forms"],
                study_type=state["study_type"]
            )
            
            state["policies"] = result
            state["messages"].append(f"Policies: {len(result.get('policies', []))} recommended")
            state["agents_used"].append("policy_recommender")
            
            print(f"   Policies: {len(result.get('policies', []))} recommended")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            state["errors"].append(f"Policy error: {str(e)}")
        
        return state
    
    def _check_compliance(self, state: StudyState) -> StudyState:
        """Step 5: Check compliance using Clinical Compliance Agent"""
        print("\n🏥 STEP 5: Checking clinical compliance...")
        
        try:
            # Use compliance agent
            result = self.compliance_agent.check_compliance(
                forms=state["forms"],
                study_config=state["study_config"]
            )
            
            state["compliance_check"] = result
            state["messages"].append(f"Compliance: {result.get('status', 'unknown')}")
            state["agents_used"].append("clinical_compliance")
            
            print(f"   Status: {result.get('status', 'unknown')}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            state["errors"].append(f"Compliance error: {str(e)}")
        
        return state
    
    def _quality_assurance(self, state: StudyState) -> StudyState:
        """Step 6: Quality assurance using Reflection QA Agent"""
        print("\n✅ STEP 6: Quality assurance check...")
        
        try:
            # Use QA agent
            result = self.qa_agent.validate(
                forms=state["forms"],
                schedule=state["schedule"],
                study_config=state["study_config"]
            )
            
            state["quality_score"] = result
            state["messages"].append(f"Quality: {result.get('score', 0)}/10")
            state["agents_used"].append("reflection_qa")
            state["complete"] = True
            
            print(f"   Score: {result.get('score', 0)}/10")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            state["errors"].append(f"QA error: {str(e)}")
            state["complete"] = False
        
        return state
    
    def _route_after_scheduling(self, state: StudyState) -> str:
        """Decide next step after scheduling based on study type"""
        requirements = self.classifier.get_agent_requirements(state["study_type"])
        
        # Personal tracker: skip to QA (or end if no QA)
        if state["study_type"] == "personal_tracker":
            return "qa" if "reflection_qa" in requirements["optional_agents"] else "end"
        
        # Simple survey: go to policies
        if state["study_type"] == "simple_survey":
            return "policies"
        
        # Clinical trial: go to policies (which will then route to compliance)
        if state["study_type"] == "clinical_trial":
            return "policies"
        
        return "end"
    
    def _route_after_policies(self, state: StudyState) -> str:
        """Decide next step after policies based on study type"""
        
        # Clinical trial: needs compliance
        if state["study_type"] == "clinical_trial":
            return "compliance"
        
        # Simple survey: skip to QA
        if state["study_type"] == "simple_survey":
            return "qa"
        
        return "end"
    
    def _route_after_compliance(self, state: StudyState) -> str:
        """Decide next step after compliance - always go to QA for clinical trials"""
        return "qa"
    
    def create_study(self, description: str) -> Dict:
        """
        Create a complete study configuration from natural language description
        
        Args:
            description: Natural language study description
            
        Returns:
            Complete study configuration with forms, schedule, policies, etc.
        """
        
        print("\n" + "="*60)
        print("🚀 STARTING MULTI-AGENT ORCHESTRATION")
        print("="*60)
        
        # Initialize state
        initial_state: StudyState = {
            "description": description,
            "study_type": "",
            "study_config": {},
            "messages": [],
            "forms": [],
            "schedule": {},
            "policies": {},
            "compliance_check": {},
            "quality_score": {},
            "agents_used": [],
            "errors": [],
            "complete": False
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        print("\n" + "="*60)
        print("🎉 Workflow complete!")
        print("="*60)
        print(f"✅ ORCHESTRATION COMPLETE")
        print("="*60)
        
        return {
            "success": final_state["complete"],
            "study_type": final_state["study_type"],
            "agents_used": final_state["agents_used"],
            "forms": final_state["forms"],
            "schedule": final_state["schedule"],
            "policies": final_state.get("policies", {}),
            "compliance": final_state.get("compliance_check", {}),
            "quality": final_state.get("quality_score", {}),
            "messages": final_state["messages"]
        }


# Test function
def test_orchestrator():
    """Test the orchestrator with different study types"""
    orchestrator = LangGraphOrchestrator()
    
    test_cases = [
        "I want to track my mood daily for 30 days",
        "Survey employees about workplace satisfaction weekly for 2 months",
        "Phase 2 clinical trial for hypertension medication with screening, baseline, treatment, and follow-up phases"
    ]
    
    for i, description in enumerate(test_cases, 1):
        print(f"\n\n{'='*60}")
        print(f"TEST CASE {i}")
        print('='*60)
        print(f"Description: {description}\n")
        
        result = orchestrator.create_study(description)
        
        print(f"\n📊 RESULTS:")
        print(f"   Success: {result['success']}")
        print(f"   Study Type: {result['study_type']}")
        print(f"   Agents Used: {len(result['agents_used'])}")
        print(f"   Forms Created: {len(result['forms'])}")
        print(f"   Messages: {len(result['messages'])}")
        
        input("\n👉 Press Enter to continue to next test case...")


if __name__ == "__main__":
    test_orchestrator()