from pydantic import BaseModel, Field
from typing import Optional


class Laptop(BaseModel):
    id: Optional[str] = None
    name: str
    brand: Optional[str] = None
    price_inr: Optional[int] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    battery_wh: Optional[int] = None
    battery_hrs: Optional[float] = None
    weight_kg: Optional[float] = None
    display_in: Optional[float] = None
    display_type: Optional[str] = None
    os: Optional[str] = None
    source_url: Optional[str] = None


class ScoredLaptop(Laptop):
    total_score: float = 0.0
    performance_score: float = 0.0
    battery_score: float = 0.0
    gaming_score: float = 0.0
    value_score: float = 0.0
