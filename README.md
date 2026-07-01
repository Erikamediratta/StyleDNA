# GRWM — Get Ready With Me (Generative Recommendations With Me)

An AI fashion assistant that actually thinks before answering. Ask it what to wear and it checks the weather, looks through your wardrobe, and gives you a real recommendation — not a generic one.

🔗 **Live:** https://grwm-agent.onrender.com  
📂 **Code:** https://github.com/Erikamediratta/StyleDNA

---

## What it does

You type something like "what should I wear to work tomorrow?" and the AI agent:

1. Checks the actual weather in your city via OpenWeatherMap
2. Looks up the clothes you've saved in your wardrobe
3. Combines both with a language model to give you a specific outfit recommendation

It's not a single API call — it's a proper ReAct agent that decides what information it needs, fetches it, and reasons over it before responding.

---

## Why I built it this way

Most "AI fashion" demos I saw were just prompt → response. No context, no real data, no reasoning. I wanted to build something where the AI actually had to *do* things before it could answer — which meant building a real agentic loop with tool calls.

I also wanted to practice a two-service architecture since it's common in real engineering teams: one service owns auth and data (Node.js), another owns the AI logic (Python). They talk to each other over HTTP using JWT for authentication.

---

## Stack

**Backend (auth + data)**
- Node.js, Express
- MongoDB + Mongoose
- JWT for auth, bcrypt for password hashing

**AI layer**
- Python, Flask
- LangChain (ReAct agent with `create_react_agent`)
- Groq API running Llama 3.3 70B
- OpenWeatherMap for live weather

---

## How the agent actually works

LangChain's ReAct pattern lets the model alternate between thinking and acting:

```
Thought: I need to know the weather first
Action: get_weather → "Mumbai, 34°C, humid"

Thought: Now I need to see what they own
Action: get_wardrobe → "white kurta, blue jeans, sneakers"

Thought: I have enough to give a good answer
Action: get_style_advice → combines everything into a recommendation

Final Answer: "Given the heat, go with your white kurta and jeans..."
```

Each tool is a plain Python function decorated with `@tool`. The docstring is what the model reads to decide *when* to use it — so writing good descriptions matters a lot.

I learned this the hard way: an 8B model (llama-3.1-8b-instant) would get stuck in loops and never reach a final answer. Switching to the 70B model (llama-3.3-70b-versatile) fixed it completely. Smaller models struggle with multi-step ReAct loops.

---

## Architecture

```
Browser
   ↓
Flask (port 5000) — handles pages, sessions, calls the agent
   ↓                              ↓
Node.js (port 8000)         LangChain Agent
   ↓                         ↙    ↓    ↘
MongoDB               weather  wardrobe  style_advice
                      API      (→ Node)   (→ Groq LLM)
```

Flask sits in the middle — it's the only thing the user talks to. It calls Node.js for auth and wardrobe data, and calls the Python agent directly for AI chat. The agent itself calls Node.js's wardrobe API using the user's JWT token so it fetches *their* specific clothes.

---

## One thing that tripped me up

JWT cookies don't automatically transfer between services on different ports. When Node.js sets the cookie, Flask has to manually extract it from the response and store it in its own session — then re-attach it to every request it makes back to Node.js. Took a while to figure out why authentication kept failing across services.

---

## Project structure

```
StyleDNA/
├── backend/                  Node.js API
│   ├── server.js
│   ├── routes/
│   │   ├── auth.routes.js
│   │   └── wardrobe.routes.js
│   ├── controllers/
│   │   ├── auth.controller.js
│   │   └── wardrobe.controller.js
│   ├── models/user.model.js
│   ├── middleware/protectRoute.js
│   └── lib/utils/generateToken.js
│
└── agent/                    Python AI layer
    ├── app.py                Flask routes + session handling
    ├── agent.py              LangChain ReAct agent
    ├── tools/
    │   ├── weather_tool.py
    │   ├── wardrobe_tool.py
    │   └── style_tool.py
    └── templates/            HTML pages
```

---

## Running locally

**Backend:**
```bash
cd backend
npm install
# add .env with MONGO_URI, JWT_SECRET
npm run dev
```

**Agent:**
```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# add .env with GROQ_API_KEY, OPENWEATHER_API_KEY, BACKEND_URL, FLASK_SECRET
python app.py
```

Both need to run at the same time. Backend on port 8000, Flask on 5000.

---

## What I'd do differently

- Use a shared Redis store for sessions instead of Flask's built-in session (would make scaling easier)
- Add streaming so the agent's reasoning is visible to the user in real time
- Store past outfit choices so the agent can reference what you've worn recently
- The wardrobe tool fetches all items every time — a simple cache would reduce unnecessary API calls during a single agent run

---

Built by Erika Mediratta · [LinkedIn](your-linkedin-url) · [GitHub](https://github.com/Erikamediratta)
