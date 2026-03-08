<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=40&pause=1000&color=00D9FF&center=true&vCenter=true&width=600&lines=🎙️+DHWANI.AI; Voice-First+Banking+Assistant;Speak+Any+Indian+Language!" alt="Typing SVG" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq_AI-FF6B35?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Sarvam_AI-6366F1?style=for-the-badge&logo=audio&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/Ashurai84/Dhwani.ai?style=flat-square&color=00D9FF" />
  <img src="https://img.shields.io/github/stars/Ashurai84/Dhwani.ai?style=flat-square&color=FFD700" />
  <img src="https://img.shields.io/github/forks/Ashurai84/Dhwani.ai?style=flat-square&color=00FF88" />
  <img src="https://img.shields.io/badge/Made_in-India_🇮🇳-orange?style=flat-square" />
</p>

---

<h2 align="center">🌟 Revolutionizing Banking with Voice AI for Bharat 🌟</h2>

<p align="center">
  <b>Dhwani.ai</b> is an AI-powered Voice Banking Assistant that speaks <b>YOUR language</b>.<br/>
  Hindi, Tamil, Telugu, Bengali, Marathi, English — we understand them all!
</p>

---

## 🚀 What Makes Dhwani.ai Special?

<table>
<tr>
<td width="50%">

### 🎤 Voice-First Experience
No typing needed! Just speak naturally in your language and get instant voice responses.

### 🧠 Powered by Cutting-Edge AI
- **Groq AI** (Llama 3.3 70B) - Lightning-fast responses
- **Sarvam AI** - India's best STT & TTS

### 🔒 Bank-Grade Security
- PII Redaction (Aadhaar, Phone numbers auto-hidden)
- Secure conversation storage
- Human review flagging for sensitive queries

</td>
<td width="50%">

### 🌐 Multi-Language Magic
```
🇮🇳 Hindi      → "Mujhe loan chahiye"
🇮🇳 Tamil      → "எனக்கு கடன் வேண்டும்"
🇮🇳 Telugu     → "నాకు లోన్ కావాలి"
🇮🇳 Bengali    → "আমার লোন দরকার"
🇮🇳 Marathi    → "मला कर्ज हवे आहे"
🇬🇧 English    → "I need a loan"
```

### ⚡ Blazing Fast
- STT: ~2 seconds
- AI Response: ~500ms
- TTS: ~1 second
- **Total: Under 4 seconds!**

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                    🎙️ CUSTOMER SPEAKS                            ║
║                  "Mujhe home loan chahiye"                       ║
╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║                    🔊 SARVAM STT                                  ║
║              Voice → Text (saarika:v2.5)                         ║
║           Supports 10+ Indian Languages                          ║
╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║                    🔒 PII REDACTION                               ║
║         Auto-hide Aadhaar, Phone, Email, Account Numbers         ║
╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║                    🧠 GROQ AI (Llama 3.3)                         ║
║         Intent Detection + Contextual Response Generation        ║
║              Banking-Specific System Prompt                      ║
╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║                    🔊 SARVAM TTS                                  ║
║              Text → Voice (bulbul:v3)                            ║
║           Natural "Shubh" Voice @ 1.25x Speed                    ║
╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║                    🎧 CUSTOMER HEARS                              ║
║         "Ji bilkul! Aapko fixed rate chahiye ya floating?"       ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## ⚡ Quick Start

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Ashurai84/Dhwani.ai.git
cd Dhwani.ai/backend
```

### 2️⃣ Setup Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn httpx python-dotenv sqlalchemy pydantic
```

### 3️⃣ Configure API Keys
Create a `.env` file in the `backend` folder:
```env
GROQ_API_KEY="your_groq_api_key"        # Get from: console.groq.com
SARVAM_API_KEY="your_sarvam_api_key"    # Get from: sarvam.ai
```

### 4️⃣ Launch! 🚀
```bash
uvicorn main:app --reload --port 8000
```

