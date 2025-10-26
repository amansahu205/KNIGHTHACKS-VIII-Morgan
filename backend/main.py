"""
FastAPI Backend for KNIGHTHACKS-VIII-Morgan
AI Legal Tender Multi-Agent System
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import orchestrator router function
from orchestrator.router import process_case_file


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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
