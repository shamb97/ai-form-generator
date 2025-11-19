"""
Conditional Dependencies Engine
================================

This engine handles conditional form activation based on:
- Form completion status
- Phase progression
- Event triggers
- Custom conditions

Example Use Cases:
- "Show Treatment Form only if Baseline is complete"
- "Activate Follow-up Forms only in Follow-up Phase"
- "Trigger Exit Survey if Early Termination event occurs"
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class ConditionType(str, Enum):
    """Types of conditions that can trigger form activation"""
    FORM_COMPLETED = "form_completed"
    PHASE_REACHED = "phase_reached"
    EVENT_TRIGGERED = "event_triggered"
    DAY_REACHED = "day_reached"
    ALL_FORMS_IN_PHASE = "all_forms_in_phase_completed"


class ConditionalRule:
    """
    Represents a rule for conditional form activation
    """
    def __init__(
        self,
        rule_id: str,
        condition_type: ConditionType,
        condition_value: Any,
        target_forms: List[str],
        description: str = ""
    ):
        self.rule_id = rule_id
        self.condition_type = condition_type
        self.condition_value = condition_value
        self.target_forms = target_forms
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "condition_type": self.condition_type,
            "condition_value": self.condition_value,
            "target_forms": self.target_forms,
            "description": self.description
        }


class ConditionalEngine:
    """
    Engine for evaluating conditional dependencies and activating forms
    """
    
    def __init__(self):
        self.rules: Dict[str, ConditionalRule] = {}
        self.form_activation_status: Dict[int, Dict[str, bool]] = {}  # {subject_id: {form_id: is_active}}
        self.completion_status: Dict[int, Dict[str, bool]] = {}  # {subject_id: {form_id: is_complete}}
        self.subject_phases: Dict[int, str] = {}  # {subject_id: current_phase}
        self.triggered_events: Dict[int, List[str]] = {}  # {subject_id: [event_types]}
    
    def add_rule(self, rule: ConditionalRule):
        """Add a conditional rule"""
        self.rules[rule.rule_id] = rule
        print(f"✅ Added conditional rule: {rule.rule_id}")
    
    def mark_form_complete(self, subject_id: int, form_id: str):
        """Mark a form as complete for a subject"""
        if subject_id not in self.completion_status:
            self.completion_status[subject_id] = {}
        self.completion_status[subject_id][form_id] = True
        print(f"✅ Marked form '{form_id}' complete for subject {subject_id}")
        
        # Check if this completion triggers any rules
        self._evaluate_completion_rules(subject_id, form_id)
    
    def set_subject_phase(self, subject_id: int, phase: str):
        """Set the current phase for a subject"""
        self.subject_phases[subject_id] = phase
        print(f"✅ Subject {subject_id} entered phase: {phase}")
        
        # Check if this phase change triggers any rules
        self._evaluate_phase_rules(subject_id, phase)
    
    def trigger_event(self, subject_id: int, event_type: str):
        """Trigger an event for a subject"""
        if subject_id not in self.triggered_events:
            self.triggered_events[subject_id] = []
        self.triggered_events[subject_id].append(event_type)
        print(f"⚡ Event '{event_type}' triggered for subject {subject_id}")
        
        # Check if this event triggers any rules
        self._evaluate_event_rules(subject_id, event_type)
    
    def check_condition(
        self,
        subject_id: int,
        condition_type: ConditionType,
        condition_value: Any
    ) -> bool:
        """
        Check if a condition is met for a subject
        
        Args:
            subject_id: The subject to check
            condition_type: Type of condition
            condition_value: Value to check against
            
        Returns:
            True if condition is met, False otherwise
        """
        if condition_type == ConditionType.FORM_COMPLETED:
            form_id = condition_value
            return self.completion_status.get(subject_id, {}).get(form_id, False)
        
        elif condition_type == ConditionType.PHASE_REACHED:
            phase = condition_value
            return self.subject_phases.get(subject_id) == phase
        
        elif condition_type == ConditionType.EVENT_TRIGGERED:
            event_type = condition_value
            return event_type in self.triggered_events.get(subject_id, [])
        
        elif condition_type == ConditionType.ALL_FORMS_IN_PHASE:
            phase = condition_value
            # This would check if all required forms in a phase are complete
            # Simplified for now
            return self.subject_phases.get(subject_id) == phase
        
        return False
    
    def activate_forms(self, subject_id: int, form_ids: List[str]):
        """
        Activate forms for a subject
        
        Args:
            subject_id: Subject to activate forms for
            form_ids: List of form IDs to activate
        """
        if subject_id not in self.form_activation_status:
            self.form_activation_status[subject_id] = {}
        
        for form_id in form_ids:
            self.form_activation_status[subject_id][form_id] = True
        
        print(f"✅ Activated {len(form_ids)} forms for subject {subject_id}")
    
    def deactivate_forms(self, subject_id: int, form_ids: List[str]):
        """Deactivate forms for a subject"""
        if subject_id not in self.form_activation_status:
            return
        
        for form_id in form_ids:
            self.form_activation_status[subject_id][form_id] = False
        
        print(f"🔒 Deactivated {len(form_ids)} forms for subject {subject_id}")
    
    def get_active_forms(self, subject_id: int) -> List[str]:
        """Get all active forms for a subject"""
        if subject_id not in self.form_activation_status:
            return []
        
        return [
            form_id 
            for form_id, is_active in self.form_activation_status[subject_id].items()
            if is_active
        ]
    
    def _evaluate_completion_rules(self, subject_id: int, completed_form_id: str):
        """Evaluate rules triggered by form completion"""
        for rule in self.rules.values():
            if rule.condition_type == ConditionType.FORM_COMPLETED:
                if rule.condition_value == completed_form_id:
                    # This rule is triggered!
                    self.activate_forms(subject_id, rule.target_forms)
                    print(f"🎯 Rule '{rule.rule_id}' triggered by completion of '{completed_form_id}'")
    
    def _evaluate_phase_rules(self, subject_id: int, phase: str):
        """Evaluate rules triggered by phase change"""
        for rule in self.rules.values():
            if rule.condition_type == ConditionType.PHASE_REACHED:
                if rule.condition_value == phase:
                    # This rule is triggered!
                    self.activate_forms(subject_id, rule.target_forms)
                    print(f"🎯 Rule '{rule.rule_id}' triggered by entering phase '{phase}'")
    
    def _evaluate_event_rules(self, subject_id: int, event_type: str):
        """Evaluate rules triggered by event"""
        for rule in self.rules.values():
            if rule.condition_type == ConditionType.EVENT_TRIGGERED:
                if rule.condition_value == event_type:
                    # This rule is triggered!
                    self.activate_forms(subject_id, rule.target_forms)
                    print(f"🎯 Rule '{rule.rule_id}' triggered by event '{event_type}'")
    
    def get_status_summary(self, subject_id: int) -> Dict[str, Any]:
        """Get complete status summary for a subject"""
        return {
            "subject_id": subject_id,
            "current_phase": self.subject_phases.get(subject_id, "Not Set"),
            "active_forms": self.get_active_forms(subject_id),
            "completed_forms": [
                form_id 
                for form_id, is_complete in self.completion_status.get(subject_id, {}).items()
                if is_complete
            ],
            "triggered_events": self.triggered_events.get(subject_id, []),
            "total_active": len(self.get_active_forms(subject_id)),
            "total_complete": len([
                f for f, c in self.completion_status.get(subject_id, {}).items() if c
            ])
        }


# Test the engine if run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING CONDITIONAL ENGINE")
    print("="*60)
    
    # Create engine
    engine = ConditionalEngine()
    
    # Add a rule: "Show Treatment Forms when Baseline is complete"
    rule1 = ConditionalRule(
        rule_id="baseline_to_treatment",
        condition_type=ConditionType.FORM_COMPLETED,
        condition_value="baseline_assessment",
        target_forms=["treatment_form_1", "treatment_form_2"],
        description="Activate treatment forms after baseline completion"
    )
    engine.add_rule(rule1)
    
    # Test subject
    subject_id = 101
    
    print("\n--- Initial Status ---")
    print(f"Active forms: {engine.get_active_forms(subject_id)}")
    
    print("\n--- Complete Baseline ---")
    engine.mark_form_complete(subject_id, "baseline_assessment")
    
    print("\n--- Check Active Forms ---")
    active = engine.get_active_forms(subject_id)
    print(f"Active forms: {active}")
    
    print("\n--- Full Status ---")
    status = engine.get_status_summary(subject_id)
    import json
    print(json.dumps(status, indent=2))
    
    print("\n" + "="*60)
    print("✅ CONDITIONAL ENGINE TEST COMPLETE!")
    print("="*60 + "\n")
