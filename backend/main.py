"""
FastAPI Backend for KNIGHTHACKS-VIII-Morgan
AI Legal Tender Multi-Agent System
"""

print("[DEBUG] main.py is being loaded...")

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

# Import orchestrator router function
from orchestrator.router import process_case_file

# Import Twilio service (optional - will use mock mode if import fails)
try:
    from utils.twilio_service import twilio_service
    TWILIO_AVAILABLE = True
    print("[OK] Twilio service loaded successfully")
except Exception as e:
    print(f"[WARNING] Twilio service failed to load: {e}")
    print("[WARNING] Running in mock mode")
    TWILIO_AVAILABLE = False
    twilio_service = None

# Import Calendar service (optional - will use mock mode if import fails)
try:
    from utils.calendar_service import calendar_service
    CALENDAR_AVAILABLE = True
    print("[OK] Calendar service loaded successfully")
except Exception as e:
    print(f"[WARNING] Calendar service failed to load: {e}")
    print("[WARNING] Running in mock mode")
    CALENDAR_AVAILABLE = False
    calendar_service = None


# Initialize FastAPI app
app = FastAPI(
    title="KNIGHTHACKS-VIII-Morgan API",
    description="AI Multi-Agent Backend for Legal Case Processing",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint to confirm server is running.
    
    Returns:
        dict: Server status message
    """
    return {
        "status": "running",
        "message": "KNIGHTHACKS-VIII-Morgan API is operational",
        "project": "AI Legal Tender Multi-Agent System",
        "version": "1.0.0"
    }


@app.post("/process_file")
async def upload_case_file(file: UploadFile = File(...)):
    """
    Process uploaded .txt case file through AI orchestrator.
    
    Args:
        file: Uploaded .txt file containing case information
        
    Returns:
        dict: Structured JSON output from orchestrator with agent results
        
    Raises:
        HTTPException: If file is not .txt or processing fails
    """
    # Validate file type
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Process through orchestrator
        result = await process_case_file(text)
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be valid UTF-8 encoded text"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


# ============================================
# Twilio Voice Call Endpoints
# ============================================

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify routes are working"""
    return {"status": "test endpoint works"}


class CallRequest(BaseModel):
    """Request model for initiating a call"""
    to_number: str
    case_id: Optional[str] = "UNKNOWN"
    client_name: Optional[str] = "Client"
    from_number: Optional[str] = None


class SMSRequest(BaseModel):
    """Request model for sending SMS"""
    to_number: str
    message: str
    from_number: Optional[str] = None


@app.post("/api/calls/initiate")
async def initiate_call(request: CallRequest):
    """
    Initiate a phone call to client
    
    Request body:
    {
        "to_number": "+15551234567",
        "case_id": "2024-PI-9999",
        "client_name": "Sarah Martinez",
        "from_number": "+15559876543"  // optional
    }
    
    Returns:
        Call details including SID and status
    """
    if not twilio_service:
        raise HTTPException(
            status_code=500,
            detail="Twilio service not available. Check server logs for import errors."
        )
    
    try:
        result = twilio_service.initiate_call(
            to_number=request.to_number,
            from_number=request.from_number,
            case_id=request.case_id,
            client_name=request.client_name
        )
        
        return JSONResponse(
            status_code=200 if result["status"] in ["success", "mock"] else 500,
            content=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initiating call: {str(e)}"
        )


@app.get("/api/calls/{call_sid}/status")
async def get_call_status(call_sid: str):
    """
    Get current status of a call
    
    Args:
        call_sid: Twilio Call SID
        
    Returns:
        Call status details
    """
    try:
        result = twilio_service.get_call_status(call_sid)
        
        return JSONResponse(
            status_code=200 if result["status"] in ["success", "mock"] else 404,
            content=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching call status: {str(e)}"
        )


@app.get("/api/calls/{call_sid}/recording")
async def get_call_recording(call_sid: str):
    """
    Get recording URL for a completed call
    
    Args:
        call_sid: Twilio Call SID
        
    Returns:
        Recording details including URL
    """
    try:
        result = twilio_service.get_call_recording(call_sid)
        
        return JSONResponse(
            status_code=200 if result["status"] == "success" else 404,
            content=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recording: {str(e)}"
        )


@app.post("/api/calls/status")
async def call_status_callback(request: Request):
    """
    Webhook endpoint for Twilio call status updates
    
    Twilio will POST to this endpoint with call status updates
    """
    form_data = await request.form()
    
    # Log the callback data
    print(f"📞 Call Status Update: {dict(form_data)}")
    
    # Generate TwiML response
    twiml = twilio_service.generate_call_twiml()
    
    return Response(content=twiml, media_type="application/xml")


@app.post("/api/calls/status/recording")
async def recording_status_callback(request: Request):
    """
    Webhook endpoint for Twilio recording status updates
    """
    form_data = await request.form()
    
    # Log the recording data
    print(f"🎙️ Recording Status Update: {dict(form_data)}")
    
    # Here you would typically:
    # 1. Save recording URL to database
    # 2. Trigger transcription service
    # 3. Run AI analysis on transcription
    
    return JSONResponse(content={"status": "received"})


@app.post("/api/sms/send")
async def send_sms(request: SMSRequest):
    """
    Send SMS message to client
    
    Request body:
    {
        "to_number": "+15551234567",
        "message": "Your appointment is confirmed for tomorrow at 2 PM.",
        "from_number": "+15559876543"  // optional
    }
    
    Returns:
        Message details
    """
    try:
        result = twilio_service.send_sms(
            to_number=request.to_number,
            message=request.message,
            from_number=request.from_number
        )
        
        return JSONResponse(
            status_code=200 if result["status"] in ["success", "mock"] else 500,
            content=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending SMS: {str(e)}"
        )


# ============================================
# Chat/Q&A Endpoint
# ============================================

from datetime import datetime, timedelta
from openai import AsyncOpenAI

# Initialize OpenAI client
try:
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("[OK] OpenAI client initialized successfully")
except Exception as e:
    print(f"[WARNING] OpenAI client initialization failed: {e}")
    openai_client = None

class ChatRequest(BaseModel):
    """Request model for chat questions"""
    question: str
    case_context: Optional[dict] = None


@app.post("/api/chat/ask")
async def ask_question(request: ChatRequest):
    """
    Answer attorney questions about the case using AI
    
    Request body:
    {
        "question": "What are the key issues in this case?",
        "case_context": {
            "client_name": "Emily Watson",
            "case_type": "Premises Liability",
            "attorney_brief": "...",
            "agent_outputs": {...}
        }
    }
    
    Returns:
        AI-generated response based on case context
    """
    try:
        print(f"[DEBUG] Chat question received: {request.question}")
        
        # Check if OpenAI client is available
        if not openai_client:
            print("[WARNING] OpenAI client not available, using fallback")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "answer": "I can help you with questions about this case. Based on the available information, I can provide insights about the client, case details, evidence, and recommended actions.",
                    "agent": "Legal Assistant"
                }
            )
        
        # Build context from case data
        context_parts = []
        
        if request.case_context:
            if request.case_context.get("attorney_brief"):
                context_parts.append(f"Attorney Brief:\n{request.case_context['attorney_brief']}")
            
            if request.case_context.get("client_name"):
                context_parts.append(f"Client: {request.case_context['client_name']}")
            
            if request.case_context.get("case_type"):
                context_parts.append(f"Case Type: {request.case_context['case_type']}")
            
            if request.case_context.get("agent_outputs"):
                context_parts.append(f"Agent Analysis: {str(request.case_context['agent_outputs'])[:500]}")
        
        context_text = "\n\n".join(context_parts) if context_parts else "No case context available."
        
        print(f"[DEBUG] Context built, calling OpenAI...")
        
        # Call OpenAI
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful legal assistant for Morgan & Morgan attorneys. Answer questions about cases based on the provided context. Be concise, professional, and actionable."
                },
                {
                    "role": "user",
                    "content": f"Case Context:\n{context_text}\n\nAttorney Question: {request.question}"
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        print(f"[DEBUG] OpenAI response received: {answer[:100]}...")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "answer": answer,
                "agent": "Legal Assistant"
            }
        )
        
    except Exception as e:
        print(f"[ERROR] Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "answer": "I can help you with questions about this case. Based on the available information, I can provide insights about the client, case details, evidence, and recommended actions.",
                "agent": "Legal Assistant"
            }
        )


