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
- Multi-role authentication system
- Event Trigger System (Day 2 - NEW!)
- Schedule Optimizer AI Agent (Day 2 - ENHANCED!)
- CONVERSATIONAL AI (Day 4 - NEW!)

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
from typing import Optional, List
from datetime import datetime, date

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
from .database import (
    init_db, get_db, 
    create_study, create_form, create_day_type,
    get_all_studies, get_study, get_forms_by_study
)

# Authentication
from .auth_database import init_db as init_auth_db
from .auth_api import router as auth_router, get_current_user
from .designer_api import router as designer_router

# Local modules
from .scheduler import calculate_lcm_schedule, ScheduleRequest, ScheduleResponse
from .study_config import (
    StudyConfiguration,
    ParticipantUIConfig,
    StudyFeatures,
    validate_configuration
)
from .skip_logic import (
    SkipLogicEvaluator,
    SkipLogicRule,
    SkipCondition,
    add_skip_logic_to_field
)
from .consent import (
    ConsentSchema,
    ConsentRecord,
    ConsentValidator,
    ConsentManager,
    create_standard_consent,
    ConsentType
)

# Event Handler (NEW!)
from .event_handler import (
    EventHandler,
    DayTypeDefinition,
    DayTypePriority,
    create_default_event_handler
)

# AI Agents
from .agents.base_agent import BaseAgent
from .agents.form_designer_agent import FormDesignerAgent
from .agents.schedule_optimizer_agent import ScheduleOptimizerAgent
from .agents.policy_recommender_agent import PolicyRecommenderAgent
from .agents.clinical_compliance_agent import ClinicalComplianceAgent
from .agents.reflection_qa_agent import ReflectionQAAgent

# Conditional Engine (NEW! - DAY 3)
from .conditional_engine import ConditionalEngine, ConditionalRule, ConditionType

# Conversational AI (NEW! - DAY 4)
from .conversation_manager import ConversationManager
from .langgraph_orchestrator import LangGraphOrchestrator


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="AI Form Generator API",
    description="AI-powered clinical research form generation and scheduling with multi-role authentication, event system, and conversational AI",
    version="2.2.0"
)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
consent_manager = ConsentManager()

# Initialize conversation manager (NEW! - DAY 4)
conversation_manager = ConversationManager()

# AI Agents (initialized on startup)
form_designer = None
schedule_optimizer = None
policy_recommender = None
compliance_checker = None
qa_reviewer = None

# Event Handler (initialized on startup) - NEW!
event_handler = None

# Conditional Engine (initialized on startup) - NEW!
conditional_engine = None

