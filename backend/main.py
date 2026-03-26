from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers.recommend import router as recommend_router
from routers.history   import router as history_router
from routers.compare   import router as compare_router
from db.supabase_client import get_supabase
from models.query       import AuthRequest

app = FastAPI(
    title="LaptopMatch API",
    description="AI-powered laptop recommendation backend",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────
app.include_router(recommend_router, prefix="/api")
app.include_router(history_router,   prefix="/api")
app.include_router(compare_router,   prefix="/api")


# ── Auth endpoints ───────────────────────────────────────────
@app.post("/api/auth/signup")
async def signup(body: AuthRequest):
    """Create a new user via Supabase Auth."""
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_up({
            "email":    body.email,
            "password": body.password,
            "options":  {"data": {"full_name": body.full_name or ""}},
        })
        if not res.session:
            raise HTTPException(
                status_code=400,
                detail="Signup failed — check your email and try again.",
            )
        return {
            "access_token": res.session.access_token,
            "user_id":      res.user.id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/auth/login")
async def login(body: AuthRequest):
    """Sign in an existing user via Supabase Auth."""
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_password({
            "email":    body.email,
            "password": body.password,
        })
        if not res.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "access_token": res.session.access_token,
            "user_id":      res.user.id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid email or password")


# ── Health check ─────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "LaptopMatch API"}


# ── Run directly ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
