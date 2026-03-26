# LaptopMatch — AI Laptop Recommendation Assistant

An AI-powered assistant that recommends the top 1–3 laptops based on your needs.
Type what you want in plain language — get clear picks with human-readable explanations.

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 18, React Router v6, Axios    |
| Backend    | FastAPI (Python 3.11+), Pydantic v2 |
| Database   | Supabase (PostgreSQL)               |
| Auth       | Supabase Auth (email + Google)      |
| AI         | OpenAI GPT-4o-mini (3-agent system) |

---

## Project Structure

```
laptop-recommender/
├── frontend/
│   ├── src/
│   │   ├── pages/          Landing, Chat, Login, Signup
│   │   ├── components/     NavBar, SearchBar, CategoryBubbles,
│   │   │                   ChatMessage, LaptopCard, ScoreBar, LaptopDetail
│   │   ├── lib/api.js      All FastAPI calls
│   │   └── styles/         CSS Modules (beige design system)
│   └── package.json
│
├── backend/
│   ├── main.py             FastAPI entry + auth endpoints
│   ├── routers/            recommend, history, compare
│   ├── services/
│   │   ├── query_parser.py Agent 1 — LLM query → intent
│   │   ├── scorer.py       Agent 2 — rule-based scoring
│   │   └── explainer.py    Agent 3 — LLM explanations
│   ├── models/             Pydantic schemas
│   ├── db/                 Supabase client
│   └── seed_laptops.py     CSV → Supabase ingest
│
└── README.md
```

---

## Quick Start

### 1 — Clone the repo

```bash
git clone https://github.com/your-username/laptop-recommender.git
cd laptop-recommender
```

### 2 — Set up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project.
2. In the **SQL Editor**, run all the SQL from the section below.
3. In **Project Settings → API**, copy:
   - **Project URL** → `SUPABASE_URL`
   - **service_role** secret key → `SUPABASE_SERVICE_KEY`

### 3 — Set up the backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
OPENAI_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o-mini
```

### 4 — Seed the laptop database

Download a dataset from Kaggle:
👉 https://www.kaggle.com/datasets/muhammetvarl/laptop-price

Or search: **"laptop price dataset"** on [kaggle.com](https://www.kaggle.com)

```bash
python seed_laptops.py --file path/to/laptop_price.csv
```

### 5 — Run the backend

```bash
uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 6 — Set up the frontend

```bash
cd ../frontend
npm install
cp .env.example .env
```

The default `.env` is already correct:
```
VITE_API_URL=http://localhost:8000
```

### 7 — Run the frontend

```bash
npm run dev
# Opens at http://localhost:5173
```

---

## Supabase SQL Setup

Run this in the Supabase **SQL Editor**:

```sql
-- Laptops table
CREATE TABLE laptops (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL,
  brand        TEXT,
  price_inr    INTEGER,
  cpu          TEXT,
  gpu          TEXT,
  ram_gb       INTEGER,
  storage_gb   INTEGER,
  battery_wh   INTEGER,
  battery_hrs  FLOAT,
  weight_kg    FLOAT,
  display_in   FLOAT,
  display_type TEXT,
  os           TEXT,
  source_url   TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE laptops ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public can read laptops" ON laptops
  FOR SELECT USING (true);

-- Queries table
CREATE TABLE queries (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  query_text    TEXT,
  parsed_intent JSONB,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own queries" ON queries
  FOR ALL USING (auth.uid() = user_id);

-- Recommendations table
CREATE TABLE recommendations (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id   UUID REFERENCES queries(id) ON DELETE CASCADE,
  laptop_id  UUID REFERENCES laptops(id),
  score      FLOAT,
  explanation TEXT,
  rank       INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own recommendations" ON recommendations
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM queries q
      WHERE q.id = query_id AND q.user_id = auth.uid()
    )
  );

-- Saved comparisons
CREATE TABLE saved_comparisons (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  laptop_id  UUID REFERENCES laptops(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE saved_comparisons ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own comparisons" ON saved_comparisons
  FOR ALL USING (auth.uid() = user_id);
```

