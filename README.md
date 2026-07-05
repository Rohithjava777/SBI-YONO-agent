# SBI  YONO Agent 🚀

An **AI-powered financial assistant** prototype for SBI that helps users plan purchases, build savings goals, and discover personalized financial products through conversational AI.

Developed for the **SBI Hackathon at GFF 2026** | [Team Terrain X](https://github.com/Rohithjava777)

---

## ✨ Features

- **Conversational Onboarding** — Intelligent multi-step onboarding collects name, life stage, profession, income, and financial goals
- **Smart Purchase Goal Planner** — Simply say *"I want a bike for 288,555"* and get three personalized, mathematically optimized savings plans
- **Flexible Salary Input** — Accepts salary in any format: `35000`, `5 lakh`, `120 per hour`, etc.
- **Financial Health Insights** — Spending analysis, savings recommendations, and budget optimization tips
- **Product Recommendations** — Curated SBI financial products displayed in a dynamic sidebar based on user profile
- **Claude AI Integration** — Optional live AI responses via Anthropic's Claude API for richer conversation context

---

## 🏗️ Architecture

### Tech Stack
| Layer | Tech |
|-------|------|
| **Frontend** | React 18 + TypeScript + Vite |
| **Backend** | FastAPI + Python |
| **AI Agent** | Claude API (Anthropic) or Mock Agent |
| **Deployment** | Vercel (Serverless) |
| **Database** | In-memory (demo) / Easy to integrate PostgreSQL |

### Repository Structure
```
SBI-smart-flow-agent/
├── api/
│   ├── index.py                    # Vercel serverless entry (FastAPI)
│   └── requirements.txt            # Python dependencies
├── backend/
│   ├── app.py                      # FastAPI application & AI routing
│   ├── goal_planner.py             # Purchase intent & savings calculations
│   ├── mock_agent.py               # Mock agent fallback
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main React component
│   │   ├── components/             # Reusable UI components
│   │   ├── styles/                 # Global & component styles
│   │   └── utils/                  # Helper functions
│   ├── vite.config.ts              # Vite config + dev proxy
│   ├── package.json                # Node dependencies
│   └── tsconfig.json
├── vercel.json                     # Vercel build & routing config
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 16+ & npm
- **Python** 3.9+
- **Anthropic API Key** (optional, for live Claude AI)

### 1. Clone the Repository
```bash
git clone https://github.com/Rohithjava777/SBI-smart-flow-agent.git
cd SBI-smart-flow-agent
```

### 2. Backend Setup

#### macOS / Linux
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

#### Windows (PowerShell)
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

**Enable Claude AI** (optional):
```bash
# macOS / Linux
export CLAUDE_API_KEY="your-anthropic-api-key"

# Windows PowerShell
$Env:CLAUDE_API_KEY="your-anthropic-api-key"
```

Backend runs at `http://127.0.0.1:8000` | Docs at `/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` (auto-proxies API calls to backend)

### 4. Test the Agent
Open [http://localhost:5173](http://localhost:5173) and:
1. Log in with any credentials
2. Complete onboarding
3. Ask: *"I want a bike for 288555"*
4. See three personalized savings plans in real-time

---

## 🌐 Deploy to Vercel

### One-Click Deployment

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Import on Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Select your GitHub repository
   - Vercel auto-detects the configuration from `vercel.json`

3. **Add Environment Variables** (Optional)
   - In Vercel Dashboard → Settings → Environment Variables
   - Add: `CLAUDE_API_KEY=your-anthropic-api-key`

4. **Deploy**
   - Click "Deploy" and wait ~2–3 minutes
   - Your app is live at `https://<your-project>.vercel.app`

### How It Works on Vercel

| Route | Handler |
|-------|---------|
| `/` | React SPA (static frontend) |
| `/api/*` | FastAPI serverless function |
| `/docs` | FastAPI Swagger UI |

**No separate backend host needed** — everything is in one Vercel project.

### Deploy via CLI (Optional)
```bash
npm install -g vercel
cd SBI-smart-flow-agent
vercel
```

---

## 📋 API Endpoints

### Health Check
```
GET /api/health
```
Response:
```json
{ "status": "ok", "agent": "claude" }
```

### Chat / Agent
```
POST /api/chat
Content-Type: application/json

{
  "user_id": "user123",
  "user_input": "I want a bike for 288555",
  "history": [...]
}
```

Response:
```json
{
  "agent_response": "Great! Let me help you plan...",
  "intent": "purchase_goal",
  "goals": [...],
  "recommendations": [...]
}
```

---

## 💡 Demo Flow

### Step 1: Login
Enter any username/password (no auth required in demo)

### Step 2: Onboarding
- **Name** → "Rohith"
- **Age** → 22
- **Profession** → "Student / Software Engineer"
- **Monthly Income** → "35000" or "5 lakh"
- **Financial Goals** → "Save for a bike, invest in crypto, build emergency fund"

### Step 3: Chat with Agent
```
You: "I want a bike for 288555"
Agent: "Perfect! What's your monthly income?"

You: "35000"
Agent: "Here are three savings plans:
  1. Aggressive (12 months) — ₹24,000/month
  2. Moderate (18 months) — ₹16,000/month
  3. Conservative (24 months) — ₹12,000/month"
```

### Step 4: View Goals & Products
- **Goal Tracker** sidebar shows your savings progress
- **Products** section recommends SBI savings accounts, investment options, and loan products

---

## 🛠️ Development

### Run Tests
```bash
cd backend
pytest tests/ -v
```

### Code Style
```bash
# Format code
black . --line-length=100

# Lint
flake8 . --max-line-length=100
```

### Environment Variables
Copy `.env.example` to `.env` and fill in:
```env
CLAUDE_API_KEY=sk-ant-...
DEBUG=true
```

---

## 📚 Project Structure Details

### `backend/app.py`
- FastAPI application setup
- `/api/health` and `/api/chat` endpoints
- Claude API integration with fallback to mock agent
- CORS configuration for frontend

### `backend/goal_planner.py`
- `parse_salary()` — Converts "5 lakh", "35000", etc. to numeric values
- `calculate_savings_plans()` — Generates three mathematically optimized plans
- `detect_purchase_intent()` — Extracts item name and price from user input

### `frontend/src/App.tsx`
- Chat interface with message history
- Onboarding form
- Goal tracker sidebar
- Product recommendations carousel

---

## 🤖 AI Agent Details

### Claude AI Mode (Recommended)
- **Richer context** — Claude understands financial scenarios deeply
- **Natural responses** — Conversational, contextual advice
- **Cost** — Pay-per-request via Anthropic API

### Mock Agent Mode (Fallback)
- **Deterministic responses** — Predictable for testing
- **No API key needed** — Works offline
- **Limited** — Rule-based, no LLM reasoning

**Toggle in `backend/app.py`:**
```python
# Set to "claude" or "mock"
AGENT_MODE = "claude"
```

---

## 🐛 Troubleshooting

### Frontend won't connect to backend
- Ensure backend is running on `http://127.0.0.1:8000`
- Check `vite.config.ts` proxy settings point to correct backend URL
- Clear browser cache: `Ctrl+Shift+Delete` or `Cmd+Shift+Delete`

### Claude API key not working
- Verify key format: starts with `sk-ant-`
- Check Anthropic dashboard for active billing
- Set env var before starting backend:
  ```bash
  export CLAUDE_API_KEY="your-key"
  ```

### Vercel deployment fails
- Check `vercel.json` syntax: `vercel logs`
- Ensure `api/requirements.txt` lists all dependencies
- Add `CLAUDE_API_KEY` in Vercel Environment Variables

### Savings plan calculations seem wrong
- Check `goal_planner.py` for the salary parsing logic
- Test manually: `python -c "from goal_planner import parse_salary; print(parse_salary('5 lakh'))"`

---

## 📈 Performance & Scalability

| Aspect | Current | Scalable To |
|--------|---------|-------------|
| **Users** | Demo (in-memory) | 100K+ (add PostgreSQL) |
| **API Calls** | Serverless (Vercel) | ∞ (auto-scaling) |
| **AI Requests** | Claude API | 1K+ req/min (rate limited) |
| **Frontend** | Static SPA | Global CDN via Vercel |

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is developed for the **SBI Hackathon at GFF 2026** and is provided for **educational and demonstration purposes only**.

**Proprietary Notice:** SBI, YONO, and related trademarks are the property of State Bank of India. This is an unofficial prototype.

---

## 🎯 Hackathon Context

**Hackathon:** SBI Hackathon at GFF 2026  
**Problem Statement:** Agentic AI for Banking (Conversational Financial Assistance)  
**Team:** Team Terrain X  
**Project:** SBI SmartFlow — Intelligent financial planning and product discovery

---

## 📞 Support

- **Issues?** Open a GitHub issue with details
- **Ideas?** Start a GitHub Discussion
- **Questions?** Check the [Wiki](https://github.com/Rohithjava777/SBI-smart-flow-agent/wiki) (coming soon)

---

## 🌟 Acknowledgments

- **Anthropic** — Claude API for intelligent AI responses
- **Vercel** — Full-stack deployment platform
- **SBI** — For the hackathon opportunity
- **Team Terrain X** — For bringing this to life

---

**Built with ❤️ for the SBI Hackathon**

⭐ If you find this helpful, please star the repo!
