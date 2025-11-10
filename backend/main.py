"""
AI-Powered Clinical Form Generator
Backend API Server

Features:
- AI form generation from natural language (Day 1)
- LCM scheduling algorithm (Day 2)
- Phase tracking, events, navigation (Day 3)
- Study configuration module (Day 3 extension)
- Intra-form skip logic (Day 4)
- Database persistence (Day 5)
- Multi-role authentication system (NEW!)

Next Steps:
- Informed consent system
"""

# ============================================================================
# IMPORTS
# ============================================================================

# Standard library
import os
import json
import re
from pathlib import Path
from typing import Optional
from datetime import datetime
from designer_api import router as designer_router

# Environment and configuration
from dotenv import load_dotenv

# Load environment variables
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# FastAPI and related
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# External services
import anthropic

# Database
from database import (
    init_db, get_db, 
    create_study, create_form, create_day_type,
    get_all_studies, get_study, get_forms_by_study
)

# Authentication (NEW!)
from auth_database import init_db as init_auth_db
from auth_api import router as auth_router
from designer_api import router as designer_router

# Local modules
from scheduler import calculate_lcm_schedule, ScheduleRequest, ScheduleResponse
from study_config import (
    StudyConfiguration,
    ParticipantUIConfig,
    StudyFeatures,
    validate_configuration
)
from skip_logic import (
    SkipLogicEvaluator,
    SkipLogicRule,
    SkipCondition,
    add_skip_logic_to_field
)
from consent import (
    ConsentSchema,
    ConsentRecord,
    ConsentValidator,
    ConsentManager,
    create_standard_consent,
    ConsentType
)

# AI Agents (NEW!)
from agents.base_agent import BaseAgent
from agents.form_designer_agent import FormDesignerAgent
from agents.schedule_optimizer_agent import ScheduleOptimizerAgent
from agents.policy_recommender_agent import PolicyRecommenderAgent
from agents.clinical_compliance_agent import ClinicalComplianceAgent
from agents.reflection_qa_agent import ReflectionQAAgent


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="AI Form Generator API",
    description="AI-powered clinical research form generation and scheduling with multi-role authentication",
    version="2.0.0"
)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
consent_manager = ConsentManager()

# AI Agents (initialized on startup)
form_designer = None
schedule_optimizer = None
policy_recommender = None
compliance_checker = None
qa_reviewer = None

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize databases and AI agents on startup."""
    global form_designer, schedule_optimizer, policy_recommender, compliance_checker, qa_reviewer
    
    # Initialize databases
    init_db()  # Research forms database
    init_auth_db()  # Authentication database
    
    # Initialize AI Agents
    print("🤖 Initializing AI Agents...")
    form_designer = FormDesignerAgent()
    schedule_optimizer = ScheduleOptimizerAgent()
    policy_recommender = PolicyRecommenderAgent()
    compliance_checker = ClinicalComplianceAgent()
    qa_reviewer = ReflectionQAAgent()
    print("✅ All 5 AI agents initialized successfully!")
    
    print("🚀 Server started - All systems ready!")


# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

# Allow all origins for development/demo
# In production, specify exact origins
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Include authentication router (NEW!)
app.include_router(auth_router)
app.include_router(designer_router)


# ============================================================================
# SYSTEM PROMPT FOR AI FORM GENERATION
# ============================================================================

SYSTEM_PROMPT = """You are an expert clinical research form designer. Convert the user's description into a valid JSON form schema.

OUTPUT RULES:
1. Return ONLY valid JSON - no markdown, no explanations, no code blocks
2. Follow this EXACT structure:

{
  "form_id": "lowercase_with_underscores",
  "title": "Human Readable Title",
  "description": "Brief description",
  "fields": [
    {
      "field_id": "field_name",
      "label": "Question Label",
      "type": "text|number|dropdown|radio|checkbox|slider|date|time|textarea",
      "required": true,
      "options": ["Option 1", "Option 2"],
      "validation": {
        "min": 0,
        "max": 10,
        "min_length": 1,
        "max_length": 500
      },
      "help_text": "Optional guidance",
      "skip_logic": {
        "condition": {
          "field": "other_field_id",
          "operator": "equals|greater_than|less_than|contains",
          "value": "comparison_value"
        },
        "action": "show",
        "target_fields": ["this_field_id"]
      }
    }
  ]
}

