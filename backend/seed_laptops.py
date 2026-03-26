"""
seed_laptops.py — one-time script to load a laptop dataset CSV into Supabase.

Usage:
    python seed_laptops.py --file path/to/laptops.csv

Download a dataset from Kaggle:
    https://www.kaggle.com/datasets/muhammetvarl/laptop-price
    or search "laptop price dataset" on kaggle.com

The script auto-detects common column names from popular datasets.
"""

import os
import re
import sys
import argparse
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

BATCH_SIZE = 50


# ── Helpers ──────────────────────────────────────────────────
def _extract_number(s, default=0) -> float:
    """Pull the first float from a string like '8GB' or '1.5 kg'."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return default
    match = re.search(r"[\d.]+", str(s))
    return float(match.group()) if match else default


def _inr(val) -> int:
    """Convert price to INR integer. Handles $, £, ₹, plain numbers."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0
    s = str(val).replace(",", "").strip()
    num = re.sub(r"[^\d.]", "", s)
    try:
        price = float(num)
    except ValueError:
        return 0
    # If price looks like USD (< 5000), convert to INR
    if price < 5000:
        price *= 83
    return int(price)


def _col(df: pd.DataFrame, *candidates: str):
    """Return the first matching column name (case-insensitive)."""
    lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def clean_dataframe(df: pd.DataFrame) -> list[dict]:
    """Normalize a raw Kaggle CSV → list of laptop dicts for Supabase."""

    rows = []
    for _, row in df.iterrows():
        def g(*keys):
            col = _col(df, *keys)
            return row[col] if col else None

        name  = str(g("Product", "laptop_name", "name", "model") or "Unknown Laptop").strip()
        brand = str(g("Company", "brand", "manufacturer") or "").strip()
        if not brand and " " in name:
            brand = name.split()[0]

        price_raw = g("Price_euros", "Price", "price", "price_inr", "price_usd")
        price_inr = _inr(price_raw)

        cpu = str(g("Cpu", "cpu", "processor", "CPU_model") or "").strip() or None
        gpu = str(g("Gpu", "gpu", "GPU_model", "graphics") or "").strip() or None
        if gpu and gpu.lower() in ("nan", "none", ""):
            gpu = None

        ram_raw = g("Ram", "ram", "RAM", "ram_gb")
        ram_gb  = int(_extract_number(ram_raw, 8))

        sto_raw    = g("Memory", "storage", "Storage", "hdd_ssd")
        storage_gb = int(_extract_number(str(sto_raw or ""), 256))
        # Handle TB
        if sto_raw and "tb" in str(sto_raw).lower():
            storage_gb = int(_extract_number(str(sto_raw), 1) * 1000)

        wt_raw    = g("Weight", "weight", "weight_kg")
        weight_kg = round(_extract_number(wt_raw, 2.0), 2)

        screen_raw = g("Inches", "screen_size", "display_size", "display_in")
        display_in = round(_extract_number(screen_raw, 15.6), 1)

        screen_res = str(g("ScreenResolution", "display_type", "resolution") or "")
        display_type = screen_res[:40] if screen_res else None

        os_raw = str(g("OpSys", "os", "operating_system") or "").strip()
        os     = os_raw if os_raw and os_raw.lower() not in ("nan", "none", "") else None

        # Estimate battery hours from weight proxy (heavier often = more battery)
        battery_hrs = round(max(3.0, 12.0 - weight_kg * 1.5), 1)

        if not name or price_inr == 0:
            continue

        rows.append({
            "name":         name,
            "brand":        brand or None,
            "price_inr":    price_inr,
            "cpu":          cpu,
            "gpu":          gpu,
            "ram_gb":       ram_gb,
            "storage_gb":   storage_gb,
            "battery_hrs":  battery_hrs,
            "weight_kg":    weight_kg,
            "display_in":   display_in,
            "display_type": display_type,
            "os":           os,
        })

    return rows


def seed(csv_path: str):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in backend/.env")
        sys.exit(1)

    print(f"Reading {csv_path} …")
    df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
    print(f"  {len(df)} rows loaded. Cleaning…")

    rows = clean_dataframe(df)
    print(f"  {len(rows)} valid laptops after cleaning.")

    if not rows:
        print("No valid rows found. Check column names in your CSV.")
        sys.exit(1)

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Clear existing data (optional — comment out to append)
    print("Clearing existing laptops table…")
    client.table("laptops").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    print(f"Inserting in batches of {BATCH_SIZE}…")
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        client.table("laptops").insert(batch).execute()
        print(f"  Inserted rows {i+1}–{min(i+BATCH_SIZE, len(rows))}")

    print(f"\nDone! {len(rows)} laptops seeded into Supabase.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed laptop CSV into Supabase")
    parser.add_argument("--file", required=True, help="Path to laptop CSV file")
    args = parser.parse_args()
    seed(args.file)
