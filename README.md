# StyleDNA — Agentic AI Fashion Stylist

StyleDNA is a full-stack AI fashion assistant that reasons over real-time weather, a user's personal wardrobe, and expert styling knowledge to generate personalized outfit recommendations — through a genuine multi-step AI agent, not a single prompt-response call.

🔗 **Live Demo:** 
https://grwm-agent.onrender.com

---

## Table of Contents

- [The Problem It Solves](#the-problem-it-solves)
- [How It Works (High Level)](#how-it-works-high-level)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [The Agent — How It Thinks](#the-agent--how-it-thinks)
- [Project Structure](#project-structure)
- [Core Flows Explained](#core-flows-explained)
- [Authentication Flow](#authentication-flow)
- [Database Schema](#database-schema)
- [Running Locally](#running-locally)
- [Environment Variables](#environment-variables)
- [Key Engineering Decisions](#key-engineering-decisions)
- [What I'd Improve Next](#what-id-improve-next)

---

## The Problem It Solves

Most "AI fashion" tools either show generic outfit photos or are simple prompt-to-response chatbots with no real context. StyleDNA is different — it's an **agent** that actively gathers information before answering, the same way a human stylist would:

1. A human stylist checks the weather before suggesting an outfit
2. They look at what's actually in your closet
3. They combine both with fashion expertise to give a final recommendation

StyleDNA's AI agent does exactly this, autonomously, using real APIs and a real database — not hallucinated information.

---

## How It Works (High Level)

```
User: "What should I wear tomorrow for work?"
                    ↓
        Agent receives the question
                    ↓
   Agent THINKS: "I need weather data first"
                    ↓
        Calls get_weather("Delhi")
                    ↓
   Agent THINKS: "Now I need their wardrobe"
                    ↓
        Calls get_wardrobe("work")
                    ↓
   Agent THINKS: "I have enough to give advice"
                    ↓
        Calls get_style_advice(combined context)
                    ↓
        Returns final, reasoned answer to user
```

This is the **ReAct** pattern (Reason + Act): the model alternates between thinking out loud and taking actions, observing results, and deciding what to do next — until it has enough information to answer.

---

## System Architecture

StyleDNA deliberately uses **two separate backend services** in two different languages, talking to each other over HTTP. This wasn't accidental complexity — it mirrors how real production systems are often composed of specialized services.

```
┌─────────────────────────────────────────────────────────┐
│                         BROWSER                          │
│              (renders Flask's HTML templates)             │
└───────────────────────────┬───────────────────────────────┘
                             │ HTTP (forms, cookies)
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  FLASK SERVER (Python)                   │
│                     localhost:5000                        │
│  • Renders all pages (login, signup, wardrobe, chat)      │
│  • Holds the user's session (Flask session)                │
│  • Forwards auth/wardrobe requests to Node.js               │
│  • Calls the LangChain agent directly for AI chat          │
└────────────┬───────────────────────────┬──────────────────┘
             │ HTTP + JWT cookie         │ Python function call
             ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────────────┐
│   NODE.JS BACKEND        │   │     LANGCHAIN AGENT          │
│   (Express)               │   │     (agent.py)                │
│   localhost:8000          │   │                                │
│                            │   │  Reasons step-by-step using:   │
│  • Signup / Login / Logout│   │  ┌──────────┬─────────────┐    │
│  • JWT issuing & verify   │   │  │get_weather│get_wardrobe│    │
│  • bcrypt password hash   │   │  └────┬─────┴──────┬──────┘    │
│  • Wardrobe CRUD          │   │       │             │           │
│  • protectRoute middleware│   │       ▼             ▼           │
└────────────┬───────────────┘   │  OpenWeather   calls back to   │
             │                   │     API        Node.js's        │
             ▼                   │                /api/wardrobe    │
┌─────────────────────────┐     │       │                          │
│       MONGODB            │     │       ▼                          │
│  (Atlas, cloud-hosted)   │◄────┤  get_style_advice                │
│                            │     │  → calls Groq (Llama 3.1)       │
│  users collection:         │     └─────────────────────────────┘
│  { username, password,     │
│    email, wardrobe: [...] }│
└─────────────────────────┘
```

**Why split it this way?**

- The Node.js service owns *identity and data* — authentication and the wardrobe database. This is a well-understood, battle-tested pattern (Express + JWT + MongoDB).
- The Python service owns *reasoning* — LangChain's agent ecosystem is Python-first, so the AI logic lives there.
- Flask sits in the middle as the **presentation layer**, gluing both together for the end user. It never talks to MongoDB directly — it always goes through Node.js's authenticated API, which keeps a single source of truth for data access rules.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Auth & Data API | Node.js + Express | Mature, well-known REST API patterns |
| Database | MongoDB + Mongoose | Flexible schema for nested wardrobe arrays |
| Auth | JWT + bcrypt | Stateless tokens, industry-standard hashing |
| AI Orchestration | LangChain (ReAct agent) | Production-grade agent framework |
| LLM | Groq (Llama 3.1 8B Instant) | Fast, free-tier friendly, generous limits |
| Weather Data | OpenWeatherMap API | Real-world grounding for recommendations |
| Frontend | Flask + Jinja2 templates | Lightweight, server-rendered, no JS framework needed |

---

## The Agent — How It Thinks

The agent isn't a single Gemini/GPT call. It's built using LangChain's `create_react_agent`, which wraps an LLM with a **ReAct prompt template** instructing it to alternate between `Thought`, `Action`, and `Observation` until it reaches a `Final Answer`.

```python
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=6
)
```

### The Three Tools

Each tool is a plain Python function decorated with `@tool`, which makes it callable by the agent. The **docstring is critical** — it's what the agent reads to decide *when* to use each tool.

```python
@tool
def get_weather(city: str = "Delhi") -> str:
    """Get current weather for a city.
    Use this when you need to know the weather
    to make outfit recommendations."""
```

| Tool | What it does | Talks to |
|---|---|---|
| `get_weather` | Fetches live temperature, conditions, humidity | OpenWeatherMap API |
| `get_wardrobe` | Fetches the logged-in user's clothing items | Node.js `/api/wardrobe` (with JWT) |
| `get_style_advice` | Generates styling tips combining context | Groq LLM directly |

### A Real Trace From The Logs

```
Thought: I need to know the current weather in Delhi
Action: get_weather
Action Input: Delhi
Observation: Temperature: 41°C, broken clouds, humidity 22%

Thought: Now I should check the user's wardrobe
Action: get_wardrobe
Action Input: occasion='work'
Observation: White Linen Shirt, Beige Chinos

Thought: I have enough information to give style advice
Action: get_style_advice
Action Input: "work outfit for 41°C Delhi heat using white shirt and chinos"
Observation: 🎯 Recommended Outfit: White Linen Shirt + Beige Chinos...

Thought: I now know the final answer
Final Answer: Wear your white linen shirt with beige chinos...
```

This trace is real output from `verbose=True` — every tool call is genuinely executed, not simulated.

### Conversation Memory

Because each call to `ask_style_agent()` is otherwise stateless, the last 6 messages of chat history are manually injected into the prompt so the agent can resolve follow-up questions like *"what about shoes?"* in context of the previous answer.

```python
history_text = ""
for msg in chat_history[-6:]:
    role = "User" if msg["role"] == "user" else "Stylist"
    history_text += f"{role}: {msg['content']}\n"

full_question = f"""
The user's city is {user_city}.
Previous conversation:
{history_text}
New question: {question}
"""
```

---

## Project Structure

```
StyleDNA Project/
│
├── backend/                     ← Node.js / Express API
│   ├── server.js                  entry point, mounts routes
│   ├── routes/
│   │   ├── auth.routes.js         /api/auth/* endpoints
│   │   └── wardrobe.routes.js     /api/wardrobe/* endpoints
│   ├── controllers/
│   │   ├── auth.controller.js     signup/login/logout/getMe logic
│   │   └── wardrobe.controller.js add/get/delete wardrobe items
│   ├── models/
│   │   └── user.model.js          Mongoose schema (user + wardrobe)
│   ├── middleware/
│   │   └── protectRoute.js        JWT verification middleware
│   ├── DB/
│   │   └── connectMongoDB.js      Mongoose connection setup
│   └── lib/utils/
│       └── generateToken.js       JWT creation + cookie setting
│
└── agent/                       ← Python / Flask + LangChain
    ├── app.py                     Flask routes, session handling
    ├── agent.py                   LangChain ReAct agent setup
    ├── tools/
    │   ├── weather_tool.py        OpenWeatherMap integration
    │   ├── wardrobe_tool.py       calls Node.js wardrobe API
    │   └── style_tool.py          Groq LLM styling advice
    ├── templates/                 Jinja2 HTML pages
    └── static/style.css
```

---

## Core Flows Explained

### 1. Signup → Login → Session

```
Browser submits signup form (Flask /signup)
        ↓
Flask forwards data as JSON to Node.js /api/auth/signup
        ↓
Node.js validates, hashes password with bcrypt, saves to MongoDB
        ↓
Node.js generates a JWT, sets it as an HTTP-only cookie on its response
        ↓
Flask extracts that cookie value and stores it in its own
Flask session (because Flask and Node.js are different
origins/ports — cookies don't transfer automatically)
        ↓
Flask redirects user to /chat, now "logged in" on both sides
```

### 2. Adding a Wardrobe Item

```
User submits the wardrobe form (Flask /wardrobe)
        ↓
Flask sends item data + JWT cookie to Node.js /api/wardrobe/add
        ↓
Node.js's protectRoute middleware verifies the JWT
        ↓
wardrobe.controller.js pushes the new item into
the user's wardrobe array in MongoDB
        ↓
Flask re-fetches the updated wardrobe list and re-renders the page
```

### 3. Asking The AI Stylist

```
User types a question in the chat UI (Flask /chat, POST)
        ↓
Flask appends the question to session["chat_history"]
        ↓
Flask calls ask_style_agent(question, jwt_token, city, chat_history)
        ↓
agent.py sets os.environ["USER_JWT"] so wardrobe_tool.py
can authenticate its own call back to Node.js
        ↓
AgentExecutor runs the full ReAct loop (see trace above)
        ↓
Final answer returned to Flask
        ↓
Flask appends the answer to chat_history and re-renders /chat
```

---

## Authentication Flow

JWT was chosen over server-side sessions because the system is split across two independently-running services (Node.js and Python) — a stateless token that either service can verify (given the shared secret) is simpler than synchronizing session stores across two languages.

```javascript
// generateToken.js
const token = jwt.sign(
    { userId },
    process.env.JWT_SECRET,
    { expiresIn: "15d" }
);

res.cookie("jwt", token, {
    httpOnly: true,   // inaccessible to client-side JS — mitigates XSS token theft
    secure: false,    // would be true behind HTTPS in production
    maxAge: 15 * 24 * 60 * 60 * 1000
});
```

```javascript
// protectRoute.js — runs before any protected controller
const token = req.cookies.jwt;
if (!token) return res.status(401).json({ error: "Not authorized" });

const decoded = jwt.verify(token, process.env.JWT_SECRET);
const user = await User.findById(decoded.userId).select("-password");

req.user = user;
next();
```

Passwords are never stored or transmitted in plain text — `bcrypt.hash()` salts and hashes them before they ever reach the database, and `.select("-password")` ensures the hash never leaves the server in any API response.

---

## Database Schema

A single `users` collection holds each user's wardrobe as a **nested array of subdocuments**, rather than a separate `wardrobe_items` collection. This was a deliberate choice — wardrobe items are always queried in the context of "this user's wardrobe," never independently, so embedding avoids an unnecessary join/lookup.

```javascript
const WardrobeItemSchema = new mongoose.Schema({
    name:     { type: String, required: true },
    category: { type: String, required: true }, // top, bottom, dress, shoes...
    color:    { type: String, required: true },
    occasion: { type: String, default: "casual" },
    season:   { type: String, default: "all" },
    emoji:    { type: String, default: "👕" },
});

const UserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    fullname: { type: String, required: true },
    email:    { type: String, required: true, unique: true },
    password: { type: String, required: true },
    city:     { type: String, default: "Delhi" },
    wardrobe: [WardrobeItemSchema],
}, { timestamps: true });
```

---

## Running Locally

**1. Backend (Node.js)**

```bash
cd backend
npm install
# create a .env file (see Environment Variables below)
npm run dev
```

**2. Agent (Python)**

```bash
cd agent
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
# create a .env file (see Environment Variables below)
python app.py
```

**3. Visit** `http://localhost:5000`

Both services must be running simultaneously — Flask depends on the Node.js API for all auth and wardrobe operations.

---

## Environment Variables

**`backend/.env`**
```
MONGO_URI=your_mongodb_atlas_connection_string
JWT_SECRET=any_long_random_string
PORT=8000
```

**`agent/.env`**
```
BACKEND_URL=http://localhost:8000/api
FLASK_SECRET=any_long_random_string
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
```

---

## Key Engineering Decisions

- **Two-service architecture over a monolith** — chosen specifically to use Node.js's mature auth ecosystem alongside Python's mature AI/agent ecosystem (LangChain), rather than forcing one language to do both jobs adequately.
- **ReAct agent over a single prompt** — a single Gemini/GPT call cannot fetch live weather or query a database mid-generation. The agent pattern lets the model decide *what information it's missing* and go get it.
- **String-only tool inputs** — early iterations used multi-parameter tools (`occasion, weather, wardrobe_items`), which the ReAct agent struggled to call correctly (it's optimized for single-string action inputs). Consolidating to one `context: str` parameter per tool fixed reliability.
- **JWT over sessions** — needed for the cross-service architecture; Flask manually extracts and re-attaches the cookie because the two servers are on different ports/origins.
- **Switched LLM providers (Gemini → OpenAI → Groq)** during development after hitting free-tier rate limits and billing requirements — Groq's free tier (Llama 3.1 8B) proved both fast and reliable for an agent making 4–5 calls per user question.

---

## What I'd Improve Next

- Add response streaming so the agent's thinking is visible to the user in real time, not just in server logs
- Move from Flask sessions to a proper shared-secret JWT validated independently by Flask (currently Flask trusts its own session rather than re-verifying the token itself)
- Add a vector store (e.g. ChromaDB) so the agent can reason over *past* outfit choices, not just the current wardrobe snapshot
- Replace polling-style wardrobe fetches with a cached layer to reduce repeated calls to Node.js during a single agent run
