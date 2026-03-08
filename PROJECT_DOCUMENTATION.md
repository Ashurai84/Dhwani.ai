# 🏦 AI Banking Assistant - IDEIA 2.0

## Yeh Project Kya Hai?

Yeh ek **Voice-Based AI Banking Assistant** hai jo Indian languages (Hindi, English, Tamil, etc.) mein customers se baat kar sakta hai. Matlab customer bank ko call kare ya branch mein aaye, toh AI unse baat karega - unki language mein!

**Simple Example:**
- Customer bola: "Mujhe home loan chahiye"
- AI samjha: Intent = home_loan_enquiry
- AI bola: "Ji bilkul, aapko kya fixed rate chahiye ya floating?"
- Sab kuch VOICE mein - type karne ki zaroorat nahi!

---

## 🏗️ Architecture - System Kaise Kaam Karta Hai

```
┌──────────────────────────────────────────────────────────────────┐
│                    CUSTOMER KA PHONE / BROWSER                    │
│                     (Voice Input Diya Customer Ne)                │
└──────────────────────────────────────────────────────────────────┘
                                │
                                │ Audio (Base64 format mein)
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER (main.py)                     │
│                   Yeh sab requests handle karta hai               │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    AI PIPELINE (ai_service.py)                    │
│                                                                   │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│   │ SARVAM  │    │   PII   │    │  GROQ   │    │ SARVAM  │       │
│   │  STT    │ ─▶ │ REDACT  │ ─▶ │   AI    │ ─▶ │   TTS   │       │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘       │
│                                                                   │
│   Voice→Text    Aadhaar/Phone   Samjho &      Text→Voice         │
│                 Hide Karo       Jawab Do                          │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     MONGODB ATLAS (Cloud DB)                      │
│                  Sessions, Conversations, Reports                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📂 Files Ka Breakdown

```
Ideia 2.0/
├── .venv/                 # Python virtual environment (packages yahan hai)
├── backend/
│   ├── .env               # API keys yahan hai (IMPORTANT - share mat karna!)
│   ├── main.py            # FastAPI server - sab endpoints yahan hai
│   ├── ai_service.py      # AI logic - STT, AI brain, TTS sab yahan
│   ├── database.py        # MongoDB connection setup
│   ├── schemas.py         # Request/Response ka structure define
│   └── voice_test.html    # Browser mein test karne ka page
└── PROJECT_DOCUMENTATION.md  # Yeh file!
```

---

## 🔧 Har File Kya Karti Hai

### 1. `main.py` - Server Ka Main File

Yeh FastAPI application hai jisme saare API endpoints defined hain:

| Endpoint | Method | Kya Karta Hai |
|----------|--------|---------------|
| `/` | GET | Voice test page serve karta hai |
| `/interaction/start` | POST | Naya session start karta hai (session_id milta hai) |
| `/interaction/audio` | POST | Audio le ke AI response deta hai |
| `/interaction/text` | POST | Text input leke AI response deta hai (fallback) |
| `/interaction/end` | POST | Session end karke report generate karta hai |
| `/reports` | GET | Saari reports list karta hai |
| `/sessions` | GET | Saare sessions dikhata hai |
| `/conversations/{session_id}` | GET | Ek session ki saari baatcheet dikhata hai |
| `/report/{report_id}` | GET | Ek specific report + conversations |
| `/ws/dashboard` | WebSocket | Real-time updates ke liye |

**Kaise kaam karta hai:**
```
1. Customer ne bola → Audio base64 mein convert hua
2. /interaction/audio endpoint pe gaya
3. ai_service.py ko call hua
4. Response aaya with TTS audio
5. MongoDB mein save hua
6. Customer ko audio response mila
```

### 2. `ai_service.py` - AI Ka Dimag

Yeh file mein ACTUAL AI logic hai:

**Functions:**

| Function | Kya Karta Hai |
|----------|---------------|
| `transcribe_with_sarvam()` | Voice → Text (Sarvam API use karke) |
| `redact_pii()` | Aadhaar, Phone numbers hide kar deta hai |
| `call_groq_api()` | Groq AI ko call karke response leta hai |
| `call_sarvam_engine()` | Hindi queries ke liye AI response |
| `call_groq_engine()` | Complex queries ke liye AI response |
| `generate_sarvam_tts()` | Text → Voice (Shubh voice mein) |
| `process_audio_pipeline()` | Full flow: STT → PII → AI → TTS |
| `process_text_pipeline()` | Text input ke liye (STT skip) |
| `generate_final_summary()` | Call end hone pe summary generate |
| `execute_with_timeout()` | Agar slow ho toh 3.5 sec mein timeout |

**Full Pipeline:**
```
Audio Aaya
    │
    ▼
