from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    query: str


class QueryIntent(BaseModel):
    budget_inr: int = Field(default=60000, ge=0)
    use_case: str = Field(default="general")
    priorities: List[str] = Field(default_factory=list)
    brand_pref: Optional[str] = None


class RecommendRequest(BaseModel):
    budget_inr: int = Field(default=60000, ge=0)
    use_case: str = Field(default="general")
    priorities: List[str] = Field(default_factory=list)
    brand_pref: Optional[str] = None
    limit: int = Field(default=3, ge=1, le=5)


class ExplainRequest(BaseModel):
    laptops: list
    user_query: str
    intent: dict


class HistorySaveRequest(BaseModel):
    query_text: str
    intent: dict
    recommendations: list


class AuthRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
