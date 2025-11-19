"""
Clinical Compliance Agent
=========================

This agent checks for regulatory compliance in clinical trial forms!

It verifies:
- ICH-GCP compliance
- 21 CFR Part 11 requirements
- GDPR data privacy
- Informed consent requirements
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


class ClinicalComplianceAgent(BaseAgent):
    """
    Specialized agent for regulatory compliance checking
    """
    
    def __init__(self):
        system_prompt = """You are an expert in clinical trial regulatory compliance.

Your job is to review study designs and forms for compliance with:
- ICH-GCP (International Council for Harmonisation - Good Clinical Practice)
- 21 CFR Part 11 (FDA Electronic Records)
- GDPR (EU Data Privacy)
- Informed Consent Requirements

RULES:
- Flag potential compliance issues
- Suggest required fields for regulatory compliance
- Identify missing documentation
- Recommend audit trail requirements
- ALWAYS output valid JSON only - NO markdown code blocks

OUTPUT FORMAT (raw JSON only):
{
  "compliance_status": "compliant|needs_review|non_compliant",
  "issues": [
    {
      "regulation": "ICH-GCP|21CFR11|GDPR|Consent",
      "severity": "critical|high|medium|low",
      "issue": "description of the issue",
      "recommendation": "how to fix it"
    }
  ],
  "required_fields": [
    {
      "field_name": "required field",
      "regulation": "which regulation requires it",
      "rationale": "why it's required"
    }
  ],
  "recommendations": ["list of compliance suggestions"]
}

CRITICAL: Output ONLY raw JSON, no markdown formatting!"""
        
        super().__init__(
            name="Clinical Compliance Agent",
            role="Verifies regulatory compliance",
            system_prompt=system_prompt
        )
    
    def _clean_json_response(self, response: str) -> str:
        """Clean up JSON response"""
        response_clean = response.strip()
        if response_clean.startswith("```"):
            lines = response_clean.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_clean = "\n".join(lines)
        return response_clean.strip()
    
    def check_compliance(
        self, 
        study_design: Dict[str, Any],
        region: str = "US"
    ) -> Dict[str, Any]:
        """
        Check study design for regulatory compliance
        
        Args:
            study_design: The study configuration to check
            region: Regulatory region (US, EU, etc.)
            
        Returns:
            Compliance report
        """
        study_name = study_design.get('study_name', 'Unknown Study')
        print(f"\n🏥 Checking compliance for '{study_name}' ({region} regulations)...")
        
        prompt = f"""Review this study design for regulatory compliance:

Region: {region}
Study Design:
{json.dumps(study_design, indent=2)}

Check for compliance with:
- ICH-GCP standards
- 21 CFR Part 11 (if US)
- GDPR (if EU)
- Informed consent requirements
- Audit trail requirements

Remember: Output ONLY raw JSON, no markdown!"""
        
        response = self.think(prompt)
        
        try:
            response_clean = self._clean_json_response(response)
            compliance = json.loads(response_clean)
            
            print(f"✅ Compliance check complete!")
            print(f"   Status: {compliance.get('compliance_status', 'Unknown')}")
            print(f"   Issues found: {len(compliance.get('issues', []))}")
            return compliance
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing compliance JSON: {e}")
            print(f"Raw response (first 300 chars): {response[:300]}")
            return {
                "error": "Failed to parse compliance report",
                "raw_response": response[:200]
            }
    
    def verify_consent_process(self, consent_form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify informed consent form meets requirements
        
        Args:
            consent_form: The consent form to verify
            
        Returns:
            Verification report
        """
        print(f"\n📋 Verifying consent form compliance...")
        
        prompt = f"""Review this consent form for regulatory requirements:

{json.dumps(consent_form, indent=2)}

Check for:
- Required ICH-GCP consent elements
- Clear language (8th grade reading level)
- Voluntary participation statement
- Right to withdraw
- Data privacy information
- Risk disclosure
- Contact information

Provide verification as raw JSON:
{{
  "compliant": true/false,
  "missing_elements": ["list of missing required elements"],
  "recommendations": ["suggestions for improvement"]
}}

Remember: Output ONLY raw JSON, no markdown!"""
        
        response = self.think(prompt)
        
        try:
            response_clean = self._clean_json_response(response)
            verification = json.loads(response_clean)
            print(f"✅ Consent verification complete!")
            compliant = verification.get('compliant', False)
            print(f"   Compliant: {'Yes' if compliant else 'No'}")
            return verification
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing verification JSON: {e}")
            return {"error": "Failed to parse verification"}


# Test the agent if run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING CLINICAL COMPLIANCE AGENT")
    print("="*60)
    
    # Create the agent
    compliance = ClinicalComplianceAgent()
    
    # Test 1: Check study compliance
    print("\n--- Test 1: Study Compliance Check ---")
    test_study = {
        "study_name": "Depression Treatment Trial",
        "duration_days": 84,
        "forms": [
            {"form_name": "Daily Mood", "frequency": 1},
            {"form_name": "Adverse Events", "frequency": 7}
        ],
        "consent_required": True,
        "data_retention_years": 15
    }
    
    report = compliance.check_compliance(test_study, region="US")
    print("\nResult:")
    print(json.dumps(report, indent=2))
    
    # Test 2: Verify consent form
    print("\n--- Test 2: Consent Form Verification ---")
    test_consent = {
        "title": "Informed Consent for Depression Study",
        "sections": [
            "Purpose of study",
            "Procedures",
            "Risks and benefits",
            "Confidentiality"
        ]
    }
    
    verification = compliance.verify_consent_process(test_consent)
    print("\nResult:")
    print(json.dumps(verification, indent=2))
    
    print("\n" + "="*60)
    print("✅ CLINICAL COMPLIANCE AGENT TEST COMPLETE!")
    print("="*60 + "\n")