transcribe_with_sarvam() ─── "Mera naam Ashutosh hai" 
    │
    ▼
redact_pii() ─── "Mera naam Ashutosh hai" (safe text)
    │
    ▼
call_sarvam_engine() ─── {response: "Namaste Ashutosh!", intent: "greeting"}
    │
    ▼
generate_sarvam_tts() ─── Base64 Audio of "Namaste Ashutosh!"
    │
    ▼
Return sab kuch
```

### 3. `database.py` - MongoDB Connection

Simple file jo MongoDB Atlas se connect karti hai:

```python
# Connect hota hai startup pe
await connect_db()

# Use karte hain endpoints mein
db = get_db()
await db.sessions.insert_one({...})
await db.conversations.find({...})

# Disconnect hota hai shutdown pe  
await close_db()
```

**MongoDB Collections (Tables jaisi):**
- `sessions` - Session info (session_id, channel, status)
- `conversations` - Messages (speaker, message, timestamp)
- `reports` - Final reports (summary, intent, recommended_action)

### 4. `schemas.py` - Data Structure

Yeh define karta hai ki request/response mein kya aana chahiye:

```python
# Start request mein channel chahiye
class InteractionStartRequest:
    channel: str  # "voice_chat" ya "callcenter"

# Audio request mein yeh sab chahiye
class InteractionAudioRequest:
    session_id: str
    audio_file: str  # Base64 encoded
    language: str    # "hi-IN", "en-IN", etc.

# Response mein yeh milega
class InteractionAudioResponse:
    transcription: str  # Jo bola woh text mein
    intent: str         # Customer ka intent
    ai_response: str    # AI ka jawab
    base_64_audio_response: str  # Audio mein jawab
```

### 5. `voice_test.html` - Testing Page

Browser mein `http://localhost:8000` pe jaake test kar sakte ho:

**Features:**
- 🎤 Green button press karo → Bolo
- 🔇 Silence detect → Automatically send
- 🔊 AI ka jawab sunao
- 🔄 Fir se automatically listen
- ⌨️ Type bhi kar sakte ho (fallback)
- 🌐 Language change kar sakte ho

### 6. `.env` - Secret Keys

```
GROQ_API_KEY="gsk_xxx..."      # Groq AI ka key (groq.com se lo)
SARVAM_API_KEY="sk_xxx..."     # Sarvam AI ka key (sarvam.ai se lo)
MONGODB_URI="mongodb+srv://..." # MongoDB Atlas ka URI
```

**IMPORTANT:** Yeh file KABHI share mat karna! `.gitignore` mein daalna.

---

## 🔒 Security Features - PII Protection

Banking mein security bahut important hai. Yeh system kaise protect karta hai:

### 1. PII Redaction
Customer bola: "Mera Aadhaar 123456789012 hai"
AI ko gaya: "Mera Aadhaar [REDACTED_NUMBER] hai"

```python
def redact_pii(text):
    # 10-12 digit numbers hide (Aadhaar, Phone)
    text = re.sub(r'\b\d{10,12}\b', '[REDACTED_NUMBER]', text)
    # Email hide
    text = re.sub(r'\S+@\S+', '[REDACTED_EMAIL]', text)
    return text
```

