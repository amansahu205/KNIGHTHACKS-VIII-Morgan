# 🚀 Deployment Guide

## Quick Deployment for Hackathon Demo

### Option 1: Vercel (Frontend) + Local Backend (Recommended)

#### Step 1: Deploy Frontend to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy Frontend:**
   ```bash
   cd frontend
   vercel
   ```
   
3. **Follow prompts:**
   - Link to existing project? **No**
   - Project name: **knighthacks-morgan**
   - Which directory? **./frontend**
   - Override settings? **No**

4. **Set Environment Variable in Vercel:**
   - Go to your Vercel dashboard
   - Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `http://localhost:8000` (will update with ngrok)

#### Step 2: Expose Local Backend with ngrok

1. **Install ngrok:**
   - Download from: https://ngrok.com/download
   - Or: `choco install ngrok` (Windows)

2. **Start your backend:**
   ```bash
   .\start_backend.ps1
   ```

3. **In another terminal, run ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`)

5. **Update Vercel Environment Variable:**
   - Go to Vercel dashboard
   - Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to your ngrok URL
   - Redeploy: `vercel --prod`

#### Step 3: Test

Visit your Vercel URL and test all features!

---

## Option 2: Full Local Demo (Simplest)

1. **Start Backend:**
   ```bash
   .\start_backend.ps1
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open:** http://localhost:3000

4. **Share screen during presentation!**

---

## Option 3: Deploy Both to Cloud

### Frontend: Vercel
- Same as Option 1, Step 1

### Backend: Render.com

1. **Go to:** https://render.com
2. **New Web Service** → Connect GitHub
3. **Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3
   
4. **Add Environment Variables:**
   - Copy all from `.env` file
   - Add each one in Render dashboard

5. **Deploy!**

6. **Update Vercel:**
   - Set `NEXT_PUBLIC_API_URL` to your Render URL
   - Redeploy

---

## Environment Variables Needed

### Backend (.env):
```
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number
ATTORNEY_PHONE_NUMBER=your_number
```

### Frontend (Vercel):
```
NEXT_PUBLIC_API_URL=your_backend_url
```

---

## 🎯 Recommended for Hackathon:

**Option 1** - Vercel + ngrok
- Professional frontend URL
- Backend runs locally (no deployment issues)
- Easy to demo
- Can show backend logs live

---

## Troubleshooting

### CORS Errors:
- Backend already has CORS enabled for all origins
- Check that `NEXT_PUBLIC_API_URL` is set correctly

### 404 Errors:
- Ensure backend is running
- Check ngrok URL is correct
- Verify environment variable in Vercel

### API Key Errors:
- Ensure all environment variables are set
- Restart backend after changing .env

---

## 📞 Support

For issues during deployment, check:
1. Backend logs
2. Browser console (F12)
3. Vercel deployment logs
4. ngrok dashboard
