"""
Reflection & QA Agent
=====================

This agent provides quality control and catches errors!

It reviews outputs from other agents and checks for:
- Logical inconsistencies
- Missing information
- Potential errors
- Quality issues
"""

from typing import Dict, Any, List
import json
import sys
import os

# Handle imports whether running as module or script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agents.base_agent import BaseAgent
else:
    from .base_agent import BaseAgent


class ReflectionQAAgent(BaseAgent):
    """
    Specialized agent for quality assurance and error detection
    
    Acts as the "second pair of eyes" to catch issues
    """
    
    def __init__(self):
        system_prompt = """You are an expert quality assurance reviewer for clinical research systems.

Your job is to critically review outputs from other AI agents and identify:
1. Logical inconsistencies
2. Missing required information
3. Potential errors or edge cases
4. Quality issues
5. Improvement opportunities

RULES:
- Be thorough and critical
- Don't assume - verify everything
- Think about edge cases and failure modes
- Provide specific, actionable feedback
- ALWAYS output valid JSON only - NO markdown code blocks

OUTPUT FORMAT (raw JSON only):
{
  "quality_score": number (0-100),
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "logic|data|compliance|usability|other",
      "issue": "what's wrong",
      "location": "where the issue is",
      "recommendation": "how to fix it"
    }
  ],
  "strengths": ["what was done well"],
  "improvements": ["specific suggestions for improvement"],
  "approval_status": "approved|needs_revision|rejected",
  "overall_assessment": "summary of quality review"
}

CRITICAL: Output ONLY raw JSON, no markdown formatting!"""
        
        super().__init__(
            name="Reflection & QA Agent",
            role="Quality assurance and error detection",
            system_prompt=system_prompt
        )
    
    def _clean_json_response(self, response: str) -> str:
        """Clean up JSON response - remove markdown code blocks"""
        response_clean = response.strip()
        if response_clean.startswith("```"):
            lines = response_clean.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_clean = "\n".join(lines)
        return response_clean.strip()
    
    def review_output(
        self, 
        agent_name: str,
        output: Dict[str, Any],
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Review output from another agent
        
        Args:
            agent_name: Which agent produced this output
            output: The output to review
            context: Additional context for the review
            
        Returns:
            Quality assessment report
        """
        print(f"\n🔍 Reviewing output from {agent_name}...")
        
        prompt = f"""Review this output from the {agent_name}:

OUTPUT:
{json.dumps(output, indent=2)}

{f'CONTEXT: {context}' if context else ''}

Provide a thorough quality assessment checking for:
1. Logical consistency
2. Completeness
3. Accuracy
4. Edge cases
5. Potential issues

Remember: Output ONLY raw JSON, no markdown!"""
        
        response = self.think(prompt)
        
        try:
            response_clean = self._clean_json_response(response)
            review = json.loads(response_clean)
            
            score = review.get('quality_score', 0)
            issues_count = len(review.get('issues', []))
            status = review.get('approval_status', 'unknown')
            
            print(f"✅ Review complete!")
            print(f"   Quality Score: {score}/100")
            print(f"   Issues Found: {issues_count}")
            print(f"   Status: {status.upper()}")
            return review
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing review JSON: {e}")
            print(f"Raw response (first 300 chars): {response[:300]}")
            return {
                "error": "Failed to parse review",
                "raw_response": response[:200]
            }
    
    def cross_check_agents(
        self,
        outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cross-check outputs from multiple agents for consistency
        
        Args:
            outputs: Dictionary of agent_name -> output pairs
            
        Returns:
            Consistency check report
        """
        print(f"\n🔄 Cross-checking outputs from {len(outputs)} agents...")
        
        prompt = f"""Review these outputs from multiple agents for consistency:

{json.dumps(outputs, indent=2)}

Check for:
1. Conflicting information
2. Missing dependencies
3. Inconsistent assumptions
4. Integration issues

Provide consistency assessment as raw JSON (no markdown).

Remember: Output ONLY raw JSON, no markdown!"""
        
        response = self.think(prompt)
        
        try:
            response_clean = self._clean_json_response(response)
            check = json.loads(response_clean)
            print(f"✅ Cross-check complete!")
            return check
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing cross-check JSON: {e}")
            return {"error": "Failed to parse cross-check"}


# Test the agent if run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING REFLECTION & QA AGENT")
    print("="*60)
    
    # Create the agent
    qa_agent = ReflectionQAAgent()
    
    # Test 1: Review a form design
    print("\n--- Test 1: Review Form Design ---")
    test_form_output = {
        "form_id": "mood_tracker",
        "form_name": "Mood Tracker",
        "fields": [
            {
                "field_id": "happiness",
                "field_type": "scale",
                "validation": {"min": 1, "max": 10}
            }
        ]
    }
    
    review = qa_agent.review_output(
        agent_name="Form Designer Agent",
        output=test_form_output,
        context="This form will be used daily in a depression treatment trial"
    )
    print("\nResult:")
    print(json.dumps(review, indent=2))
    
    # Test 2: Cross-check multiple agents
    print("\n--- Test 2: Cross-Check Multiple Agents ---")
    multi_outputs = {
        "Form Designer": {
            "forms": 3,
            "frequency": "daily"
        },
        "Schedule Optimizer": {
            "total_forms": 3,
            "lcm": 1,
            "max_burden": 3
        }
    }
    
    consistency = qa_agent.cross_check_agents(multi_outputs)
    print("\nResult:")
    print(json.dumps(consistency, indent=2))
    
    print("\n" + "="*60)
    print("✅ REFLECTION & QA AGENT TEST COMPLETE!")
    print("="*60 + "\n")