### 2. Timeout Protection
Agar AI slow ho toh 3.5 sec ke baad human agent ko transfer:
```python
async def execute_with_timeout(coro, timeout=3.5):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return {"ai_response": "System busy. Human agent se connect kar rahe hain."}
```

### 3. Human Review Flag
Agar AI ka confidence low ho (<85%), toh human review ke liye mark:
```python
if confidence < 0.85:
    requires_human_review = True
```

---

## 🛠️ Setup Instructions

### Step 1: MongoDB Atlas Setup

1. https://www.mongodb.com/atlas pe jao
2. Free account banao
3. New Cluster create karo (FREE tier)
4. Database Access mein user banao
5. Network Access mein 0.0.0.0/0 allow karo (ya apna IP)
6. Connect → Drivers → Connection string copy karo
7. `.env` mein paste karo:
```
MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```

### Step 2: API Keys Lo

**Groq AI (FREE):**
1. https://console.groq.com jao
2. Sign up karo
3. API Keys section mein new key banao
4. Copy karke `.env` mein daalo

**Sarvam AI:**
1. https://www.sarvam.ai jao
2. Account banao
3. API key lo
4. Copy karke `.env` mein daalo

### Step 3: Server Start Karo

```bash
# Folder mein jao
cd "/Users/ashutoshrai/Desktop/Ideia 2.0/backend"

# Virtual environment activate karo
source ../.venv/bin/activate

# Server start karo
uvicorn main:app --reload --port 8000
```

### Step 4: Test Karo

Browser mein jao: http://localhost:8000

Green button dabao aur bolo:
- "Mujhe home loan chahiye"
- "Balance check karna hai"
- "Account open karna hai"

---

## 📡 API Usage Examples

### Start Session
```bash
curl -X POST http://localhost:8000/interaction/start \
  -H "Content-Type: application/json" \
  -d '{"channel": "voice_chat"}'

# Response: {"session_id": "session_abc123"}
```

### Send Audio
```bash
curl -X POST http://localhost:8000/interaction/audio \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_abc123",
    "audio_file": "BASE64_AUDIO_HERE",
    "language": "hi-IN"
  }'
```

### End Session & Get Report
```bash
curl -X POST http://localhost:8000/interaction/end \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_abc123"}'

# Response: {"report_id": "REP_xyz789"}
```

### Get All Reports
```bash
curl http://localhost:8000/reports
```

### Get Specific Report
```bash
curl http://localhost:8000/report/REP_xyz789
```

---

## 🎤 AI Services Detail

### Sarvam AI - STT (Speech to Text)
- **Model:** saarika:v2.5
- **Languages:** Hindi, English, Tamil, Telugu, Bengali, Marathi, etc.
- **Kaise kaam karta hai:** Audio file bhejo → Text milta hai
- **Timeout:** 8 seconds

### Groq AI - Brain
- **Model:** llama-3.3-70b-versatile
- **Kya karta hai:** Text samajhta hai, intent detect karta hai, response generate karta hai
- **Speed:** Bahut fast (~500ms)
- **Free tier:** Bahut generous!

### Sarvam AI - TTS (Text to Speech)
- **Model:** bulbul:v3
- **Voice:** Shubh (Male, Friendly)
- **Speed:** 1.25x (normal se thoda fast)
- **Quality:** 22050 Hz

---

## 🗄️ Database Structure (MongoDB)

### Sessions Collection
```json
{
  "session_id": "session_abc123",
  "channel": "voice_chat",
  "status": "active",
  "start_time": "2024-03-08T10:30:00Z",
  "end_time": null
}
```

### Conversations Collection
```json
{
  "session_id": "session_abc123",
  "speaker": "user",
  "message": "Mujhe loan chahiye",
  "timestamp": "2024-03-08T10:30:05Z"
}
```

### Reports Collection
```json
{
  "report_id": "REP_xyz789",
  "session_id": "session_abc123",
  "channel": "voice_chat",
  "intent": "loan_enquiry",
  "summary": "Customer ne home loan ke baare mein pucha.",
  "recommended_action": "Loan officer se connect karo",
  "confidence_score": 0.9,
  "requires_human_review": false,
  "timestamp": "2024-03-08T10:35:00Z"
}
```