### 5️⃣ Open in Browser
```
🌐 Voice Chat UI:  http://localhost:8000
📚 API Docs:       http://localhost:8000/docs
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | 🎤 Voice Chat Interface |
| `/interaction/start` | POST | 🆕 Start new session |
| `/interaction/audio` | POST | 🎙️ Send audio, get AI response |
| `/interaction/text` | POST | ⌨️ Text fallback |
| `/interaction/end` | POST | ✅ End session & generate report |
| `/reports` | GET | 📊 List all reports |
| `/sessions` | GET | 📋 List all sessions |
| `/conversations/{session_id}` | GET | 💬 Get session conversations |
| `/report/{report_id}` | GET | 📄 Get detailed report |
| `/ws/dashboard` | WebSocket | 📡 Real-time updates |

---

## 🛠️ Tech Stack

<table>
<tr>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="50"/>
<br/><b>Python 3.11+</b>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="50"/>
<br/><b>FastAPI</b>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" width="50"/>
<br/><b>SQLite</b>
</td>
<td align="center" width="20%">
🧠
<br/><b>Groq AI</b>
</td>
<td align="center" width="20%">
🎙️
<br/><b>Sarvam AI</b>
</td>
</tr>
</table>

---

## 🎯 Use Cases

<table>
<tr>
<td width="33%" align="center">
<h3>🏦 Bank Call Centers</h3>
<p>Automate customer queries with AI that speaks their language</p>
</td>
<td width="33%" align="center">
<h3>📱 Mobile Banking</h3>
<p>Voice-enabled banking for users who prefer speaking over typing</p>
</td>
<td width="33%" align="center">
<h3>🏪 Branch Kiosks</h3>
<p>Self-service voice assistants at bank branches</p>
</td>
</tr>
</table>

---

## 📁 Project Structure

```
Dhwani.ai/
├── 📂 backend/
│   ├── 🐍 main.py           # FastAPI server & endpoints
│   ├── 🧠 ai_service.py     # AI pipeline (STT → AI → TTS)
│   ├── 🗄️ database.py       # Database configuration
│   ├── 📋 models.py         # SQLAlchemy ORM models
│   ├── 📝 schemas.py        # Pydantic schemas
│   ├── 🎨 voice_test.html   # Voice chat UI
│   └── 🔐 .env              # API keys (not in repo)
└── 📖 README.md
```

---

## 🔒 Security Features

| Feature | Description |
|---------|-------------|
| 🔐 **PII Redaction** | Auto-masks Aadhaar, phone numbers, emails before AI processing |
| ⏱️ **Timeout Protection** | 3.5s AI timeout prevents hanging calls |
| 🚨 **Human Review Flag** | Low-confidence responses flagged for manual review |
| 📝 **Audit Trail** | All conversations logged for compliance |

---

## 🎙️ Try It Out!

Once the server is running, try saying:

| Language | Try Saying |
|----------|------------|
| Hindi | "Mujhe home loan chahiye" |
| Hindi | "Balance check karna hai" |
| Hindi | "FD rates kya hai?" |
| English | "I want to open an account" |
| Tamil | "கடன் பற்றி தெரிய வேண்டும்" |

---

## 📊 Performance Optimizations

| Metric | Value | Benefit |
|--------|-------|---------|
| STT Timeout | 8 sec | Prevents hanging on bad audio |
| AI Timeout | 3.5 sec | Fast fallback to human agent |
| TTS Timeout | 10 sec | Allows quality audio generation |
| Max Tokens | 400 | Concise, relevant responses |
| TTS Speed | 1.25x | Natural, brisk conversation |
| Silence Detection | 0.8 sec | Quick response triggers |

---

## 🚀 Deployment

### Railway.app (Recommended)
```bash
# Push to GitHub, then:
# 1. Connect Railway to your GitHub repo
# 2. Add environment variables
# 3. Deploy!
```

### Manual Deployment
```bash
# Install production server
pip install gunicorn

# Run
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔀 Submit PRs

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

<p align="center">
  <b>Ashutosh Rai</b><br/><br/>
  <a href="https://github.com/Ashurai84">
    <img src="https://img.shields.io/badge/GitHub-Ashurai84-181717?style=for-the-badge&logo=github" />
  </a>
</p>

---

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=00D9FF&center=true&vCenter=true&width=500&lines=Built+with+❤️+for+Bharat;Voice+Banking+ka+Future+🚀;Dhwani+%3D+Sound+in+Sanskrit+🎵" alt="Typing SVG" />
</p>

<p align="center">
  ⭐ <b>Star this repo if you found it helpful!</b> ⭐
</p>
