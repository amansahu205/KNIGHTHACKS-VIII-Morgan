# ⚡ Quick Start Guide

## 🚀 Start Development (2 Commands)

### Terminal 1 - Backend
```bash
uvicorn backend.main:app --reload
```
✅ Running at: `http://localhost:8000`

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
✅ Running at: `http://localhost:3000`

---

## 📦 First Time Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node dependencies
cd frontend
npm install
cd ..

# 3. Configure environment
# Edit .env with your API keys
```

---

## 🧪 Test the System

```bash
# Test backend
python temp/test_end_to_end.py

# Test frontend
# Open http://localhost:3000
# Upload file from data/ folder
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI server |
| `frontend/app/page.tsx` | Main UI |
| `frontend/.env.local` | API URL config |
| `.env` | Backend API keys |
| `data/*.txt` | Sample case files |

---

## 🔌 API Endpoint

```bash
POST http://localhost:8000/process_file
Content-Type: multipart/form-data
Body: .txt file
```

---

## 🐛 Common Issues

**Frontend won't start?**
```bash
cd frontend && npm install
```

**Backend errors?**
```bash
pip install -r requirements.txt
# Check .env has API keys
```

**CORS errors?**
```bash
# Check backend is running
# Verify frontend/.env.local has correct URL
```

---

## 📖 Full Documentation

- **Setup**: `README.md`
- **Integration**: `SETUP_COMPLETE.md`
- **Project Status**: `PROJECT_STATUS.md`

---

**Need help?** Check `README.md` for detailed instructions.