---

## 🔄 Request-Response Flow

```
Customer Bola: "Mujhe home loan chahiye"
         │
         ▼
   ┌─────────────────────────────────────────┐
   │          1. SARVAM STT                   │
   │     Audio → "Mujhe home loan chahiye"    │
   └─────────────────────────────────────────┘
         │
         ▼
   ┌─────────────────────────────────────────┐
   │          2. PII REDACTION               │
   │     Text same (no PII found)            │
   └─────────────────────────────────────────┘
         │
         ▼
   ┌─────────────────────────────────────────┐
   │          3. GROQ AI                     │
   │     Intent: "home_loan_enquiry"         │
   │     Response: "Ji bilkul, aapko         │
   │     fixed rate chahiye ya floating?"    │
   └─────────────────────────────────────────┘
         │
         ▼
   ┌─────────────────────────────────────────┐
   │          4. SARVAM TTS                  │
   │     Text → Audio (Shubh voice)          │
   └─────────────────────────────────────────┘
         │
         ▼
   ┌─────────────────────────────────────────┐
   │          5. MONGODB SAVE                │
   │     Conversation stored                 │
   └─────────────────────────────────────────┘
         │
         ▼
Customer Ko Audio Response Mila! 🔊
```

---

## ⚡ Performance Optimizations

| Optimization | Value | Kyun |
|--------------|-------|------|
| STT Timeout | 8 sec | Zyada wait nahi karna |
| AI Timeout | 3.5 sec | Fast response chahiye |
| TTS Timeout | 10 sec | Audio generate hone do |
| Max Tokens | 400 | Short responses = fast |
| TTS Pace | 1.25x | Jaldi bole AI |
| Silence Detection | 0.8 sec | Jaldi bhejo audio |

---

## 🚀 Production Mein Deploy Kaise Kare

### Option 1: Railway.app (Easy)
1. GitHub pe push karo
2. railway.app pe jao
3. New project → Deploy from GitHub
4. Environment variables mein API keys daalo
5. Done!

### Option 2: Render.com
1. render.com pe jao
2. New Web Service
3. GitHub repo connect karo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Requirements.txt Banao
```
fastapi
uvicorn
motor
pymongo
httpx
python-dotenv
pydantic
```

---

## 🐛 Common Issues & Solutions

### "MONGODB_URI not set"
**Solution:** `.env` file mein MongoDB URI daalo

### "GROQ_API_KEY not set"
**Solution:** Groq console se API key lo aur `.env` mein daalo

### "STT failed"
**Reasons:**
- Audio 30 sec se zyada hai
- Wrong audio format
- Sarvam API down

### "TTS failed"
**Reasons:**
- Text bahut lamba hai
- Wrong language code
- Sarvam API down

### Server start nahi ho raha
```bash
# Virtual env activate karo pehle
source ../.venv/bin/activate

# Fir start karo
uvicorn main:app --reload
```

---

## 📞 Contact & Support

- **Groq AI Docs:** https://console.groq.com/docs
- **Sarvam AI Docs:** https://docs.sarvam.ai
- **MongoDB Docs:** https://www.mongodb.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com

---

## 🎯 Summary

Yeh project basically ek AI-powered voice assistant hai banking ke liye:

1. **Customer bolta hai** → Sarvam STT text mein convert karta hai
2. **PII hide hota hai** → Security ke liye
3. **Groq AI samajhta hai** → Intent detect + response
4. **Sarvam TTS bolti hai** → Audio response
5. **MongoDB mein save** → Future reference ke liye
6. **Report banta hai** → Bank staff ke liye

**Tech Stack:**
- FastAPI (Python backend)
- MongoDB Atlas (Cloud database)
- Groq AI (Llama 3.3 - brain)
- Sarvam AI (STT + TTS - voice)

**Tested Languages:** Hindi, English, Tamil, Telugu, Bengali, Marathi

---

Made with ❤️ for  Banking
