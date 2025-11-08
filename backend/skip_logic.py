"""
Intra-Form Skip Logic Module

Handles conditional display of form fields based on user responses.
Enables dynamic forms where fields appear/disappear based on answers.

Examples:
- "If Q1 = 'Yes', show Q2-Q5"
- "If age >= 18, show adult_consent, else show parental_consent"
- "If symptoms contains 'fever', show temperature_field"
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class OperatorType(str, Enum):
    """Supported comparison operators for skip logic conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    CONTAINS = "contains"  # For arrays/checkboxes
    NOT_CONTAINS = "not_contains"
    IN_LIST = "in"  # Value is in a list
    NOT_IN_LIST = "not_in"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class LogicOperator(str, Enum):
    """Logical operators for combining multiple conditions."""
    AND = "and"
    OR = "or"


class SkipCondition(BaseModel):
    """
    A single condition for skip logic evaluation.
    
    Example:
        {
            "field": "has_symptoms",
            "operator": "equals",
            "value": "Yes"
        }
    """
    field: str = Field(description="Field ID to check")
    operator: OperatorType = Field(description="Comparison operator")
    value: Any = Field(default=None, description="Value to compare against")
    
    def evaluate(self, field_value: Any) -> bool:
        """
        Evaluate this condition against a field value.
        
        Args:
            field_value: Current value of the field
            
        Returns:
            True if condition is satisfied, False otherwise
        """
        # Handle empty/missing values
        if field_value is None or field_value == "":
            if self.operator == OperatorType.IS_EMPTY:
                return True
            if self.operator == OperatorType.IS_NOT_EMPTY:
                return False
            # For other operators, empty value means condition fails
            return False
        
        # IS_NOT_EMPTY check
        if self.operator == OperatorType.IS_NOT_EMPTY:
            return True
        
        # IS_EMPTY check (but we have a value)
        if self.operator == OperatorType.IS_EMPTY:
            return False
        
        # All other operators need a comparison value
        if self.value is None:
            return False
        
        # Perform comparison based on operator
        try:
            if self.operator == OperatorType.EQUALS:
                return str(field_value).lower() == str(self.value).lower()
            
            elif self.operator == OperatorType.NOT_EQUALS:
                return str(field_value).lower() != str(self.value).lower()
            
            elif self.operator == OperatorType.GREATER_THAN:
                return float(field_value) > float(self.value)
            
            elif self.operator == OperatorType.GREATER_THAN_OR_EQUAL:
                return float(field_value) >= float(self.value)
            
            elif self.operator == OperatorType.LESS_THAN:
                return float(field_value) < float(self.value)
            
            elif self.operator == OperatorType.LESS_THAN_OR_EQUAL:
                return float(field_value) <= float(self.value)
            
            elif self.operator == OperatorType.CONTAINS:
                # For checkbox/multi-select: check if value in array
                if isinstance(field_value, list):
                    return self.value in field_value
                # For text: substring match
                return str(self.value).lower() in str(field_value).lower()
            
            elif self.operator == OperatorType.NOT_CONTAINS:
                if isinstance(field_value, list):
                    return self.value not in field_value
                return str(self.value).lower() not in str(field_value).lower()
            
            elif self.operator == OperatorType.IN_LIST:
                # Check if field_value is in the provided list
                if isinstance(self.value, list):
                    return field_value in self.value
                return False
            
            elif self.operator == OperatorType.NOT_IN_LIST:
                if isinstance(self.value, list):
                    return field_value not in self.value
                return True
            
            else:
                # Unknown operator
                return False
                
        except (ValueError, TypeError):
            # Type conversion failed
            return False