# ============================================
# Google Calendar Endpoints
# ============================================


class MeetingRequest(BaseModel):
    """Request model for scheduling a meeting"""
    client_name: str
    client_email: Optional[str] = None
    case_id: Optional[str] = None
    duration_minutes: int = 30
    preferred_date: Optional[str] = None  # ISO format date
    preferred_time: Optional[str] = None  # HH:MM format


@app.post("/api/calendar/schedule")
async def schedule_meeting(request: MeetingRequest):
    """
    Schedule a meeting with a client
    
    Request body:
    {
        "client_name": "Sarah Martinez",
        "client_email": "sarah@example.com",
        "case_id": "2024-PI-9999",
        "duration_minutes": 30,
        "preferred_date": "2024-10-27",
        "preferred_time": "14:00"
    }
    
    Returns:
        Meeting details including calendar event
    """
    if not calendar_service:
        # Mock mode
        return JSONResponse(
            status_code=200,
            content={
                "status": "mock",
                "message": "Meeting scheduled (mock mode)",
                "event_id": f"mock_event_{datetime.now().timestamp()}",
                "client_name": request.client_name,
                "date": request.preferred_date or "TBD",
                "time": request.preferred_time or "TBD"
            }
        )
    
    try:
        # Parse date and time
        if request.preferred_date and request.preferred_time:
            start_dt = datetime.fromisoformat(f"{request.preferred_date}T{request.preferred_time}:00")
        else:
            # Default to tomorrow at 2 PM
            start_dt = datetime.now() + timedelta(days=1)
            start_dt = start_dt.replace(hour=14, minute=0, second=0, microsecond=0)
        
        end_dt = start_dt + timedelta(minutes=request.duration_minutes)
        
        # Create calendar event
        event = await calendar_service.create_event(
            summary=f"Client Meeting - {request.client_name}",
            description=f"Case: {request.case_id or 'N/A'}\nClient: {request.client_name}",
            start_time=start_dt,
            end_time=end_dt,
            attendees=[request.client_email] if request.client_email else None
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": event.get("status"),
                "event_id": event.get("id"),
                "client_name": request.client_name,
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "calendar_link": event.get("htmlLink"),
                "message": f"Meeting scheduled with {request.client_name}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scheduling meeting: {str(e)}"
        )


@app.get("/api/calendar/available-slots")
async def get_available_slots(
    duration: int = 30,
    days_ahead: int = 7
):
    """
    Get available time slots for scheduling
    
    Query params:
        duration: Meeting duration in minutes (default: 30)
        days_ahead: How many days to look ahead (default: 7)
    
    Returns:
        List of available time slots
    """
    if not calendar_service:
        # Mock available slots
        now = datetime.now()
        mock_slots = []
        for i in range(1, 6):
            slot_time = now + timedelta(days=i, hours=2)
            mock_slots.append({
                "start": slot_time.isoformat(),
                "end": (slot_time + timedelta(minutes=duration)).isoformat(),
                "formatted": slot_time.strftime("%A, %B %d at %I:%M %p")
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "mock",
                "slots": mock_slots
            }
        )
    
    try:
        slots = await calendar_service.find_available_slots(
            duration_minutes=duration,
            days_ahead=days_ahead
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "slots": slots
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding available slots: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
