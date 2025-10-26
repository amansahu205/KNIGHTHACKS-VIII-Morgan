# 📁 Frontend Structure

## Overview

This project now has an organized multi-app structure with a central dashboard.

```
KNIGHTHACKS-VIII-Morgan/
├── dashboard/              # Main dashboard (landing page)
│   ├── app/
│   │   ├── page.tsx       # Dashboard home with 3 app cards
│   │   ├── morgan/        # Morgan & Morgan route
│   │   │   └── page.tsx   # Redirects to deployed Morgan app
│   │   ├── oneethos/      # OneEthos route (if needed)
│   │   └── servicenow/    # ServiceNow route (if needed)
│   └── ...
│
├── frontend/              # Morgan & Morgan AI Legal Assistant
│   ├── app/
│   │   ├── page.tsx       # Main Morgan & Morgan app
│   │   └── layout.tsx
│   ├── components/
│   │   ├── chat-interface.tsx
│   │   ├── action-toolbar.tsx
│   │   └── ...
│   └── ...
│
└── backend/               # Shared backend for all apps
    └── ...
```

## 🚀 How It Works

### Dashboard (Port 3001)
- **URL**: http://localhost:3001
- **Purpose**: Landing page with cards for all 3 apps
- **Features**:
  - OneEthos card
  - Morgan & Morgan card → Redirects to deployed app
  - ServiceNow card

### Morgan & Morgan App (Deployed)
- **URL**: https://v0-knight-hacks.vercel.app
- **Purpose**: Full AI Legal Assistant application
- **Features**:
  - Case file upload
  - Multi-agent AI analysis
  - Interactive chat
  - Twilio calling
  - Meeting scheduling

## 🎯 Running the Apps

### Start Dashboard:
```bash
cd dashboard
npm install
npm run dev
```
Access at: http://localhost:3001

### Start Morgan & Morgan (Local Development):
```bash
cd frontend
npm install
npm run dev
```
Access at: http://localhost:3000

### Start Backend:
```bash
.\start_backend.ps1
```
Backend runs at: http://localhost:8000

## 🔗 Navigation Flow

1. **User visits Dashboard** → http://localhost:3001
2. **Clicks "Morgan & Morgan" card**
3. **Redirected to** → https://v0-knight-hacks.vercel.app
4. **Uses the full Morgan & Morgan AI Legal Assistant**

## 📦 Deployment

### Dashboard Deployment (Optional):
```bash
cd dashboard
vercel
```

### Morgan & Morgan (Already Deployed):
- **Production**: https://v0-knight-hacks.vercel.app
- **Backend**: ngrok tunnel to localhost:8000

## 🎨 Branding

Each app has its own theme:
- **OneEthos**: Blue/Cyan theme
- **Morgan & Morgan**: Burgundy (#8B1F1F) & Gold (#D4AF37)
- **ServiceNow**: ServiceNow brand colors

## 🔧 Configuration

### Dashboard Environment Variables:
None required (static routing)

### Morgan & Morgan Environment Variables:
- `NEXT_PUBLIC_API_URL`: Backend URL (ngrok or deployed backend)

### Backend Environment Variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

## 📝 Notes

- Dashboard serves as a portfolio/launcher
- Each app can be developed independently
- Shared backend serves all apps
- Morgan & Morgan is the primary hackathon project