# In-memory storage for events (in production, use database)
# This is a simple implementation for Day 2 - will be enhanced with database on Day 5
events_store = {}  # {study_id: {subject_id: [events]}}

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize databases, AI agents, and event handler on startup."""
    global form_designer, schedule_optimizer, policy_recommender, compliance_checker, qa_reviewer, event_handler, conditional_engine
    
    # Initialize databases
    print("✅ Database initialized successfully")
    init_db()  # Research forms database
    init_auth_db()  # Authentication database
    print("✅ Database initialized")
    
    # Initialize AI Agents
    print("🤖 Initializing AI Agents...")
    form_designer = FormDesignerAgent()
    schedule_optimizer = ScheduleOptimizerAgent()
    policy_recommender = PolicyRecommenderAgent()
    compliance_checker = ClinicalComplianceAgent()
    qa_reviewer = ReflectionQAAgent()
    print("✅ All 5 AI agents initialized successfully!")
    
    # Initialize Event Handler (NEW!)
    print("⚡ Initializing Event Handler...")
    event_handler = create_default_event_handler()
    print("✅ Event handler initialized with default day types!")
    
    # Initialize Conditional Engine (NEW! - DAY 3)
    print("🔗 Initializing Conditional Engine...")
    conditional_engine = ConditionalEngine()
    print("✅ Conditional engine initialized!")
    
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

# Include authentication router
app.include_router(auth_router)
app.include_router(designer_router)


# ============================================================================
# SYSTEM PROMPT FOR AI FORM GENERATION
# ============================================================================

SYSTEM_PROMPT = """You are an expert clinical research form designer with metadata intelligence. Convert the user's description into a valid JSON response with TWO parts:
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
      },
      {
        "field": "phase_name",
        "why": "Identifies which study phase this data belongs to",
        "how": "Set based on current phase",
        "example": "Treatment Phase",
        "applies_if": "Study has multiple phases"
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

EXAMPLES:

Example 1: Personal Tracker
Input: "Track my water intake daily for 7 days"
study_type: "personal_tracker", recommended_tier: 1
form_schema.fields: [water_cups, notes]
metadata_suggestions: Only submission_timestamp in required

Example 2: Clinical Trial
Input: "30-day depression study with daily mood, weekly QoL, baseline and follow-up assessments"
study_type: "clinical_trial", recommended_tier: 3, has_phases: true
form_schema.fields: [mood_score, energy_level, sleep_quality, etc.]
metadata_suggestions: submission_timestamp, study_day, phase_name, visit_number

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


# --- Event System Models (NEW!) ---

class EventTriggerRequest(BaseModel):
    """Request to trigger an event."""
    study_id: int = Field(description="Study ID")
    subject_id: int = Field(description="Subject ID")
    event_type: str = Field(description="Type: baseline, eot, early_termination, adverse_event, protocol_deviation")
    event_name: str = Field(description="Human-readable event name")
    trigger_day: int = Field(description="Study day when event occurred")
    metadata: Optional[dict] = None


class EventTriggerResponse(BaseModel):
    """Response from event trigger."""
    success: bool
    event_id: str
    triggered_forms: List[str]
    priority_explanation: dict
    message: str
    error: Optional[str] = None


class EventStatusResponse(BaseModel):
    """Response with event status for a study."""
    success: bool
    study_id: int
    total_events: int
    events_by_type: dict
    recent_events: List[dict]
    error: Optional[str] = None


class ScheduleRecalculationRequest(BaseModel):
    """Request to recalculate schedule based on event."""
    study_id: int
    subject_id: int
    event_day: int
    event_type: str


class ScheduleRecalculationResponse(BaseModel):
    """Response from schedule recalculation."""
    success: bool
    affected_days: List[int]
    new_schedule: dict
    changes_summary: str
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
        "message": "AI Form Generator API - Running with AI Agents, Authentication, Event System & Conversational AI",
        "version": "2.2.0",
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
            "conversation_ai": "/api/v1/conversation/*",
            "schedule_generation": "/api/v1/schedule/generate",
            "event_trigger": "/api/v1/events/trigger",
            "event_status": "/api/v1/events/status/{study_id}",
            "schedule_recalculate": "/api/v1/events/recalculate",
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
        },
        "new_features": {
            "event_system": "Trigger events that override regular schedules (baseline, EOT, early termination)",
            "priority_resolution": "Events always win over regular schedules - bulletproof clash prevention",
            "conversational_ai": "Natural language study creation with multi-turn dialogue (DAY 4)"
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
        "event_handler_initialized": event_handler is not None,
        "conversation_manager_initialized": conversation_manager is not None,
        "ai_agents": {
            "form_designer": form_designer is not None,
            "schedule_optimizer": schedule_optimizer is not None,
            "policy_recommender": policy_recommender is not None,
            "compliance_checker": compliance_checker is not None,
            "qa_reviewer": qa_reviewer is not None
        },
        "event_system": {
            "handler_ready": event_handler is not None,
            "registered_day_types": len(event_handler.day_types) if event_handler else 0
        },
        "conversational_ai": {
            "manager_ready": conversation_manager is not None,
            "active_conversations": len(conversation_manager.conversations) if conversation_manager else 0
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
        
        # Validate NEW structure with metadata intelligence
        if "form_schema" not in schema:
            return FormGenerationResponse(
                success=False,
                error="Invalid schema structure: missing form_schema",
                raw_response=response_text[:500]
            )
        
        form_schema = schema.get("form_schema", {})
        
        if "form_id" not in form_schema or "fields" not in form_schema:
            return FormGenerationResponse(
                success=False,
                error="Invalid form_schema structure: missing form_id or fields",
                raw_response=response_text[:500]
            )
        
        # Extract metadata intelligence
        study_classification = schema.get("study_classification", {})
        metadata_suggestions = schema.get("metadata_suggestions", {})
        
        print(f"✅ Generated form: {form_schema.get('form_id')}")
        print(f"📊 Study type: {study_classification.get('study_type', 'unknown')}")
        print(f"🏷️  Metadata tier: {study_classification.get('recommended_tier', 1)}")
        
        # Return the complete schema (for backward compatibility, we include form_schema at top level)
        return FormGenerationResponse(
            success=True,
            form_id=form_schema.get("form_id"),
            form_schema=schema  # Return the FULL schema including metadata
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
# AI AGENT ENDPOINTS
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
    
    This endpoint combines the LCM algorithm (scheduler.py) with AI reasoning
    to explain WHY the schedule is optimal and provide recommendations.
    
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
                "form_name": f"Form_{i+1}",
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
        print(f"📊 AI Reasoning: {result.get('schedule_rationale', '')[:100]}...")
        
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
        result = qa_reviewer.review_output(
            agent_name=f"{request.review_type.title()} Content",
            output=request.content,
            context=f"Reviewing {request.review_type} for quality assurance"
        )
        
        print(f"✅ Quality review complete")
        
        return AIQAResponse(
            success=True,
            quality_score=result.get('quality_score'),
            feedback=result
        )
        
    except Exception as e:
        print(f"❌ AI Quality Review Error: {e}")
        return AIQAResponse(
            success=False,
            error=str(e)
        )


# ============================================================================
# CONVERSATIONAL AI ENDPOINTS (NEW! - DAY 4)
# ============================================================================

@app.post("/api/v1/conversation/start")
async def start_conversation(
    current_user: dict = Depends(get_current_user)
):
    """Start a new conversational study creation session"""
    try:
        user_id = str(current_user.user_id)
        result = conversation_manager.start_conversation(user_id)
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/conversation/message")
async def send_conversation_message(
    message: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send a message in the conversation"""
    try:
        msg = message.get("message", "")
        
        if not msg:
            raise HTTPException(status_code=400, detail="Message is required")
        
        user_id = str(current_user.user_id)
        result = conversation_manager.send_message(user_id, msg)
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/conversation/get/{user_id}")
async def get_conversation(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get conversation history for a user"""
    try:
        # Verify user can only access their own conversation
        if str(current_user.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = conversation_manager.get_conversation(user_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/conversation/clear/{user_id}")
async def clear_conversation(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Clear conversation history for a user"""
    try:
        # Verify user can only clear their own conversation
        if str(current_user.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = conversation_manager.clear_conversation(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "status": "success",
            "message": "Conversation cleared"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/conversation/create-study")
async def create_study_from_conversation(
    description: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger study creation from conversation
    (Usually happens automatically, but this endpoint allows manual triggering)
    """
    try:
        desc = description.get("description", "")
        
        if not desc:
            raise HTTPException(status_code=400, detail="Description is required")
        
        user_id = str(current_user.user_id)
        orchestrator = LangGraphOrchestrator()
        result = orchestrator.create_study(desc, user_id)
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EVENT TRIGGER SYSTEM ENDPOINTS (NEW! - DAY 2)
# ============================================================================

@app.post("/api/v1/events/trigger", response_model=EventTriggerResponse)
async def trigger_event(request: EventTriggerRequest):
    """
    Trigger an event that overrides regular schedule.
    
    Events always take priority over regular day types.
    
    Event Types:
    - baseline: Study start (consent, demographics)
    - eot: End of Treatment (final assessments)
    - early_termination: Early withdrawal (exit questionnaire)
    - adverse_event: Safety reporting
    - protocol_deviation: Protocol violation
    
    Example:
        POST /api/v1/events/trigger
        {
            "study_id": 1,
            "subject_id": 101,
            "event_type": "adverse_event",
            "event_name": "Headache reported",
            "trigger_day": 15,
            "metadata": {"severity": "mild"}
        }
    """
    if not event_handler:
        return EventTriggerResponse(
            success=False,
            event_id="",
            triggered_forms=[],
            priority_explanation={},
            message="Event handler not initialized",
            error="Event handler not initialized"
        )
    
    try:
        print(f"⚡ Event Trigger: {request.event_type} for subject {request.subject_id} on day {request.trigger_day}")
        
        # Map event type to day type ID
        event_type_map = {
            "baseline": "EVENT_BASELINE",
            "eot": "EVENT_EOT",
            "early_termination": "EVENT_EARLY_TERM",
            "adverse_event": "EVENT_ADVERSE",
            "protocol_deviation": "EVENT_DEVIATION"
        }
        
        day_type_id = event_type_map.get(request.event_type.lower())
        
        if not day_type_id:
            return EventTriggerResponse(
                success=False,
                event_id="",
                triggered_forms=[],
                priority_explanation={},
                message=f"Unknown event type: {request.event_type}",
                error=f"Unknown event type: {request.event_type}"
            )
        
        # Get the forms that should be triggered
        # For now, assume regular schedule might include A_ONLY or AB
        candidate_day_types = ["A_ONLY", "AB", day_type_id]
        
        # Use event handler to determine what should happen
        active_day_type = event_handler.determine_active_day_type(candidate_day_types)
        triggered_forms = active_day_type.forms if active_day_type else []
        
        # Get priority explanation
        explanation = event_handler.get_priority_explanation(candidate_day_types)
        
        # Generate event ID
        event_id = f"EVT_{request.study_id}_{request.subject_id}_{request.trigger_day}_{datetime.now().timestamp()}"
        
        # Store event in memory (in production, save to database)
        if request.study_id not in events_store:
            events_store[request.study_id] = {}
        if request.subject_id not in events_store[request.study_id]:
            events_store[request.study_id][request.subject_id] = []
        
        events_store[request.study_id][request.subject_id].append({
            "event_id": event_id,
            "event_type": request.event_type,
            "event_name": request.event_name,
            "trigger_day": request.trigger_day,
            "triggered_at": datetime.now().isoformat(),
            "triggered_forms": triggered_forms,
            "metadata": request.metadata or {}
        })
        
        print(f"✅ Event triggered: {len(triggered_forms)} forms activated")
        print(f"📋 Forms: {triggered_forms}")
        
        return EventTriggerResponse(
            success=True,
            event_id=event_id,
            triggered_forms=triggered_forms,
            priority_explanation=explanation,
            message=f"Event '{request.event_name}' triggered successfully. {len(triggered_forms)} forms activated."
        )
        
    except Exception as e:
        print(f"❌ Event Trigger Error: {e}")
        import traceback
        traceback.print_exc()
        return EventTriggerResponse(
            success=False,
            event_id="",
            triggered_forms=[],
            priority_explanation={},
            message="Failed to trigger event",
            error=str(e)
        )


@app.get("/api/v1/events/status/{study_id}", response_model=EventStatusResponse)
async def get_event_status(study_id: int):
    """
    Get event status for a study.
    
    Returns:
    - Total event count
    - Events grouped by type
    - Recent events (last 10)
    
    Example:
        GET /api/v1/events/status/1
    """
    try:
        print(f"📊 Getting event status for study {study_id}")
        
        if study_id not in events_store:
            return EventStatusResponse(
                success=True,
                study_id=study_id,
                total_events=0,
                events_by_type={},
                recent_events=[]
            )
        
        # Collect all events for this study across all subjects
        all_events = []
        events_by_type = {}
        
        for subject_id, events in events_store[study_id].items():
            for event in events:
                all_events.append({
                    "subject_id": subject_id,
                    **event
                })
                
                event_type = event['event_type']
                if event_type not in events_by_type:
                    events_by_type[event_type] = 0
                events_by_type[event_type] += 1
        
        # Sort by triggered_at (most recent first)
        all_events.sort(key=lambda e: e['triggered_at'], reverse=True)
        
        # Get recent 10
        recent_events = all_events[:10]
        
        print(f"✅ Found {len(all_events)} events for study {study_id}")
        
        return EventStatusResponse(
            success=True,
            study_id=study_id,
            total_events=len(all_events),
            events_by_type=events_by_type,
            recent_events=recent_events
        )
        
    except Exception as e:
        print(f"❌ Event Status Error: {e}")
        return EventStatusResponse(
            success=False,
            study_id=study_id,
            total_events=0,
            events_by_type={},
            recent_events=[],
            error=str(e)
        )


@app.post("/api/v1/events/recalculate", response_model=ScheduleRecalculationResponse)
async def recalculate_schedule(request: ScheduleRecalculationRequest):
    """
    Recalculate schedule based on an event.
    
    When an event occurs, this endpoint determines:
    1. Which days are affected
    2. How the schedule changes
    3. What forms should now appear
    
    This is a simplified version for Day 2. Full implementation will
    integrate with scheduler.py and database on Day 5.
    
    Example:
        POST /api/v1/events/recalculate
        {
            "study_id": 1,
            "subject_id": 101,
            "event_day": 15,
            "event_type": "eot"
        }
    """
    if not event_handler:
        return ScheduleRecalculationResponse(
            success=False,
            affected_days=[],
            new_schedule={},
            changes_summary="Event handler not initialized",
            error="Event handler not initialized"
        )
    
    try:
        print(f"🔄 Recalculating schedule for subject {request.subject_id} after {request.event_type} event")
        
        # Map event type to day type
        event_type_map = {
            "baseline": "EVENT_BASELINE",
            "eot": "EVENT_EOT",
            "early_termination": "EVENT_EARLY_TERM"
        }
        
        day_type_id = event_type_map.get(request.event_type.lower())
        
        if not day_type_id:
            return ScheduleRecalculationResponse(
                success=False,
                affected_days=[],
                new_schedule={},
                changes_summary=f"Unknown event type: {request.event_type}",
                error=f"Unknown event type: {request.event_type}"
            )
        
        # For Day 2, we'll do a simplified recalculation
        # Full implementation with scheduler.py integration comes on Day 5
        
        # Event overrides day it occurs on
        affected_days = [request.event_day]
        
        # Get forms that should appear
        event_day_type = event_handler.get_day_type(day_type_id)
        triggered_forms = event_day_type.forms if event_day_type else []
        
        # Create simplified schedule update
        new_schedule = {
            str(request.event_day): {
                "day_type": day_type_id,
                "forms": triggered_forms,
                "is_event": True,
                "reason": f"Event {request.event_type} overrides regular schedule"
            }
        }
        
        changes_summary = f"Day {request.event_day} changed to {day_type_id} with {len(triggered_forms)} forms"
        
        print(f"✅ Schedule recalculated: {len(affected_days)} days affected")
        
        return ScheduleRecalculationResponse(
            success=True,
            affected_days=affected_days,
            new_schedule=new_schedule,
            changes_summary=changes_summary
        )
        
    except Exception as e:
        print(f"❌ Schedule Recalculation Error: {e}")
        return ScheduleRecalculationResponse(
            success=False,
            affected_days=[],
            new_schedule={},
            changes_summary="Failed to recalculate schedule",
            error=str(e)
        )


# ============================================================================
# CONDITIONAL DEPENDENCIES ENDPOINTS (NEW! - DAY 3)
# ============================================================================

class ConditionalCheckRequest(BaseModel):
    """Request to check if a condition is met."""
    study_id: int
    subject_id: int
    condition_type: str = Field(description="Type: form_completed, phase_reached, event_triggered")
    condition_value: str = Field(description="Value to check (form_id, phase_name, event_type)")


class ConditionalCheckResponse(BaseModel):
    """Response from condition check."""
    success: bool
    condition_met: bool
    message: str
    error: Optional[str] = None


class ConditionalActivateRequest(BaseModel):
    """Request to activate forms."""
    study_id: int
    subject_id: int
    form_ids: List[str] = Field(description="Forms to activate")
    reason: Optional[str] = None


class ConditionalActivateResponse(BaseModel):
    """Response from form activation."""
    success: bool
    activated_count: int
    activated_forms: List[str]
    message: str
    error: Optional[str] = None


class ConditionalStatusResponse(BaseModel):
    """Response with subject's activation status."""
    success: bool
    subject_id: int
    active_forms: List[str]
    completed_forms: List[str]
    current_phase: str
    triggered_events: List[str]
    error: Optional[str] = None


@app.post("/api/v1/conditional/check", response_model=ConditionalCheckResponse)
async def check_condition(request: ConditionalCheckRequest):
    """
    Check if a condition is met for a subject.
    
    Condition Types:
    - form_completed: Check if a form is complete
    - phase_reached: Check if subject is in a phase
    - event_triggered: Check if an event occurred
    
    Example:
        POST /api/v1/conditional/check
        {
            "study_id": 1,
            "subject_id": 101,
            "condition_type": "form_completed",
            "condition_value": "baseline_assessment"
        }
    """
    if not conditional_engine:
        return ConditionalCheckResponse(
            success=False,
            condition_met=False,
            message="Conditional engine not initialized",
            error="Conditional engine not initialized"
        )
    
    try:
        print(f"🔍 Checking condition: {request.condition_type} = {request.condition_value}")
        
        # Map string to enum
        condition_type_map = {
            "form_completed": ConditionType.FORM_COMPLETED,
            "phase_reached": ConditionType.PHASE_REACHED,
            "event_triggered": ConditionType.EVENT_TRIGGERED
        }
        
        condition_type = condition_type_map.get(request.condition_type.lower())
        if not condition_type:
            return ConditionalCheckResponse(
                success=False,
                condition_met=False,
                message=f"Unknown condition type: {request.condition_type}",
                error=f"Unknown condition type: {request.condition_type}"
            )
        
        # Check the condition
        is_met = conditional_engine.check_condition(
            request.subject_id,
            condition_type,
            request.condition_value
        )
        
        message = f"Condition {'MET' if is_met else 'NOT MET'}: {request.condition_type} = {request.condition_value}"
        print(f"✅ {message}")
        
        return ConditionalCheckResponse(
            success=True,
            condition_met=is_met,
            message=message
        )
        
    except Exception as e:
        print(f"❌ Condition Check Error: {e}")
        return ConditionalCheckResponse(
            success=False,
            condition_met=False,
            message="Failed to check condition",
            error=str(e)
        )


@app.post("/api/v1/conditional/activate", response_model=ConditionalActivateResponse)
async def activate_forms(request: ConditionalActivateRequest):
    """
    Activate forms for a subject.
    
    This is typically called automatically when conditions are met,
    but can also be called manually.
    
    Example:
        POST /api/v1/conditional/activate
        {
            "study_id": 1,
            "subject_id": 101,
            "form_ids": ["treatment_form_1", "treatment_form_2"],
            "reason": "Baseline completed"
        }
    """
    if not conditional_engine:
        return ConditionalActivateResponse(
            success=False,
            activated_count=0,
            activated_forms=[],
            message="Conditional engine not initialized",
            error="Conditional engine not initialized"
        )
    
    try:
        print(f"🔓 Activating {len(request.form_ids)} forms for subject {request.subject_id}")
        
        # Activate the forms
        conditional_engine.activate_forms(request.subject_id, request.form_ids)
        
        message = f"Activated {len(request.form_ids)} forms for subject {request.subject_id}"
        if request.reason:
            message += f" (Reason: {request.reason})"
        
        print(f"✅ {message}")
        
        return ConditionalActivateResponse(
            success=True,
            activated_count=len(request.form_ids),
            activated_forms=request.form_ids,
            message=message
        )
        
    except Exception as e:
        print(f"❌ Form Activation Error: {e}")
        return ConditionalActivateResponse(
            success=False,
            activated_count=0,
            activated_forms=[],
            message="Failed to activate forms",
            error=str(e)
        )


@app.get("/api/v1/conditional/status/{subject_id}", response_model=ConditionalStatusResponse)
async def get_conditional_status(subject_id: int, study_id: Optional[int] = None):
    """
    Get complete conditional status for a subject.
    
    Returns:
    - Active forms
    - Completed forms
    - Current phase
    - Triggered events
    
    Example:
        GET /api/v1/conditional/status/101?study_id=1
    """
    if not conditional_engine:
        return ConditionalStatusResponse(
            success=False,
            subject_id=subject_id,
            active_forms=[],
            completed_forms=[],
            current_phase="Unknown",
            triggered_events=[],
            error="Conditional engine not initialized"
        )
    
    try:
        print(f"📊 Getting conditional status for subject {subject_id}")
        
        # Get status summary
        status = conditional_engine.get_status_summary(subject_id)
        
        print(f"✅ Status retrieved: {status['total_active']} active, {status['total_complete']} complete")
        
        return ConditionalStatusResponse(
            success=True,
            subject_id=subject_id,
            active_forms=status['active_forms'],
            completed_forms=status['completed_forms'],
            current_phase=status['current_phase'],
            triggered_events=status['triggered_events']
        )
        
    except Exception as e:
        print(f"❌ Status Retrieval Error: {e}")
        return ConditionalStatusResponse(
            success=False,
            subject_id=subject_id,
            active_forms=[],
            completed_forms=[],
            current_phase="Unknown",
            triggered_events=[],
            error=str(e)
        )


class MarkCompleteRequest(BaseModel):
    """Request to mark a form as complete."""
    study_id: int
    subject_id: int
    form_id: str


class MarkCompleteResponse(BaseModel):
    """Response from marking form complete."""
    success: bool
    message: str
    triggered_activations: List[str] = []
    error: Optional[str] = None


@app.post("/api/v1/conditional/mark-complete", response_model=MarkCompleteResponse)
async def mark_form_complete(request: MarkCompleteRequest):
    """
    Mark a form as complete for a subject.
    
    This triggers any conditional rules that depend on this form.
    
    Example:
        POST /api/v1/conditional/mark-complete
        {
            "study_id": 1,
            "subject_id": 101,
            "form_id": "baseline_assessment"
        }
    """
    if not conditional_engine:
        return MarkCompleteResponse(
            success=False,
            message="Conditional engine not initialized",
            error="Conditional engine not initialized"
        )
    
    try:
        print(f"✅ Marking form '{request.form_id}' complete for subject {request.subject_id}")
        
        # Mark the form complete (this will auto-trigger any rules)
        conditional_engine.mark_form_complete(request.subject_id, request.form_id)
        
        # Get newly activated forms
        active_forms = conditional_engine.get_active_forms(request.subject_id)
        
        message = f"Form '{request.form_id}' marked complete for subject {request.subject_id}"
        print(f"✅ {message}")
        
        return MarkCompleteResponse(
            success=True,
            message=message,
            triggered_activations=active_forms
        )
        
    except Exception as e:
        print(f"❌ Mark Complete Error: {e}")
        return MarkCompleteResponse(
            success=False,
            message="Failed to mark form complete",
            error=str(e)
        )


class AddRuleRequest(BaseModel):
    """Request to add a conditional rule."""
    rule_id: str
    condition_type: str
    condition_value: str
    target_forms: List[str]
    description: Optional[str] = ""


class AddRuleResponse(BaseModel):
    """Response from adding rule."""
    success: bool
    rule_id: str
    message: str
    error: Optional[str] = None


@app.post("/api/v1/conditional/add-rule", response_model=AddRuleResponse)
async def add_conditional_rule(request: AddRuleRequest):
    """
    Add a conditional rule.
    
    Example:
        POST /api/v1/conditional/add-rule
        {
            "rule_id": "baseline_to_treatment",
            "condition_type": "form_completed",
            "condition_value": "baseline_assessment",
            "target_forms": ["treatment_form_1", "treatment_form_2"],
            "description": "Activate treatment forms after baseline"
        }
    """
    if not conditional_engine:
        return AddRuleResponse(
            success=False,
            rule_id="",
            message="Conditional engine not initialized",
            error="Conditional engine not initialized"
        )
    
    try:
        # Map string to enum
        condition_type_map = {
            "form_completed": ConditionType.FORM_COMPLETED,
            "phase_reached": ConditionType.PHASE_REACHED,
            "event_triggered": ConditionType.EVENT_TRIGGERED
        }
        
        condition_type = condition_type_map.get(request.condition_type.lower())
        if not condition_type:
            return AddRuleResponse(
                success=False,
                rule_id="",
                message=f"Unknown condition type: {request.condition_type}",
                error=f"Unknown condition type: {request.condition_type}"
            )
        
        # Create and add rule
        rule = ConditionalRule(
            rule_id=request.rule_id,
            condition_type=condition_type,
            condition_value=request.condition_value,
            target_forms=request.target_forms,
            description=request.description
        )
        
        conditional_engine.add_rule(rule)
        
        message = f"Rule '{request.rule_id}' added successfully"
        print(f"✅ {message}")
        
        return AddRuleResponse(
            success=True,
            rule_id=request.rule_id,
            message=message
        )
        
    except Exception as e:
        print(f"❌ Add Rule Error: {e}")
        return AddRuleResponse(
            success=False,
            rule_id="",
            message="Failed to add rule",
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
    print("⚡ Event System endpoints: http://localhost:8000/api/v1/events/*")
    print("💬 Conversation endpoints: http://localhost:8000/api/v1/conversation/*")
    print("=" * 60)
    print("🤖 AI Agents Available:")
    print("   1. Form Designer - Natural language → JSON forms")
    print("   2. Schedule Optimizer - LCM scheduling with AI reasoning")
    print("   3. Policy Recommender - Validation & skip logic suggestions")
    print("   4. Clinical Compliance - GCP/HIPAA regulatory checks")
    print("   5. Reflection QA - Quality review & scoring")
    print("=" * 60)
    print("⚡ Event System Features:")
    print("   • Trigger events (baseline, EOT, early termination)")
    print("   • Priority resolution (events override regular schedule)")
    print("   • Schedule recalculation on event trigger")
    print("   • Event status tracking per study")
    print("=" * 60)
    print("💬 Conversational AI:")
    print("   • Natural language study creation")
    print("   • Multi-turn dialogue with context retention")
    print("   • Schedule preview before creation")
    print("   • Integrated with LangGraph orchestrator")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)