class SkipLogicRule(BaseModel):
    """
    Complete skip logic rule for a field or group of fields.
    
    Can have single condition or multiple conditions combined with AND/OR.
    
    Examples:
        # Simple: Show if has_symptoms = "Yes"
        {
            "condition": {
                "field": "has_symptoms",
                "operator": "equals",
                "value": "Yes"
            },
            "action": "show",
            "target_fields": ["symptom_list", "symptom_severity"]
        }
        
        # Complex: Show if (age >= 18 AND has_symptoms = "Yes")
        {
            "conditions": [
                {"field": "age", "operator": "greater_than_or_equal", "value": 18},
                {"field": "has_symptoms", "operator": "equals", "value": "Yes"}
            ],
            "logic": "and",
            "action": "show",
            "target_fields": ["adult_symptom_details"]
        }
    """
    # Single condition (simple rules)
    condition: Optional[SkipCondition] = None
    
    # Multiple conditions (complex rules)
    conditions: Optional[List[SkipCondition]] = None
    logic: LogicOperator = LogicOperator.AND
    
    # What to do when condition(s) met
    action: str = Field(
        default="show",
        description="Action to take: 'show' or 'hide'"
    )
    
    # Which fields are affected
    target_fields: List[str] = Field(
        description="Field IDs to show/hide"
    )
    
    def evaluate(self, current_values: Dict[str, Any]) -> bool:
        """
        Evaluate this rule against current form values.
        
        Args:
            current_values: Dict of field_id -> value
            
        Returns:
            True if condition(s) are satisfied, False otherwise
        """
        # Simple rule: single condition
        if self.condition:
            field_value = current_values.get(self.condition.field)
            return self.condition.evaluate(field_value)
        
        # Complex rule: multiple conditions
        if self.conditions:
            results = []
            for cond in self.conditions:
                field_value = current_values.get(cond.field)
                results.append(cond.evaluate(field_value))
            
            # Combine results based on logic operator
            if self.logic == LogicOperator.AND:
                return all(results)
            else:  # OR
                return any(results)
        
        # No conditions defined - always false
        return False


