# KNIGHTHACKS-VIII-Morgan

AI Legal Tender Multi-Agent System for Morgan & Morgan Challenge

## 🎯 Project Overview

An intelligent legal case processing system that uses specialized AI agents to automate routine legal tasks with human-in-the-loop approval. The system analyzes case files, extracts metadata, routes tasks to appropriate agents, and generates professional attorney briefs.

## 🏗️ Architecture

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI with async orchestrator
- **Agents**: 5 specialized AI agents (GPT-4 Turbo / Claude 3.5)
- **Workflow**: Human-in-the-loop approval system

## 🤖 AI Agents

1. **Records Wrangler** - Identifies missing/incomplete/duplicate records
2. **Client Communication Guru** - Drafts empathetic client messages
3. **Legal Researcher** - Finds supporting verdicts/statutes
4. **Voice Bot Scheduler** - Coordinates calls/meetings
5. **Evidence Sorter** - Classifies and extracts structured evidence data

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **OpenAI API Key** or **Anthropic API Key**

### Installation

#### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd KNIGHTHACKS-VIII-Morgan

# Copy environment file
cp .env.example .env
```

#### 2. Configure API Keys

Edit `.env` and add your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

DEFAULT_LLM_PROVIDER=openai  # or anthropic
DEFAULT_MODEL=gpt-4-turbo-preview  # or claude-3-5-sonnet-20241022
```

#### 3. Install Backend Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

#### 4. Install Frontend Dependencies

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install
# or
pnpm install
# or
yarn install

# Return to root
cd ..
```

### Running the Application

#### Option 1: Using PowerShell Scripts (Recommended for Windows)

**Terminal 1 - Backend:**
```powershell
# From project root
.\start_backend.ps1
```

Backend will start at: `http://localhost:8000`

**Terminal 2 - Frontend:**
```powershell
# From project root
.\start_frontend.ps1
```

Frontend will start at: `http://localhost:3000`

#### Option 2: Manual Commands

**Terminal 1 - Backend:**
```bash
# From project root
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
# From project root
cd frontend
npm run dev
```

#### Option 2: Run Backend Only (API Testing)

```bash
# From project root
uvicorn backend.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Testing the System

#### 1. Test Backend API

```bash
# Test with sample file
python temp/test_end_to_end.py
```

#### 2. Test Frontend Integration

1. Open `http://localhost:3000` in your browser
2. Upload a `.txt` case file (samples in `data/` folder)
3. Review AI agent outputs in chat interface
4. Approve/Modify/Reject agent recommendations

## 📁 Project Structure

```
KNIGHTHACKS-VIII-Morgan/
├── frontend/                    # Next.js frontend application
│   ├── app/                     # Next.js 14 app directory
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Main page with chat interface
│   ├── components/              # React components
│   │   ├── file-upload.tsx     # File upload component
│   │   ├── chat-interface.tsx  # Chat UI
│   │   ├── case-summary-panel.tsx
│   │   └── ui/                 # shadcn/ui components
│   ├── lib/                    # Utilities and types
│   │   └── types.ts            # TypeScript interfaces
│   ├── .env.local              # Frontend environment variables
│   ├── package.json            # Node dependencies
│   └── tsconfig.json           # TypeScript configuration
│
├── backend/                     # FastAPI backend application
│   ├── main.py                 # FastAPI app entry point
│   ├── orchestrator/           # Task detection and routing
│   │   ├── orchestrator_core.py  # Main orchestration logic
│   │   └── router.py           # API router
│   ├── agents/                 # Specialized AI agents
│   │   ├── records_wrangler.py
│   │   ├── communication_guru.py
│   │   ├── legal_researcher.py
│   │   ├── voice_bot_scheduler.py
│   │   └── evidence_sorter.py
│   ├── utils/                  # Utility modules
│   │   └── context_enricher.py  # Metadata extraction
│   └── postprocessors/         # Output formatting
│       └── brief_generator.py   # Attorney brief generation
│
├── data/                       # Sample case files
│   ├── sample_case_evidence.txt
│   ├── sample_case_incomplete_records.txt
│   └── ...
│
├── temp/                       # Test scripts (safe to delete)
│   ├── test_end_to_end.py
│   ├── test_orchestrator.py
│   └── ...
│
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔌 API Endpoints

### Backend API (`http://localhost:8000`)

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "running",
  "message": "KNIGHTHACKS-VIII-Morgan API is operational",
  "version": "1.0.0"
}
```

#### `POST /process_file`
Process uploaded case file through AI orchestrator.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `.txt` file

**Response:**
```json
{
  "summary": "Case #2024-PI-8888 | Type: Premises Liability...",
  "detected_tasks": [...],
  "agent_outputs": {...},
  "recommended_actions": [...],
  "context_metadata": {...},
  "attorney_brief": "This office represents...",
  "overall_confidence": 0.88,
  "execution_time_seconds": 5.23
}
```

## 🔧 Configuration

### Backend Configuration (`.env`)

```bash
# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
MAX_TOKENS=4096
TEMPERATURE=0.7

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Frontend Configuration (`frontend/.env.local`)

```bash
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production deployment, update to your deployed backend URL:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## 🧪 Testing

### Backend Tests

```bash
# Test individual agents
python temp/test_records_wrangler.py
python temp/test_communication_guru.py
python temp/test_legal_researcher.py
python temp/test_voice_bot_scheduler.py
python temp/test_evidence_sorter.py

# Test orchestrator
python temp/test_orchestrator.py

# Test context enricher
python temp/test_context_enricher.py

# Test brief generator
python temp/test_brief_generator.py

# Test end-to-end workflow
python temp/test_end_to_end.py
```

### Frontend Testing

```bash
cd frontend
npm run build  # Test production build
npm run lint   # Run ESLint
```

## 🚢 Deployment

### Backend Deployment (Railway/Render/Fly.io)

1. Set environment variables in deployment platform
2. Deploy with: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Connect GitHub repository to Vercel
2. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```
3. Deploy automatically on push

## 📊 Features

### ✅ Completed Features

- 5 specialized AI agents with multi-LLM support
- Async orchestrator with task detection
- Context enricher (metadata extraction)
- Attorney brief generator
- Human-in-the-loop approval workflow
- Next.js frontend with chat interface
- File upload and processing
- Real-time agent output display
- CORS-enabled API

### ⏳ Future Enhancements

- Voice bot integration for client calls
- PDF export of attorney briefs
- Case management dashboard
- Multi-user authentication
- Document version control
- Analytics and reporting

## 🔐 Security

- Never commit `.env` files
- Use environment variables for all secrets
- CORS configured for production domains
- Input validation on all endpoints
- Rate limiting (recommended for production)

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'openai'`
```bash
pip install -r requirements.txt
```

**Issue**: `OpenAIError: The api_key client option must be set`
```bash
# Check .env file has OPENAI_API_KEY set
# Load environment: python-dotenv will load it automatically
```

### Frontend Issues

**Issue**: `Cannot find module 'react'`
```bash
cd frontend
npm install
```

**Issue**: API calls failing with CORS error
```bash
# Ensure backend CORS middleware is configured
# Check NEXT_PUBLIC_API_URL in frontend/.env.local
```

## 📝 Development Rules

- Never modify `backend/` or `frontend/` without explicit instruction
- All temporary/test scripts go to `temp/` (safe to delete)
- Use structured JSON responses for all agents
- Never hardcode API keys
- Follow TypeScript strict mode in frontend
- Use async/await for all agent operations

## 👥 Team

Built for Knight Hacks VIII - Morgan & Morgan "AI Legal Tender" Challenge

## 📄 License

MIT License