SKIP LOGIC (Optional but powerful):
- Use skip_logic to make fields conditional
- Common pattern: "Show field X if field Y = 'Yes'"
- Operators: equals, not_equals, greater_than, less_than, greater_than_or_equal, less_than_or_equal, contains, is_empty, is_not_empty
- action: "show" (field visible when condition true) or "hide"
- target_fields: MUST include the current field's field_id

FIELD TYPES:
- text: Short text input
- textarea: Long text input
- number: Numeric input (use for ages, counts, measurements)
- dropdown: Single selection from list
- radio: Single selection with visible options
- checkbox: Multiple selections allowed
- slider: Numeric input with visual slider (use for scales like pain 0-10)
- date: Date picker
- time: Time picker

IMPORTANT:
- Use "slider" for rating scales (e.g., pain 0-10, satisfaction 1-5)
- Use "dropdown" for categories (e.g., location, symptoms)
- Use "radio" when there are 2-5 visible options
- Use "checkbox" when multiple selections are allowed
- Use skip_logic for conditional questions (e.g., "If has_symptoms = Yes, show symptom_details")
- Always include sensible validation rules
- Make field_id snake_case, no spaces
- Make labels clear and user-friendly"""


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

# --- Form Generation Models ---

class FormGenerationRequest(BaseModel):
    """Request to generate a form from natural language."""
    prompt: str = Field(description="Natural language description of desired form")
    model: str = Field(default="claude-sonnet-4-20250514", description="AI model to use")


class FormGenerationResponse(BaseModel):
    """Response containing generated form schema."""
    success: bool
    form_id: Optional[str] = None
    form_schema: Optional[dict] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


# --- Skip Logic Models ---

class EvaluateSkipLogicRequest(BaseModel):
    """Request to evaluate skip logic for a form."""
    form_schema: dict = Field(description="Complete form schema with skip logic")
    current_values: dict = Field(description="Current field values {field_id: value}")


class EvaluateSkipLogicResponse(BaseModel):
    """Response with field visibility information."""
    success: bool
    visible_fields: dict[str, bool] = Field(description="Map of field_id to visibility")
    required_fields: list[str] = Field(description="Currently required visible fields")
    hidden_count: int = Field(description="Number of hidden fields")
    visible_count: int = Field(description="Number of visible fields")


class ValidateFormWithSkipLogicRequest(BaseModel):
    """Request to validate form submission considering skip logic."""
    form_schema: dict = Field(description="Form schema with skip logic")
    submitted_values: dict = Field(description="Values submitted by user")


class ValidateFormResponse(BaseModel):
    """Response with validation results."""
    success: bool
    is_valid: bool
    missing_required: list[str] = []
    error: Optional[str] = None


# --- Legacy/Utility Models ---

class EchoIn(BaseModel):
    """Simple echo request for testing."""
    message: str
    meta: Optional[dict] = None


# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint - API information."""
    return {
        "status": "ok",
        "message": "AI Form Generator API - Running with AI Agents & Authentication",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "authentication": "/api/v1/auth/*",
            "form_generation": "/api/v1/forms/generate",
            "ai_form_design": "/api/v1/ai/design-form",
            "ai_schedule_optimize": "/api/v1/ai/optimize-schedule",
            "ai_policy_recommend": "/api/v1/ai/recommend-policies",
            "ai_compliance_check": "/api/v1/ai/check-compliance",
            "ai_quality_review": "/api/v1/ai/review-quality",
            "schedule_generation": "/api/v1/schedule/generate",
            "skip_logic_evaluation": "/api/v1/forms/evaluate-skip-logic",
            "study_configuration": "/api/v1/studies/configure",
            "database_studies": "/api/v1/studies"
        },
        "ai_agents": {
            "form_designer": "Converts natural language to JSON form schemas",
            "schedule_optimizer": "Optimizes schedules using LCM algorithm with AI reasoning",
            "policy_recommender": "Suggests validation rules and skip logic",
            "compliance_checker": "Checks regulatory compliance (GCP, HIPAA)",
            "qa_reviewer": "Reviews quality of forms, studies, and schedules"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    api_key_present = bool(os.getenv("ANTHROPIC_API_KEY"))
    agents_initialized = all([
        form_designer is not None,
        schedule_optimizer is not None,
        policy_recommender is not None,
        compliance_checker is not None,
        qa_reviewer is not None
    ])
    
    return {
        "ok": True,
        "api_key_configured": api_key_present,
        "database_initialized": True,
        "auth_enabled": True,
        "ai_agents_initialized": agents_initialized,
        "ai_agents": {
            "form_designer": form_designer is not None,
            "schedule_optimizer": schedule_optimizer is not None,
            "policy_recommender": policy_recommender is not None,
            "compliance_checker": compliance_checker is not None,
            "qa_reviewer": qa_reviewer is not None
        },
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
    }


@app.post("/echo")
def echo(payload: EchoIn):
    """Echo endpoint for testing."""
    return {"you_sent": payload.model_dump()}


# ============================================================================
# FORM GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/forms/generate", response_model=FormGenerationResponse)
async def generate_form(request: FormGenerationRequest):
    """
    Generate a form schema from natural language prompt using Claude AI.
    
    Example:
        POST /api/v1/forms/generate
        {
            "prompt": "Create a daily symptom diary with questions about fever, cough, and fatigue"
        }
    """
    if not request.prompt or len(request.prompt.strip()) < 10:
        raise HTTPException(
            status_code=400, 
            detail="Prompt must be at least 10 characters"
        )
    
    try:
        print(f"🤖 Calling Claude with prompt: {request.prompt[:100]}...")
        
        message = client.messages.create(
            model=request.model,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": request.prompt}]
        )
        
        response_text = message.content[0].text
        print(f"📝 Raw response: {len(response_text)} chars")
        
        # Clean markdown code blocks
        cleaned = response_text.strip()
        cleaned = re.sub(r'^```json\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()
        
        # Parse JSON
        schema = json.loads(cleaned)
        
        # Validate basic structure
        if "form_id" not in schema or "fields" not in schema:
            return FormGenerationResponse(
                success=False,
                error="Invalid schema structure: missing form_id or fields",
                raw_response=response_text[:500]
            )
        
        print(f"✅ Generated form: {schema.get('form_id')}")
        
        return FormGenerationResponse(
            success=True,
            form_id=schema.get("form_id"),
            form_schema=schema
        )
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return FormGenerationResponse(
            success=False,
            error=f"Invalid JSON: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return FormGenerationResponse(
            success=False,
            error=str(e)
        )


# ============================================================================
# AI AGENT ENDPOINTS (NEW!)
# ============================================================================

class AIFormDesignRequest(BaseModel):
    """Request for AI form design using Form Designer Agent."""
    description: str = Field(description="Natural language description of the form")


class AIFormDesignResponse(BaseModel):
    """Response from Form Designer Agent."""
    success: bool
    form_schema: Optional[dict] = None
    error: Optional[str] = None


class AIScheduleOptimizeRequest(BaseModel):
    """Request for AI schedule optimization."""
    frequencies: list[int] = Field(description="List of form frequencies in days")
    study_duration: Optional[int] = None


class AIScheduleOptimizeResponse(BaseModel):
    """Response from Schedule Optimizer Agent."""
    success: bool
    lcm: Optional[int] = None
    reasoning: Optional[str] = None
    schedule_summary: Optional[dict] = None
    error: Optional[str] = None


class AIPolicyRequest(BaseModel):
    """Request for AI policy recommendations."""
    form_schema: dict = Field(description="Form schema to analyze")


class AIPolicyResponse(BaseModel):
    """Response from Policy Recommender Agent."""
    success: bool
    recommendations: Optional[dict] = None
    error: Optional[str] = None


class AIComplianceRequest(BaseModel):
    """Request for AI compliance check."""
    study_design: dict = Field(description="Study design to check")


class AIComplianceResponse(BaseModel):
    """Response from Clinical Compliance Agent."""
    success: bool
    compliance_report: Optional[dict] = None
    error: Optional[str] = None


class AIQARequest(BaseModel):
    """Request for AI quality review."""
    content: dict = Field(description="Content to review")
    review_type: str = Field(default="form", description="Type: form, study, schedule")


class AIQAResponse(BaseModel):
    """Response from Reflection QA Agent."""
    success: bool
    quality_score: Optional[int] = None
    feedback: Optional[dict] = None
    error: Optional[str] = None


@app.post("/api/v1/ai/design-form", response_model=AIFormDesignResponse)
async def ai_design_form(request: AIFormDesignRequest):
    """
    Use Form Designer Agent to create a form from natural language.
    
    This is more sophisticated than the basic generation endpoint - it uses
    the specialized agent with clinical research expertise.
    
    Example:
        POST /api/v1/ai/design-form
        {
            "description": "Daily pain diary with location, intensity, and medication tracking"
        }
    """
    if not form_designer:
        return AIFormDesignResponse(
            success=False,
            error="Form Designer Agent not initialized"
        )
    
    try:
        print(f"🎨 Form Designer Agent: Processing '{request.description[:50]}...'")
        
        # Use the agent to design the form
        result = form_designer.design_form(request.description)
        
        # Check if there was an error
        if "error" in result:
            return AIFormDesignResponse(
                success=False,
                error=result["error"]
            )
        
        print(f"✅ Form designed: {result.get('form_name', 'Unknown')}")
        
        return AIFormDesignResponse(
            success=True,
            form_schema=result
        )
        
    except Exception as e:
        print(f"❌ AI Form Design Error: {e}")
        return AIFormDesignResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/v1/ai/refine-form", response_model=AIFormDesignResponse)
async def ai_refine_form(request: dict):
    """
    Use Form Designer Agent to refine an existing form.
    
    Example:
        POST /api/v1/ai/refine-form
        {
            "form_schema": { existing form... },
            "refinement": "Add a date field that auto-populates with today's date"
        }
    """
    if not form_designer:
        return AIFormDesignResponse(
            success=False,
            error="Form Designer Agent not initialized"
        )
    
    try:
        form_schema = request.get('form_schema')
        refinement = request.get('refinement')
        
        if not form_schema or not refinement:
            return AIFormDesignResponse(
                success=False,
                error="Both form_schema and refinement are required"
            )
        
        print(f"🔧 Form Designer Agent: Refining form - '{refinement[:50]}...'")
        
        # Use the agent to refine the form
        result = form_designer.refine_form(form_schema, refinement)
        
        # Check if there was an error
        if "error" in result:
            return AIFormDesignResponse(
                success=False,
                error=result["error"]
            )
        
        print(f"✅ Form refined: {result.get('form_name', 'Unknown')}")
        
        return AIFormDesignResponse(
            success=True,
            form_schema=result
        )
        
    except Exception as e:
        print(f"❌ AI Form Refinement Error: {e}")
        return AIFormDesignResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/v1/ai/optimize-schedule", response_model=AIScheduleOptimizeResponse)
async def ai_optimize_schedule(request: AIScheduleOptimizeRequest):
    """
    Use Schedule Optimizer Agent to find optimal schedule with AI reasoning.
    
    Example:
        POST /api/v1/ai/optimize-schedule
        {
            "frequencies": [7, 14, 30],
            "study_duration": 90
        }
    """
    if not schedule_optimizer:
        return AIScheduleOptimizeResponse(
            success=False,
            error="Schedule Optimizer Agent not initialized"
        )
    
    try:
        print(f"📅 Schedule Optimizer Agent: Processing {len(request.frequencies)} frequencies")
        
        # Convert frequency list to form list (agent expects list of dicts)
        forms = [
            {
                "form_name": f"Form {i+1}",
                "frequency": freq
            }
            for i, freq in enumerate(request.frequencies)
        ]
        
        # Use the agent to optimize
        result = schedule_optimizer.optimize_schedule(
            forms,
            request.study_duration or 90
        )
        
        # Check for error
        if "error" in result:
            return AIScheduleOptimizeResponse(
                success=False,
                error=result["error"]
            )
        
        lcm = result.get('recommended_lcm')
        print(f"✅ Schedule optimized: LCM = {lcm} days")
        
        return AIScheduleOptimizeResponse(
            success=True,
            lcm=lcm,
            reasoning=result.get('schedule_rationale'),
            schedule_summary={
                "form_distribution": result.get('form_distribution', {}),
                "burden_analysis": result.get('participant_burden_analysis', {}),
                "recommendations": result.get('recommendations', [])
            }
        )
        
    except Exception as e:
        print(f"❌ AI Schedule Optimization Error: {e}")
        import traceback
        traceback.print_exc()
        return AIScheduleOptimizeResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/v1/ai/recommend-policies", response_model=AIPolicyResponse)
async def ai_recommend_policies(request: AIPolicyRequest):
    """
    Use Policy Recommender Agent to suggest validation rules and skip logic.
    
    Example:
        POST /api/v1/ai/recommend-policies
        {
            "form_schema": { ... }
        }
    """
    if not policy_recommender:
        return AIPolicyResponse(
            success=False,
            error="Policy Recommender Agent not initialized"
        )
    
    try:
        print(f"📋 Policy Recommender Agent: Analyzing form")
        
        # Use the agent to recommend policies
        result = policy_recommender.recommend_policies(request.form_schema)
        
        print(f"✅ Policies recommended")
        
        return AIPolicyResponse(
            success=True,
            recommendations=result
        )
        
    except Exception as e:
        print(f"❌ AI Policy Recommendation Error: {e}")
        return AIPolicyResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/v1/ai/check-compliance", response_model=AIComplianceResponse)
async def ai_check_compliance(request: AIComplianceRequest):
    """
    Use Clinical Compliance Agent to check regulatory compliance.
    
    Example:
        POST /api/v1/ai/check-compliance
        {
            "study_design": { ... }
        }
    """
    if not compliance_checker:
        return AIComplianceResponse(
            success=False,
            error="Clinical Compliance Agent not initialized"
        )
    
    try:
        print(f"🔍 Clinical Compliance Agent: Checking compliance")
        
        # Use the agent to check compliance
        result = compliance_checker.check_compliance(request.study_design)
        
        print(f"✅ Compliance check complete")
        
        return AIComplianceResponse(
            success=True,
            compliance_report=result
        )
        
    except Exception as e:
        print(f"❌ AI Compliance Check Error: {e}")
        return AIComplianceResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/v1/ai/review-quality", response_model=AIQAResponse)
async def ai_review_quality(request: AIQARequest):
    """
    Use Reflection QA Agent to review quality of forms/studies/schedules.
    
    Example:
        POST /api/v1/ai/review-quality
        {
            "content": { ... },
            "review_type": "form"
        }
    """
    if not qa_reviewer:
        return AIQAResponse(
            success=False,
            error="Reflection QA Agent not initialized"
        )
    
    try:
        print(f"🔍 Reflection QA Agent: Reviewing {request.review_type}")
        
        # Use the agent to review quality
        result = qa_reviewer.review_quality(
            request.content,
            request.review_type
        )
        
        print(f"✅ Quality review complete")
        
        return AIQAResponse(
            success=True,
            quality_score=result.get('score'),
            feedback=result.get('feedback')
        )
        
    except Exception as e:
        print(f"❌ AI Quality Review Error: {e}")
        return AIQAResponse(
            success=False,
            error=str(e)
        )


# ============================================================================
# SKIP LOGIC ENDPOINTS
# ============================================================================

@app.post("/api/v1/forms/evaluate-skip-logic", response_model=EvaluateSkipLogicResponse)
def evaluate_skip_logic(request: EvaluateSkipLogicRequest):
    """
    Evaluate skip logic for a form given current values.
    """
    try:
        evaluator = SkipLogicEvaluator(request.form_schema)
        
        # Get visibility map
        visibility = evaluator.get_visible_fields(request.current_values)
        
        # Get required visible fields
        required = evaluator.get_required_fields(request.current_values)
        
        # Calculate statistics
        visible_count = sum(1 for v in visibility.values() if v)
        hidden_count = len(visibility) - visible_count
        
        return EvaluateSkipLogicResponse(
            success=True,
            visible_fields=visibility,
            required_fields=required,
            hidden_count=hidden_count,
            visible_count=visible_count
        )
        
    except Exception as e:
        print(f"❌ Skip logic evaluation error: {e}")
        return EvaluateSkipLogicResponse(
            success=False,
            visible_fields={},
            required_fields=[],
            hidden_count=0,
            visible_count=0
        )


@app.post("/api/v1/forms/validate-with-skip-logic", response_model=ValidateFormResponse)
def validate_form_with_skip_logic(request: ValidateFormWithSkipLogicRequest):
    """
    Validate form submission considering skip logic.
    """
    try:
        evaluator = SkipLogicEvaluator(request.form_schema)
        is_valid, missing = evaluator.validate_form(request.submitted_values)
        
        return ValidateFormResponse(
            success=True,
            is_valid=is_valid,
            missing_required=missing
        )
        
    except Exception as e:
        print(f"❌ Form validation error: {e}")
        return ValidateFormResponse(
            success=False,
            is_valid=False,
            error=str(e)
        )


# ============================================================================
# SCHEDULE GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/schedule/generate", response_model=ScheduleResponse)
async def generate_schedule(request: ScheduleRequest):
    """
    Generate an LCM-based schedule for multiple forms.
    """
    # Validate request
    if request.study_duration_days < 1:
        raise HTTPException(
            status_code=400,
            detail="Study duration must be at least 1 day"
        )
    
    if len(request.forms) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one form is required"
        )
    
    # Validate frequencies
    for form in request.forms:
        if form.frequency_days < 1:
            raise HTTPException(
                status_code=400,
                detail=f"Form {form.form_id} has invalid frequency: {form.frequency_days}"
            )
    
    print(f"📅 Generating schedule for study: {request.study_id}")
    print(f"   Duration: {request.study_duration_days} days")
    print(f"   Forms: {len(request.forms)}")
    
    # Calculate schedule using LCM algorithm
    result = calculate_lcm_schedule(request)
    
    if result.success:
        print(f"✅ Schedule generated! Anchor cycle: {result.anchor_cycle_days} days")
    else:
        print(f"❌ Schedule generation failed: {result.error}")
    
    return result


# ============================================================================
# STUDY CONFIGURATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/studies/configure")
def configure_study(
    study_id: str,
    study_name: str,
    preset: Optional[str] = None,
    custom_ui: Optional[dict] = None,
    custom_features: Optional[dict] = None
):
    """Create or update study configuration."""
    try:
        # Create configuration based on input
        if preset == "simple_survey":
            config = StudyConfiguration.simple_survey(study_id, study_name)
        elif preset == "clinical_trial":
            config = StudyConfiguration.clinical_trial(study_id, study_name)
        elif preset == "minimal":
            config = StudyConfiguration.minimal(study_id, study_name)
        elif custom_ui or custom_features:
            # Build custom configuration
            ui_config = ParticipantUIConfig(**custom_ui) if custom_ui else ParticipantUIConfig()
            feature_config = StudyFeatures(**custom_features) if custom_features else StudyFeatures()
            
            config = StudyConfiguration(
                study_id=study_id,
                study_name=study_name,
                participant_ui=ui_config,
                features=feature_config
            )
        else:
            # Default to simple survey
            config = StudyConfiguration.simple_survey(study_id, study_name)
        
        # Validate configuration
        is_valid, errors = validate_configuration(config)
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "message": "Configuration validation failed"
            }
        
        return {
            "success": True,
            "configuration": config.model_dump(),
            "summary": config.summary(),
            "message": f"Study '{study_name}' configured successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create configuration"
        }