class SkipLogicEvaluator:
    """
    Evaluates skip logic rules for an entire form.
    
    Determines which fields should be visible based on current values.
    """
    
    def __init__(self, form_schema: Dict[str, Any]):
        """
        Initialize evaluator with form schema.
        
        Args:
            form_schema: Complete form schema including skip logic rules
        """
        self.form_schema = form_schema
        self.rules = self._extract_rules()
    
    def _extract_rules(self) -> List[SkipLogicRule]:
        """Extract all skip logic rules from form schema."""
        rules = []
        
        for field in self.form_schema.get("fields", []):
            skip_logic = field.get("skip_logic")
            
            if skip_logic:
                try:
                    # Convert dict to SkipLogicRule model
                    rule = SkipLogicRule(**skip_logic)
                    rules.append(rule)
                except Exception as e:
                    print(f"Warning: Invalid skip logic for field {field.get('field_id')}: {e}")
        
        return rules
    
    def get_visible_fields(
        self,
        current_values: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Determine which fields should be visible.
        
        Args:
            current_values: Current form values {field_id: value}
            
        Returns:
            Dict mapping field_id to visibility {field_id: is_visible}
        """
        # Start with all fields visible
        visibility = {}
        for field in self.form_schema.get("fields", []):
            field_id = field.get("field_id")
            visibility[field_id] = True
        
        # Apply skip logic rules
        for rule in self.rules:
            rule_satisfied = rule.evaluate(current_values)
            
            # Update visibility for target fields
            for field_id in rule.target_fields:
                if rule.action == "show":
                    # Show field only if rule is satisfied
                    visibility[field_id] = rule_satisfied
                elif rule.action == "hide":
                    # Hide field only if rule is satisfied
                    visibility[field_id] = not rule_satisfied
        
        return visibility
    
    def get_required_fields(
        self,
        current_values: Dict[str, Any]
    ) -> List[str]:
        """
        Get list of required fields that are currently visible.
        
        Args:
            current_values: Current form values
            
        Returns:
            List of field IDs that are required and visible
        """
        visibility = self.get_visible_fields(current_values)
        required = []
        
        for field in self.form_schema.get("fields", []):
            field_id = field.get("field_id")
            is_required = field.get("required", False)
            is_visible = visibility.get(field_id, True)
            
            if is_required and is_visible:
                required.append(field_id)
        
        return required
    
    def validate_form(
        self,
        submitted_values: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate form submission considering skip logic.
        
        Only visible required fields must be filled.
        
        Args:
            submitted_values: Values submitted by user
            
        Returns:
            (is_valid, missing_required_fields)
        """
        required_fields = self.get_required_fields(submitted_values)
        missing = []
        
        for field_id in required_fields:
            value = submitted_values.get(field_id)
            if value is None or value == "":
                missing.append(field_id)
        
        return (len(missing) == 0, missing)


# === UTILITY FUNCTIONS ===

def add_skip_logic_to_field(
    field_schema: Dict[str, Any],
    trigger_field: str,
    trigger_value: Any,
    operator: str = "equals",
    action: str = "show"
) -> Dict[str, Any]:
    """
    Helper to add simple skip logic to a field schema.
    
    Example:
        field = {"field_id": "symptom_details", ...}
        field_with_logic = add_skip_logic_to_field(
            field,
            trigger_field="has_symptoms",
            trigger_value="Yes",
            operator="equals",
            action="show"
        )
    """
    field_schema["skip_logic"] = {
        "condition": {
            "field": trigger_field,
            "operator": operator,
            "value": trigger_value
        },
        "action": action,
        "target_fields": [field_schema["field_id"]]
    }
    return field_schema


def create_age_gate_rule(
    min_age: int,
    fields_if_adult: List[str],
    fields_if_minor: List[str]
) -> List[Dict[str, Any]]:
    """
    Create skip logic rules for age-gated content.
    
    Returns two rules: one for adults, one for minors.
    """
    return [
        {
            "condition": {
                "field": "age",
                "operator": "greater_than_or_equal",
                "value": min_age
            },
            "action": "show",
            "target_fields": fields_if_adult
        },
        {
            "condition": {
                "field": "age",
                "operator": "less_than",
                "value": min_age
            },
            "action": "show",
            "target_fields": fields_if_minor
        }
    ]


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    print("=" * 60)
    print("SKIP LOGIC MODULE - EXAMPLES")
    print("=" * 60)
    
    # Example 1: Simple smoking question
    print("\n1. SIMPLE SKIP LOGIC")
    print("-" * 60)
    
    smoking_form = {
        "form_id": "health_survey",
        "fields": [
            {
                "field_id": "smokes",
                "label": "Do you smoke?",
                "type": "radio",
                "options": ["Yes", "No"]
            },
            {
                "field_id": "cigarettes_per_day",
                "label": "How many cigarettes per day?",
                "type": "number",
                "skip_logic": {
                    "condition": {
                        "field": "smokes",
                        "operator": "equals",
                        "value": "Yes"
                    },
                    "action": "show",
                    "target_fields": ["cigarettes_per_day"]
                }
            }
        ]
    }
    
    evaluator = SkipLogicEvaluator(smoking_form)
    
    # Test: User says "Yes"
    values_yes = {"smokes": "Yes"}
    visibility_yes = evaluator.get_visible_fields(values_yes)
    print(f"User smokes: {values_yes}")
    print(f"Cigarettes field visible: {visibility_yes['cigarettes_per_day']}")
    
    # Test: User says "No"
    values_no = {"smokes": "No"}
    visibility_no = evaluator.get_visible_fields(values_no)
    print(f"\nUser doesn't smoke: {values_no}")
    print(f"Cigarettes field visible: {visibility_no['cigarettes_per_day']}")
    
    # Example 2: Complex age gate
    print("\n2. COMPLEX SKIP LOGIC (Age Gate)")
    print("-" * 60)
    
    age_form = {
        "form_id": "consent_form",
        "fields": [
            {"field_id": "age", "type": "number"},
            {"field_id": "adult_consent", "type": "checkbox",
             "skip_logic": {
                 "condition": {
                     "field": "age",
                     "operator": "greater_than_or_equal",
                     "value": 18
                 },
                 "action": "show",
                 "target_fields": ["adult_consent"]
             }},
            {"field_id": "parental_consent", "type": "checkbox",
             "skip_logic": {
                 "condition": {
                     "field": "age",
                     "operator": "less_than",
                     "value": 18
                 },
                 "action": "show",
                 "target_fields": ["parental_consent"]
             }}
        ]
    }
    
    evaluator2 = SkipLogicEvaluator(age_form)
    
    # Test: Adult
    adult_values = {"age": 25}
    adult_visibility = evaluator2.get_visible_fields(adult_values)
    print(f"Age 25: adult_consent={adult_visibility['adult_consent']}, "
          f"parental_consent={adult_visibility['parental_consent']}")
    
    # Test: Minor
    minor_values = {"age": 15}
    minor_visibility = evaluator2.get_visible_fields(minor_values)
    print(f"Age 15: adult_consent={minor_visibility['adult_consent']}, "
          f"parental_consent={minor_visibility['parental_consent']}")
    
    print("\n" + "=" * 60)
    print("✅ Skip logic module working!")
    print("=" * 60)