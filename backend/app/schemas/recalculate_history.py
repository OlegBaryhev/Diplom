from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from typing import Optional, Literal

class RecalculateHistoryCreate(BaseModel):
    name: str
    description: Optional[str]
    recalculated_by: str
    parameters: Dict[str, Any]

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
    type: Literal["rubles", "percent"]
    name: str
    description: Optional[str]
    recalculated_by: str

class FixedPriceUpdateRequest(PriceRecalculationFilter):
    value: int
    name: str
    description: Optional[str]
    recalculated_by: str

class AverageRelativePriceUpdateRequest(PriceRecalculationFilter):
    value: float
    type: Literal["rubles", "percent"]
    offset: bool
    name: str
    description: Optional[str]
    recalculated_by: str