---

## Environment Variables

### backend/.env

| Variable              | Description                              |
|-----------------------|------------------------------------------|
| `SUPABASE_URL`        | Your Supabase project URL                |
| `SUPABASE_SERVICE_KEY`| Service role key (full DB access)        |
| `OPENAI_API_KEY`      | OpenAI API key (get at platform.openai.com) |
| `LLM_MODEL`           | Model name, default `gpt-4o-mini`        |

### frontend/.env

| Variable       | Description                  |
|----------------|------------------------------|
| `VITE_API_URL` | Backend URL, default `http://localhost:8000` |

---

## Using HuggingFace Instead of OpenAI (Free Option)

If you don't have an OpenAI key, edit `backend/services/query_parser.py`
and `backend/services/explainer.py` to use the HuggingFace Inference API:

```python
import requests

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

def call_llm(prompt: str) -> str:
    res = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": prompt, "parameters": {"max_new_tokens": 300}},
    )
    return res.json()[0]["generated_text"]
```

Add `HF_TOKEN=hf_your_token` to `backend/.env`.

---

## API Endpoints

| Method | Path                    | Description                          |
|--------|-------------------------|--------------------------------------|
| POST   | `/api/auth/signup`      | Create account                       |
| POST   | `/api/auth/login`       | Sign in                              |
| POST   | `/api/analyze-query`    | Agent 1 — parse user query           |
| POST   | `/api/recommend`        | Agent 2 — score & return top laptops |
| POST   | `/api/explain`          | Agent 3 — generate explanations      |
| GET    | `/api/laptops`          | List all laptops (paginated)         |
| GET    | `/api/laptops/{id}`     | Single laptop detail                 |
| POST   | `/api/history`          | Save query history                   |
| GET    | `/api/history`          | Get user history                     |
| POST   | `/api/compare/save`     | Save laptop to compare list          |
| GET    | `/api/compare`          | Get compare list                     |
| DELETE | `/api/compare/{id}`     | Remove from compare list             |
| GET    | `/health`               | Health check                         |

Interactive docs: http://localhost:8000/docs

---

## Demo Flow

```
1. Open http://localhost:5173
2. Click "Let's start recommending" → type a query or click a bubble
3. Sign up (if not logged in) → redirected to /chat
4. See 1–3 laptop cards with score bars and spec chips
5. Click "See full details →" → slide-in panel with full specs + AI explanation
6. History auto-saves to Supabase sidebar
```

---

## How the AI Works

```
User query (plain text)
        │
        ▼
  Agent 1 (LLM)          query_parser.py
  Extracts: budget, use_case, priorities
        │
        ▼
  Agent 2 (Rule-based)   scorer.py
  Filters by budget → normalizes specs →
  weighted score by use case → top 3
        │
        ▼
  Agent 3 (LLM)          explainer.py
  Writes 2-sentence explanation per laptop
  + 1-sentence "why not others"
        │
        ▼
  Chat UI displays laptop cards + explanations
```

Scoring never relies on the LLM — it's always deterministic.
LLM is used only for parsing and explanation generation, with safe fallbacks.

---

## Evaluation Criteria Coverage

| Criterion                    | Implementation                              |
|------------------------------|---------------------------------------------|
| Accuracy of recommendations  | Weighted scoring per use-case (Agent 2)     |
| User experience and clarity  | Beige editorial UI, chat bubbles, spec bars |
| Innovation in design         | 3-agent system, value-for-money score       |
| Quality of explanations      | Context-aware LLM prompting (Agent 3)       |
| Chat-style interface ✓       | Full conversational Chat.jsx page           |
| Visual spec comparison ✓     | Detail panel with full specs table          |
| Multi-agent reasoning ✓      | 3 separate agents with clear boundaries     |

---

Built for Hackathon 2025.