@app.get("/api/v1/studies/{study_id}/config")
def get_study_config(study_id: str):
    """Get study configuration."""
    # For now, return a demo config
    config = StudyConfiguration.clinical_trial(study_id, "Demo Study")
    
    return {
        "success": True,
        "configuration": config.model_dump(),
        "summary": config.summary()
    }


@app.post("/api/v1/studies/{study_id}/participant-view")
def get_participant_view(study_id: str, context: dict):
    """Get participant view data based on study configuration."""
    try:
        config = StudyConfiguration.clinical_trial(study_id, "Demo Study")
        view_data = config.get_participant_view_data(context)
        
        return {
            "success": True,
            "study_id": study_id,
            "view_data": view_data,
            "fields_shown": list(view_data.keys()),
            "fields_hidden": list(set(context.keys()) - set(view_data.keys()))
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/v1/studies/presets")
def list_presets():
    """List available configuration presets."""
    return {
        "presets": {
            "simple_survey": {
                "name": "Simple Survey",
                "description": "Minimal UI for short surveys and questionnaires",
                "best_for": "One-time surveys, feedback forms, quick assessments",
                "ui_elements": ["Progress bar", "Next form", "Completion message"],
                "features": ["Skip logic", "Validation", "Informed consent"]
            },
            "clinical_trial": {
                "name": "Clinical Trial",
                "description": "Full-featured UI for complex longitudinal studies",
                "best_for": "Multi-phase trials, long-term studies, research protocols",
                "ui_elements": [
                    "Progress bar", "Completion %", "Phase name", 
                    "Forms remaining", "Calendar view", "Missed forms"
                ],
                "features": [
                    "Skip logic", "Validation", "Help text",
                    "Informed consent", "Eligibility check", "Progress tracking"
                ]
            },
            "minimal": {
                "name": "Minimal",
                "description": "Absolute minimum UI - just forms",
                "best_for": "Very short assessments, single-question forms",
                "ui_elements": ["Completion message only"],
                "features": ["Validation", "Informed consent"]
            }
        }
    }


# ============================================================================
# INFORMED CONSENT ENDPOINTS
# ============================================================================

class CreateConsentRequest(BaseModel):
    """Request to create a consent form."""
    study_id: str
    study_title: str
    pi_name: str
    institution: str
    purpose: str
    procedures: str
    risks: str
    benefits: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    version: str = "v1.0"


class ConsentAcceptanceRequest(BaseModel):
    """Request to accept/sign a consent form."""
    participant_id: str
    participant_name: Optional[str] = None
    consent_form_id: str
    signature: str
    witness_signature: Optional[str] = None
    witness_name: Optional[str] = None
    ip_address: Optional[str] = None


@app.post("/api/v1/consent/create")
def create_consent_form(request: CreateConsentRequest):
    """Create an informed consent form."""
    try:
        # Create consent schema
        consent = create_standard_consent(
            study_id=request.study_id,
            study_title=request.study_title,
            pi_name=request.pi_name,
            institution=request.institution,
            purpose=request.purpose,
            procedures=request.procedures,
            risks=request.risks,
            benefits=request.benefits,
            contact_name=request.contact_name,
            contact_email=request.contact_email,
            version=request.version
        )
        
        # Validate
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_schema(consent)
        
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "message": "Consent validation failed"
            }
        
        return {
            "success": True,
            "consent": consent.model_dump(),
            "consent_hash": consent.get_hash(),
            "message": f"Consent form created: {consent.form_id}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create consent form"
        }


