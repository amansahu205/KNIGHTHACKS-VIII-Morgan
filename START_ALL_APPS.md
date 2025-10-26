# 🚀 Start All Applications

## Quick Start Guide

### 1️⃣ Start Backend (Required for all apps)
```powershell
.\start_backend.ps1
```
- Backend runs at: **http://localhost:8000**
- Keep this terminal open

### 2️⃣ Start Dashboard (Main Landing Page)
```powershell
.\start_dashboard.ps1
```
- Dashboard runs at: **http://localhost:3001**
- Shows cards for all 3 apps

### 3️⃣ Start Morgan & Morgan (Optional - for local development)
```powershell
cd frontend
npm run dev
```
- Morgan app runs at: **http://localhost:3000**
- Or use deployed version: **https://v0-knight-hacks.vercel.app**

---

## 🌐 Access URLs

| App | Local URL | Deployed URL |
|-----|-----------|--------------|
| **Dashboard** | http://localhost:3001 | Deploy with `vercel` |
| **Morgan & Morgan** | http://localhost:3000 | https://v0-knight-hacks.vercel.app |
| **Backend API** | http://localhost:8000 | ngrok tunnel |

---

## 📁 Project Structure

```
KNIGHTHACKS-VIII-Morgan/
│
├── dashboard/              # Main dashboard (Port 3001)
│   └── app/
│       ├── page.tsx        # Landing page with 3 app cards
│       └── morgan/
│           └── page.tsx    # Redirects to Morgan app
│
├── frontend/               # Morgan & Morgan app (Port 3000)
│   └── app/
│       └── page.tsx        # Full AI Legal Assistant
│
└── backend/                # Shared backend (Port 8000)
    └── main.py             # FastAPI server
```

---

## 🎯 User Flow

1. **User visits Dashboard** → http://localhost:3001
2. **Sees 3 app cards:**
   - OneEthos (AI Financial Empowerment)
   - **Morgan & Morgan** (AI Legal Tender) ← Your hackathon project
   - ServiceNow (Knowledge Gap Agent)
3. **Clicks Morgan & Morgan card**
4. **Redirected to** → https://v0-knight-hacks.vercel.app
5. **Uses full AI Legal Assistant features**

---

## 🔧 For Hackathon Demo

### Option A: Use Deployed Version (Recommended)
1. Start backend: `.\start_backend.ps1`
2. Start ngrok: `ngrok http 8000`
3. Share dashboard: http://localhost:3001
4. Morgan app is already deployed: https://v0-knight-hacks.vercel.app

### Option B: Run Everything Locally
1. Start backend: `.\start_backend.ps1`
2. Start dashboard: `.\start_dashboard.ps1`
3. Start Morgan app: `cd frontend && npm run dev`
4. Access:
   - Dashboard: http://localhost:3001
   - Morgan: http://localhost:3000

---

## 📦 First Time Setup

### Dashboard:
```bash
cd dashboard
npm install
npm run dev
```

### Morgan & Morgan:
```bash
cd frontend
npm install
npm run dev
```

### Backend:
```bash
pip install -r requirements.txt
.\start_backend.ps1
```

---

## 🎨 App Themes

- **Dashboard**: Dark theme with blue/cyan accents
- **Morgan & Morgan**: Burgundy (#8B1F1F) & Gold (#D4AF37)
- **OneEthos**: Blue/Cyan theme
- **ServiceNow**: ServiceNow brand colors

---

## ✅ Checklist Before Demo

- [ ] Backend running (Port 8000)
- [ ] ngrok tunnel active (if using deployed frontend)
- [ ] Dashboard running (Port 3001) - Optional
- [ ] Morgan app deployed and accessible
- [ ] Environment variables set in Vercel
- [ ] Test file upload works
- [ ] Test AI chat works
- [ ] Test Twilio calling works

---

## 🚨 Troubleshooting

### Dashboard won't start:
```bash
cd dashboard
rm -rf node_modules
npm install
npm run dev
```

### Morgan app shows "Failed to fetch":
- Check backend is running
- Check ngrok is active
- Verify `NEXT_PUBLIC_API_URL` in Vercel

### Port already in use:
```bash
# Kill process on port 3000
npx kill-port 3000

# Kill process on port 3001
npx kill-port 3001

# Kill process on port 8000
npx kill-port 8000
```

---

## 🎉 You're Ready!

Your multi-app portfolio is now organized and ready for the hackathon demo!
