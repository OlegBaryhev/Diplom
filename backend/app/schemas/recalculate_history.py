from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class RecalculateHistoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    recalculated_by: str
    recalculation_type: Optional[int] = None
    trigger_type: Optional[str] = None
    parameters: Dict[str, Any]
    products_affected_count: Optional[int] = None
    execution_time_ms: Optional[int] = None


class RecalculateHistoryRead(RecalculateHistoryCreate):
    id: int
    recalculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceRecalculationFilter(BaseModel):
    search: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sort_by: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None


class RelativePriceUpdateRequest(PriceRecalculationFilter):
    value: float
    type: str
    name: str
    description: Optional[str] = None
    recalculated_by: Optional[str] = None


class FixedPriceUpdateRequest(PriceRecalculationFilter):
    value: int
    name: str
    description: Optional[str] = None
    recalculated_by: Optional[str] = None


class AverageRelativePriceUpdateRequest(PriceRecalculationFilter):
    value: float
    type: str
    offset: bool
    name: str
    description: Optional[str] = None
    recalculated_by: Optional[str] = None
