# --- Load environment first ---
import os, json, re
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
from scheduler import calculate_lcm_schedule, ScheduleRequest, ScheduleResponse

app = FastAPI(title="AI Form Generator API")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# CORS for frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt for Claude to generate form schemas
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
      "help_text": "Optional guidance"
    }
  ]
}

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
- Always include sensible validation rules
- Make field_id snake_case, no spaces
- Make labels clear and user-friendly"""

# Request/Response models
class FormGenerationRequest(BaseModel):
    prompt: str
    model: str = "claude-sonnet-4-20250514"

class FormGenerationResponse(BaseModel):
    success: bool
    form_id: str | None = None
    form_schema: dict | None = None
    error: str | None = None
    raw_response: str | None = None

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Form Generator API - Running",
        "endpoints": {
            "health": "/health",
            "generate_form": "/api/v1/forms/generate",
            "generate_schedule": "/api/v1/schedule/generate",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    api_key_present = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "ok": True,
        "api_key_configured": api_key_present,
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
    }

@app.post("/api/v1/forms/generate", response_model=FormGenerationResponse)
async def generate_form(request: FormGenerationRequest):
    """Generate a form schema from natural language prompt using Claude AI."""
    
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
        
        # Clean markdown
        cleaned = response_text.strip()
        cleaned = re.sub(r'^```json\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()
        
        schema = json.loads(cleaned)
        
        if "form_id" not in schema or "fields" not in schema:
            return FormGenerationResponse(
                success=False,
                error="Invalid schema structure",
                raw_response=response_text[:500]
            )
        
        print(f"✅ Generated form: {schema.get('form_id')}")
        
        return FormGenerationResponse(
            success=True,
            form_id=schema.get("form_id"),
            form_schema=schema
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return FormGenerationResponse(
            success=False,
            error=str(e)
        )

class EchoIn(BaseModel):
    message: str
    meta: dict | None = None

@app.post("/echo")
def echo(payload: EchoIn):
    return {"you_sent": payload.model_dump()}

@app.post("/api/v1/schedule/generate", response_model=ScheduleResponse)
async def generate_schedule(request: ScheduleRequest):
    """
    Generate an LCM-based schedule for multiple forms.
    
    Example:
        POST /api/v1/schedule/generate
        {
            "study_id": "study_001",
            "study_duration_days": 28,
            "forms": [
                {"form_id": "daily_diary", "frequency_days": 1, "frequency_label": "Daily"},
                {"form_id": "weekly_assessment", "frequency_days": 7, "frequency_label": "Weekly"}
            ]
        }
    """
    
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Form Generator API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
