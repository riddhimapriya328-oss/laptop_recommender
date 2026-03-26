"""
Agent 2 — deterministic scoring engine.
No LLM involved. Always produces consistent results.
"""
from typing import List, Dict, Any

USE_CASE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "gaming":  {"gpu": 0.40, "cpu": 0.30, "ram": 0.20, "price": 0.10},
    "coding":  {"cpu": 0.35, "ram": 0.35, "storage": 0.20, "price": 0.10},
    "student": {"battery": 0.35, "weight": 0.25, "price": 0.30, "cpu": 0.10},
    "design":  {"gpu": 0.30, "display": 0.25, "ram": 0.25, "cpu": 0.20},
    "budget":  {"price": 0.60, "ram": 0.20, "cpu": 0.20},
    "general": {"cpu": 0.25, "ram": 0.25, "price": 0.25, "battery": 0.25},
}

# GPU tier map — higher = better gaming / design capability
GPU_TIERS = {
    "rtx 4090": 100, "rtx 4080": 95, "rtx 4070": 90, "rtx 4060": 85,
    "rtx 3080": 82, "rtx 3070": 78, "rtx 3060": 74, "rtx 3050": 65,
    "rx 6800": 80, "rx 6700": 75, "rx 6600": 68, "rx 6500": 55,
    "gtx 1650": 50, "mx550": 35, "mx450": 30, "mx350": 25,
    "iris xe": 20, "iris plus": 15, "integrated": 10, "unknown": 10,
}


def _gpu_score(gpu: str | None) -> float:
    if not gpu:
        return 10.0
    g = gpu.lower()
    for key, score in GPU_TIERS.items():
        if key in g:
            return float(score)
    return 20.0  # unknown discrete GPU


def _safe(val, default=0):
    """Return val if numeric and > 0, else default."""
    try:
        v = float(val)
        return v if v > 0 else default
    except (TypeError, ValueError):
        return default


def _normalize(values: List[float]) -> List[float]:
    """Min-max normalize a list to [0, 100]."""
    mn, mx = min(values), max(values)
    if mx == mn:
        return [50.0] * len(values)
    return [(v - mn) / (mx - mn) * 100 for v in values]


def score_and_rank(
    laptops: List[Dict[str, Any]],
    intent: Dict[str, Any],
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    Filter by budget, score by use-case weights, return top N.
    Attaches: total_score, performance_score, battery_score,
              gaming_score, value_score to each laptop dict.
    """
    budget   = _safe(intent.get("budget_inr"), 60000)
    use_case = intent.get("use_case", "general")
    weights  = USE_CASE_WEIGHTS.get(use_case, USE_CASE_WEIGHTS["general"])

    # ── Step 1: Filter by budget ───────────────────────────────
    pool = [l for l in laptops if _safe(l.get("price_inr"), 999999) <= budget]

    if not pool:
        # Relax: take 10 cheapest
        pool = sorted(laptops, key=lambda l: _safe(l.get("price_inr"), 999999))[:10]

    if not pool:
        return []

    # ── Step 2: Collect raw feature vectors ───────────────────
    cpus     = [_safe(l.get("ram_gb"), 8) for l in pool]   # proxy: RAM for CPU power
    rams     = [_safe(l.get("ram_gb"), 8) for l in pool]
    gpus     = [_gpu_score(l.get("gpu")) for l in pool]
    storages = [_safe(l.get("storage_gb"), 256) for l in pool]
    batteries= [_safe(l.get("battery_hrs"), 5) for l in pool]
    weights_kg=[100 - _safe(l.get("weight_kg"), 2.0) * 20 for l in pool]  # lighter = higher
    displays = [_safe(l.get("display_in"), 15) for l in pool]
    prices   = [budget - _safe(l.get("price_inr"), budget) for l in pool]  # cheaper gap = value

    # ── Step 3: Normalize each dimension to 0-100 ─────────────
    n_cpu  = _normalize(cpus)
    n_ram  = _normalize(rams)
    n_gpu  = _normalize(gpus)
    n_sto  = _normalize(storages)
    n_bat  = _normalize(batteries)
    n_wt   = _normalize(weights_kg)
    n_disp = _normalize(displays)
    n_pr   = _normalize(prices)

    feature_map = {
        "cpu":     n_cpu,
        "ram":     n_ram,
        "gpu":     n_gpu,
        "storage": n_sto,
        "battery": n_bat,
        "weight":  n_wt,
        "display": n_disp,
        "price":   n_pr,
    }

    # ── Step 4: Weighted score ─────────────────────────────────
    max_price = max(_safe(l.get("price_inr"), 1) for l in pool) or 1

    scored = []
    for i, laptop in enumerate(pool):
        total = sum(
            feature_map.get(feat, [50.0] * len(pool))[i] * w
            for feat, w in weights.items()
        )

        price_inr = _safe(laptop.get("price_inr"), budget)
        value_score = (total / 100) * (budget / price_inr) * 50 if price_inr else 50

        entry = dict(laptop)
        entry["total_score"]       = round(total, 2)
        entry["performance_score"] = round((n_cpu[i] + n_ram[i]) / 2, 1)
        entry["battery_score"]     = round(n_bat[i], 1)
        entry["gaming_score"]      = round(n_gpu[i], 1)
        entry["value_score"]       = round(min(100, value_score), 1)
        scored.append(entry)

    # ── Step 5: Sort and return top N ─────────────────────────
    scored.sort(key=lambda x: x["total_score"], reverse=True)
    return scored[:limit]