@app.get("/api/v1/consent/{consent_form_id}")
def get_consent_form(consent_form_id: str):
    """Get a consent form for display."""
    # Demo consent
    consent = create_standard_consent(
        study_id="DEMO_001",
        study_title="Demo Study",
        pi_name="Dr. Demo",
        institution="Demo University",
        purpose="This is a demonstration consent form.",
        procedures="Demo procedures.",
        risks="Demo risks.",
        benefits="Demo benefits.",
        contact_name="Dr. Demo",
        contact_email="demo@example.com"
    )
    
    return {
        "success": True,
        "consent": consent.model_dump()
    }


@app.post("/api/v1/consent/accept")
def accept_consent(request: ConsentAcceptanceRequest):
    """Accept/sign a consent form."""
    try:
        # Demo consent
        consent = create_standard_consent(
            study_id="DEMO_001",
            study_title="Demo Study",
            pi_name="Dr. Demo",
            institution="Demo University",
            purpose="Demo",
            procedures="Demo",
            risks="Demo",
            benefits="Demo",
            contact_name="Dr. Demo",
            contact_email="demo@example.com"
        )
        
        # Create consent record
        record = ConsentRecord(
            record_id=f"REC_{request.participant_id}_{datetime.now().timestamp()}",
            participant_id=request.participant_id,
            participant_name=request.participant_name,
            consent_form_id=request.consent_form_id,
            consent_version=consent.version,
            consent_hash=consent.get_hash(),
            signature=request.signature,
            witness_signature=request.witness_signature,
            witness_name=request.witness_name,
            ip_address=request.ip_address
        )
        
        # Validate acceptance
        validator = ConsentValidator()
        is_valid, errors = validator.validate_consent_acceptance(record, consent)
        
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "message": "Consent acceptance validation failed"
            }
        
        # Store record
        consent_manager.add_consent_record(record)
        
        return {
            "success": True,
            "record_id": record.record_id,
            "accepted_at": record.accepted_at.isoformat(),
            "message": "Consent accepted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to accept consent"
        }


