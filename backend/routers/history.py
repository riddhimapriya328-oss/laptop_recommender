from fastapi import APIRouter, HTTPException, Request
from models.query       import HistorySaveRequest
from db.supabase_client import get_supabase
import json

router = APIRouter()


def _get_user_id(request: Request) -> str:
    """Extract user ID from Supabase JWT via Authorization header."""
    supabase = get_supabase()
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── POST /api/history ────────────────────────────────────────
@router.post("/history")
async def save_history(body: HistorySaveRequest, request: Request):
    """Save a query + its recommendations to Supabase."""
    user_id  = _get_user_id(request)
    supabase = get_supabase()

    try:
        # Insert query row
        q_res = (
            supabase.table("queries")
            .insert({
                "user_id":      user_id,
                "query_text":   body.query_text,
                "parsed_intent": body.intent,
            })
            .execute()
        )
        query_id = q_res.data[0]["id"]

        # Insert recommendation rows
        recs = [
            {
                "query_id":  query_id,
                "laptop_id": r.get("id"),
                "score":     r.get("total_score", 0),
                "rank":      i + 1,
            }
            for i, r in enumerate(body.recommendations)
            if r.get("id")
        ]
        if recs:
            supabase.table("recommendations").insert(recs).execute()

        return {"ok": True, "query_id": query_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── GET /api/history ─────────────────────────────────────────
@router.get("/history")
async def get_history(request: Request):
    """Return the user's 20 most recent queries."""
    user_id  = _get_user_id(request)
    supabase = get_supabase()

    try:
        res = (
            supabase.table("queries")
            .select("id, query_text, parsed_intent, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return {"history": res.data or []}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
