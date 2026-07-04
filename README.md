# SBI SmartFlow Agent

Yono Agent — an AI-powered financial assistant prototype for SBI. It handles onboarding, purchase goal planning, savings plans, and product recommendations.

## Features

- **Conversational onboarding** — collects name, life stage, profession, income, and goals
- **Purchase goal planner** — say *"I want a bike for 10,000"* and get three personalised savings plans
- **Flexible salary input** — accepts any amount (`35000`, `120rs`, `5 lakh`, etc.)
- **Financial health coach** — spending analysis and savings tips
- **Product recommendations** — curated SBI products in the sidebar

## Repository Structure

```
SBI-smart-flow-agent/
├── api/
│   ├── index.py           # Vercel serverless entry (FastAPI via Mangum)
│   └── requirements.txt   # Python deps for Vercel functions
├── backend/
│   ├── app.py             # FastAPI app + AI agent
│   ├── goal_planner.py    # Purchase intent & savings plan logic
│   └── requirements.txt   # Python deps for local dev
├── frontend/
│   ├── src/App.tsx        # React UI (chat, goals, tabs)
│   ├── vite.config.ts     # Vite + dev proxy to backend
│   └── package.json
├── vercel.json            # Vercel deployment config
└── README.md
```

## Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Optional — enable Claude AI instead of the built-in mock agent:

```bash
# Windows PowerShell
$Env:CLAUDE_API_KEY="your-anthropic-api-key"
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). API calls are proxied to the backend at `/api/*`.

## Deploy to Vercel

This project is configured for **full-stack Vercel deployment** — React frontend as static files and FastAPI backend as a Python serverless function.

### 1. Push to GitHub

The repo is set up for [github.com/Rohithjava777/SBI-smart-flow-agent](https://github.com/Rohithjava777/SBI-smart-flow-agent).

### 2. Import on Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import the GitHub repository
3. Leave the default settings — `vercel.json` handles build and routing
4. Add environment variable (optional):
   - `CLAUDE_API_KEY` — your Anthropic API key for live AI responses
5. Deploy

### 3. How it works on Vercel

| Path | Handler |
|------|---------|
| `/` | React SPA (`frontend/dist`) |
| `/api/chat` | FastAPI serverless function |
| `/api/health` | Health check endpoint |

No separate backend host is needed.

### Deploy via CLI (optional)

```bash
npm i -g vercel
vercel
```

## Demo Flow

1. **Login** with any credentials
2. Complete **onboarding** (name, age, profession, income, goals)
3. In chat, try: **"I want a bike for 288555"**
4. When asked, share your **monthly salary** (any format)
5. Review the **three savings plans** in chat and the Goal Tracker sidebar

## License

Prototype for the SBI Hackathon — for educational and demo purposes.
