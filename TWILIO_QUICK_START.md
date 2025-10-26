# 📞 Twilio Integration - Quick Start (5 Minutes)

## 🚀 Option 1: Demo Mode (No Twilio Account Needed)

**Already working!** Just use the system as-is:

1. Start servers:
   ```bash
   .\start_backend.ps1
   .\start_frontend.ps1
   ```

2. Upload: `data/sample_case_frustrated_client.txt`

3. Click **"Call Client Now"** button

4. See: "✅ Call initiated! (Mock mode)"

**Perfect for hackathon demo!** ✅

---

## 📞 Option 2: Real Calls (With Twilio - 15 Minutes)

### Step 1: Get Twilio Account (10 min)

1. Go to: https://www.twilio.com/try-twilio
2. Sign up (free trial)
3. Verify email + phone
4. Get a trial phone number
5. Copy these 3 things:
   - Account SID
   - Auth Token  
   - Your Twilio phone number

### Step 2: Add to `.env` (2 min)

Open `.env` file and add:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+15551234567
ATTORNEY_PHONE_NUMBER=+15559876543  # Your phone number
```

### Step 3: Verify Your Phone (2 min)

**Important for trial accounts!**

1. Go to Twilio Console → **Verified Caller IDs**
2. Click **"Add a new number"**
3. Enter your phone number
4. Verify with code

### Step 4: Install & Test (1 min)

```bash
# Install Twilio
pip install twilio

# Restart backend
.\start_backend.ps1
```

Upload test case → Click "Call Client Now" → **Your phone rings!** 📞

---

## 🎯 Quick Test

### Test API Directly:

```bash
curl -X POST http://localhost:8000/api/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+15551234567", "case_id": "TEST"}'
```

### Expected Response:

**Mock Mode**:
```json
{
  "status": "mock",
  "call_sid": "CA_mock_1234567890",
  "message": "Mock call initiated"
}
```

**Real Twilio**:
```json
{
  "status": "success",
  "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "to": "+15551234567",
  "from": "+15559876543"
}
```

---

## 🐛 Troubleshooting

### "Twilio credentials not configured"
→ Add credentials to `.env` and restart backend

### "The 'To' number is not a valid phone number"
→ Use format: `+15551234567` (with +1 country code)

### "Permission Denied"
→ For trial accounts, verify the destination number first

---

## 📚 Full Documentation

See `TWILIO_INTEGRATION_COMPLETE.md` for:
- Detailed setup guide
- API reference
- Advanced features
- Production deployment
- Troubleshooting

---

## ✅ Summary

**Mock Mode** (Current):
- ✅ Works out of the box
- ✅ Perfect for demo
- ✅ No setup needed

**Real Calls** (Optional):
- 📞 15 minutes to set up
- 📞 Free trial account
- 📞 Real phone calls
- 📞 Call recording
- 📞 SMS messaging

**Choose based on your needs!** 🎯
