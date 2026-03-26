from fastapi import APIRouter, HTTPException, Query
from models.query  import QueryRequest, RecommendRequest, ExplainRequest
from models.laptop import ScoredLaptop
from services.query_parser import parse_query
from services.scorer       import score_and_rank
from services.explainer    import generate_explanations
from db.supabase_client    import get_supabase

router = APIRouter()


# ── POST /api/analyze-query ──────────────────────────────────
@router.post("/analyze-query")
async def analyze_query(body: QueryRequest):
    """Agent 1 — parse natural language → structured intent."""
    intent = parse_query(body.query)
    return intent.model_dump()


# ── POST /api/recommend ──────────────────────────────────────
@router.post("/recommend")
async def recommend(body: RecommendRequest):
    """Agent 2 — fetch laptops from Supabase, score, return top N."""
    supabase = get_supabase()

    # Fetch laptops up to 2× budget to widen pool slightly
    budget_ceiling = int(body.budget_inr * 1.15)

    try:
        res = (
            supabase.table("laptops")
            .select("*")
            .lte("price_inr", budget_ceiling)
            .limit(200)
            .execute()
        )
        laptops = res.data or []
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")

    if not laptops:
        # Fallback: grab any laptops if none found in budget
        res = supabase.table("laptops").select("*").limit(100).execute()
        laptops = res.data or []

    if not laptops:
        return {"recommendations": []}

    intent_dict = body.model_dump()
    ranked = score_and_rank(laptops, intent_dict, limit=body.limit)

    return {"recommendations": ranked}


# ── POST /api/explain ────────────────────────────────────────
@router.post("/explain")
async def explain(body: ExplainRequest):
    """Agent 3 — generate plain-English explanations via LLM."""
    result = generate_explanations(
        laptops=body.laptops,
        user_query=body.user_query,
        intent=body.intent,
    )
    return result


# ── GET /api/laptops ─────────────────────────────────────────
@router.get("/laptops")
async def list_laptops(
    limit: int  = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0,  ge=0),
):
    """Return paginated laptop list."""
    supabase = get_supabase()
    try:
        res = (
            supabase.table("laptops")
            .select("*")
            .range(offset, offset + limit - 1)
            .execute()
        )
        return {"laptops": res.data or [], "count": len(res.data or [])}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── GET /api/laptops/{laptop_id} ─────────────────────────────
@router.get("/laptops/{laptop_id}")
async def get_laptop(laptop_id: str):
    """Return a single laptop by ID."""
    supabase = get_supabase()
    try:
        res = (
            supabase.table("laptops")
            .select("*")
            .eq("id", laptop_id)
            .single()
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Laptop not found")
        return res.data
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
