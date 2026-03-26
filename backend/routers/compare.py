from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from db.supabase_client import get_supabase

router = APIRouter()


class SaveCompareRequest(BaseModel):
    laptop_id: str


def _get_user_id(request: Request) -> str:
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


# ── POST /api/compare/save ───────────────────────────────────
@router.post("/compare/save")
async def save_compare(body: SaveCompareRequest, request: Request):
    """Save a laptop to user's comparison list (max 3)."""
    user_id  = _get_user_id(request)
    supabase = get_supabase()

    try:
        # Check existing count
        existing = (
            supabase.table("saved_comparisons")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )
        if len(existing.data or []) >= 3:
            raise HTTPException(
                status_code=400,
                detail="Maximum 3 laptops in comparison list. Remove one first.",
            )

        supabase.table("saved_comparisons").insert({
            "user_id":   user_id,
            "laptop_id": body.laptop_id,
        }).execute()

        return {"ok": True}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── GET /api/compare ─────────────────────────────────────────
@router.get("/compare")
async def get_compare(request: Request):
    """Return user's saved comparison laptops with full specs."""
    user_id  = _get_user_id(request)
    supabase = get_supabase()

    try:
        saved = (
            supabase.table("saved_comparisons")
            .select("laptop_id")
            .eq("user_id", user_id)
            .execute()
        )
        laptop_ids = [r["laptop_id"] for r in (saved.data or [])]

        if not laptop_ids:
            return {"laptops": []}

        laptops_res = (
            supabase.table("laptops")
            .select("*")
            .in_("id", laptop_ids)
            .execute()
        )
        return {"laptops": laptops_res.data or []}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── DELETE /api/compare/{laptop_id} ─────────────────────────
@router.delete("/compare/{laptop_id}")
async def remove_compare(laptop_id: str, request: Request):
    """Remove a laptop from user's comparison list."""
    user_id  = _get_user_id(request)
    supabase = get_supabase()

    try:
        supabase.table("saved_comparisons").delete().match({
            "user_id":   user_id,
            "laptop_id": laptop_id,
        }).execute()
        return {"ok": True}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