@app.get("/api/v1/consent/status/{participant_id}")
def check_consent_status(participant_id: str, study_id: Optional[str] = None):
    """Check if participant has valid consent."""
    try:
        if study_id:
            has_consent, reason = consent_manager.has_consented(
                participant_id, 
                study_id
            )
        else:
            # Check for any consent
            latest = consent_manager.get_latest_consent(participant_id)
            has_consent = latest is not None and latest.is_active
            reason = None if has_consent else "No active consent found"
        
        return {
            "success": True,
            "participant_id": participant_id,
            "has_consent": has_consent,
            "reason": reason
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/v1/consent/withdraw")
def withdraw_consent_endpoint(
    participant_id: str,
    study_id: str,
    reason: Optional[str] = None
):
    """Withdraw participant's consent."""
    try:
        success = consent_manager.withdraw_consent(
            participant_id,
            study_id,
            reason
        )
        
        if success:
            return {
                "success": True,
                "message": "Consent withdrawn successfully"
            }
        else:
            return {
                "success": False,
                "message": "No active consent found to withdraw"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/v1/consent/history/{participant_id}")
def get_consent_history_endpoint(
    participant_id: str,
    study_id: Optional[str] = None
):
    """Get complete consent history for a participant."""
    try:
        history = consent_manager.get_consent_history(
            participant_id,
            study_id
        )
        
        return {
            "success": True,
            "participant_id": participant_id,
            "consent_count": len(history),
            "consents": [record.model_dump() for record in history]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# DATABASE ENDPOINTS
# ============================================================================

@app.post("/api/v1/studies/create")
def create_study_endpoint(
    name: str,
    description: str = "",
    db = Depends(get_db)
):
    """
    Create a new study and store in database.
    
    Example:
        POST /api/v1/studies/create?name=My+Study&description=Test+study
    """
    try:
        study = create_study(db, name, description)
        return {
            "success": True,
            "study_id": study.id,
            "name": study.name,
            "description": study.description,
            "created_at": study.created_at.isoformat(),
            "message": f"Study '{name}' created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create study"
        }


@app.get("/api/v1/studies")
def list_studies(db = Depends(get_db)):
    """
    Get all studies from database.
    
    Example:
        GET /api/v1/studies
    """
    try:
        studies = get_all_studies(db)
        return {
            "success": True,
            "count": len(studies),
            "studies": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "created_at": s.created_at.isoformat(),
                    "form_count": len(s.forms)
                }
                for s in studies
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "studies": []
        }


@app.get("/api/v1/studies/{study_id}")
def get_study_details_endpoint(study_id: int, db = Depends(get_db)):
    """
    Get detailed information about a study.
    
    Example:
        GET /api/v1/studies/1
    """
    try:
        study = get_study(db, study_id)
        if not study:
            return {
                "success": False,
                "error": "Study not found"
            }
        
        return {
            "success": True,
            "study": {
                "id": study.id,
                "name": study.name,
                "description": study.description,
                "created_at": study.created_at.isoformat(),
                "forms": [
                    {
                        "id": f.id,
                        "form_id": f.form_id,
                        "title": f.title,
                        "frequency": f.frequency,
                        "created_at": f.created_at.isoformat()
                    }
                    for f in study.forms
                ],
                "form_count": len(study.forms),
                "completion_count": len(study.completions)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Form Generator API...")
    print("=" * 60)
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔐 Auth endpoints: http://localhost:8000/api/v1/auth/*")
    print("🤖 AI Agent endpoints: http://localhost:8000/api/v1/ai/*")
    print("=" * 60)
    print("🤖 AI Agents Available:")
    print("   1. Form Designer - Natural language → JSON forms")
    print("   2. Schedule Optimizer - LCM scheduling with AI reasoning")
    print("   3. Policy Recommender - Validation & skip logic suggestions")
    print("   4. Clinical Compliance - GCP/HIPAA regulatory checks")
    print("   5. Reflection QA - Quality review & scoring")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)