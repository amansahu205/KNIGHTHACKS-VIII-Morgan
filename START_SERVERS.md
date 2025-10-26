# 🚀 Start Servers

## ✅ Dependencies Installed Successfully!

Frontend dependencies installed with `--legacy-peer-deps` to resolve React 19 compatibility.

---

## Start Both Servers

### Terminal 1 - Backend
```bash
# From project root
uvicorn backend.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ Backend running at: `http://localhost:8000`  
✅ API docs at: `http://localhost:8000/docs`

---

### Terminal 2 - Frontend
```bash
# From project root
cd frontend
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Ready in 2.5s
```

✅ Frontend running at: `http://localhost:3000`

---

## Test the Integration

1. **Open browser**: `http://localhost:3000`

2. **Upload a test file**:
   - Click "Select File" or drag & drop
   - Choose a file from `data/` folder (e.g., `sample_case_evidence.txt`)

3. **Watch the magic happen**:
   - ✅ File uploads to backend
   - ✅ AI agents process the case
   - ✅ Attorney brief appears in chat
   - ✅ Agent outputs display with approve/modify/reject buttons
   - ✅ Recommended actions shown

---

## Quick Health Check

### Backend Health Check
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "status": "running",
  "message": "KNIGHTHACKS-VIII-Morgan API is operational",
  "version": "1.0.0"
}
```

### Frontend Health Check
- Open `http://localhost:3000` in browser
- Should see Morgan & Morgan branded interface
- File upload area should be visible

---

## Troubleshooting

### Backend won't start?

**Check Python environment:**
```bash
python --version  # Should be 3.11+
pip list | grep fastapi  # Should show fastapi 0.109.0
```

**Check .env file:**
```bash
# Ensure .env has API keys
cat .env  # or type .env on Windows
```

### Frontend won't start?

**Check Node version:**
```bash
node --version  # Should be 18+
npm --version
```

**Reinstall if needed:**
```bash
cd frontend
rm -rf node_modules package-lock.json  # or del on Windows
npm install --legacy-peer-deps
```

### CORS errors in browser console?

1. Ensure backend is running
2. Check `frontend/.env.local` has:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Verify CORS in `backend/main.py` (already configured ✅)

---

## Development Workflow

### Making Changes

**Backend changes:**
- Edit files in `backend/`
- Server auto-reloads (with `--reload` flag)
- Check terminal for errors

**Frontend changes:**
- Edit files in `frontend/`
- Browser auto-refreshes
- Check browser console for errors

### Testing

**Test backend only:**
```bash
python temp/test_end_to_end.py
```

**Test full integration:**
1. Start both servers
2. Upload file via UI
3. Verify all components work

---

## Stop Servers

**Stop backend:** Press `Ctrl+C` in Terminal 1  
**Stop frontend:** Press `Ctrl+C` in Terminal 2

---

## Next Steps

Once both servers are running:

1. ✅ Test file upload with sample data
2. ✅ Verify attorney brief generation
3. ✅ Test approve/modify/reject workflow
4. ✅ Check all agent outputs display correctly
5. ✅ Review logs in `temp/orchestrator_logs.log`

---

**Status**: ✅ Ready to Start Development!  
**Date**: October 26, 2024

**Run the commands above to start coding!** 🚀
