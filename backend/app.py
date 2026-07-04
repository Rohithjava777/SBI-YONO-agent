import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from goal_planner import handle_purchase_planning

app = FastAPI(title="SBI SmartFlow Prototype", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: list[dict]
    user_data: dict

def smart_mock_llm(messages: list[dict], user_data: dict) -> dict:
    last_msg = messages[-1]["text"].lower()
    
    reply = "I am processing your input to align with your financial goals."
    recs = []
    actions_logged = ["Analyzing input...", "Extracting entities"]
    health_update = None
    goal_update = None
    
    # 1. Tragic / Negative Sentiment Detection
    if any(word in last_msg for word in ["died", "passed away", "lost", "death", "accident"]):
        actions_logged = [
            "Analyzing sentiment...",
            "Detected critical/tragic life event.",
            "Updating memory store to prioritize support.",
            "Generating empathetic response."
        ]
        reply = "I am so incredibly sorry for your loss. Please accept my deepest condolences. During this difficult time, I have updated your profile and pulled up the necessary life insurance and claim assistance channels for you."
        recs = ["Term Life Insurance Support", "Claim Assistance Protocol", "Beneficiary Transfer Guidance"]
    
    # 2. Purchase Goal Planner (bike, car, any item + amount)
    elif purchase_result := handle_purchase_planning(messages, user_data):
        reply = purchase_result["reply"]
        actions_logged = purchase_result["actions_logged"]
        recs = purchase_result["recommendations"]
        goal_update = purchase_result["goal_update"]
        salary_update = purchase_result.get("salary_update")
        result = {
            "reply": reply,
            "actions_logged": actions_logged,
            "recommendations": recs,
            "health_update": health_update,
            "goal_update": goal_update,
        }
        if salary_update:
            result["salary_update"] = salary_update
        return result

    # 3. Financial Health Coach Trigger
    elif any(word in last_msg for word in ["spending", "health", "score", "expenses"]):
        actions_logged = [
            "Analyzing recent transactions...",
            "Calculating income vs expense ratio.",
            "Generating Financial Health Score."
        ]
        reply = "I've analyzed your recent financial data. Your savings rate has slightly dropped this month, but we can easily course-correct."
        health_update = {
            "score": 68,
            "savings_rate": "18%",
            "tip": "Your savings rate dropped from 25% to 18% this month. Reducing dining expenses by ₹2,000 would keep you on track for your goals."
        }
        recs = ["SBI YONO Spend Analyzer", "Automated SIP Setup"]

    # 4. Standard Positive Life Events
    elif any(word in last_msg for word in ["kid", "child", "baby"]):
        actions_logged = ["Detected life event: Childbirth", "Updating profile memory"]
        reply = "Congratulations on the new addition to your family! To help secure their future, I recommend looking into a Child Education Plan."
        recs = ["Child Education SIP", "Family Health Insurance"]

    # 5. Default Response
    else:
        actions_logged = ["Recalling user context", "Updating memory store"]
        reply = f"I have securely stored that in my memory, {user_data.get('name', '').split(' ')[0]}. I will recall this to efficiently plan and recommend the absolute best strategies for your benefit."
        recs = ["SBI Wealth Management", "Basic Savings"]

    return {
        "reply": reply,
        "actions_logged": actions_logged,
        "recommendations": recs,
        "health_update": health_update,
        "goal_update": goal_update
    }

async def get_yono_ai_response(messages: list[dict], user_data: dict) -> dict:
    purchase_result = handle_purchase_planning(messages, user_data)
    if purchase_result:
        result = {
            "reply": purchase_result["reply"],
            "actions_logged": purchase_result["actions_logged"],
            "recommendations": purchase_result["recommendations"],
            "health_update": None,
            "goal_update": purchase_result["goal_update"],
        }
        if purchase_result.get("salary_update"):
            result["salary_update"] = purchase_result["salary_update"]
        return result

    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        return smart_mock_llm(messages, user_data)

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    system_prompt = f"""You are 'Yono Agent', an Autonomous Intelligence for State Bank of India.
You do not act like a simple chatbot. You are a proactive agent which understands, remembers, recalls, and efficiently plans data for the absolute benefit of the customer.

User Profile & Memory:
{json.dumps(user_data, indent=2)}

CRITICAL INSTRUCTION:
1. ALWAYS scan for negative sentiment (died, death, loss). If found, express deep empathy and only suggest support services (Insurance claims), NEVER congratulations.
2. If the user mentions buying/purchasing something (bike, car, phone, etc.):
   - If they haven't given a budget, ask for the target amount.
   - If they haven't given monthly salary, ask for it warmly.
   - Once you have both, present THREE structured savings plans with different timelines (fast/balanced/comfortable), monthly savings amounts, and target dates. Personalise using their first name.
3. If they ask about spending/health, generate a health_update.
4. Constantly assure the user you are securely recalling their data to plan efficiently for their benefit.

Output valid JSON exactly matching this schema:
{{
  "reply": "Empathetic, agent-like response",
  "actions_logged": ["Analyzing sentiment...", "Updating Memory Store"],
  "recommendations": ["Product A", "Product B"],
  "health_update": {{"score": 75, "savings_rate": "20%", "tip": "Tip here"}} // or null,
  "goal_update": {{
    "name": "Purchase a Bike",
    "target_amount": 10000,
    "monthly_salary": 35000,
    "months": 6,
    "monthly_savings": 1667,
    "target_date": "January 2027",
    "plans": [
      {{"title": "Fast Track", "months": 3, "monthly_savings": 3334, "salary_percent": 10, "target_date": "October 2026"}},
      {{"title": "Balanced Plan", "months": 6, "monthly_savings": 1667, "salary_percent": 5, "target_date": "January 2027"}},
      {{"title": "Comfortable Plan", "months": 12, "monthly_savings": 834, "salary_percent": 2, "target_date": "July 2027"}}
    ],
    "status": "active",
    "progress": 0
  }} // or null
}}
"""

    claude_messages = []
    for m in messages:
        if m["role"] in ["user", "agent"]:
            role = "assistant" if m["role"] == "agent" else "user"
            claude_messages.append({"role": role, "content": m["text"]})

    if not claude_messages:
        claude_messages.append({"role": "user", "content": "Hello"})

    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1000,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": claude_messages,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                return smart_mock_llm(messages, user_data)
            data = resp.json()
            raw_text = data.get("content", [{}])[0].get("text", "{}")
            parsed = json.loads(raw_text)
            
            # Ensure keys exist
            if "actions_logged" not in parsed: parsed["actions_logged"] = ["Processed input"]
            if "health_update" not in parsed: parsed["health_update"] = None
            if "goal_update" not in parsed: parsed["goal_update"] = None
                
            return parsed
        except:
            return smart_mock_llm(messages, user_data)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "SBI SmartFlow Agent"}

@app.post("/api/chat")
async def chat_with_yono(req: ChatRequest):
    return await get_yono_ai_response(req.messages, req.user_data)
