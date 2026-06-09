from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProductSelection(BaseModel):
    selection_type: str = "all"
    mode: str = "include"
    product_ids: List[int] = []
    category_ids: List[int] = []
    brand_ids: List[int] = []


class RecalculationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    recalculation_type: int
    priority: int = 0
    is_active: bool = True
    trigger_type: str = "manual"
    trigger_config: Optional[Dict[str, Any]] = None
    parameters: Dict[str, Any] = {}
    product_selection: Optional[ProductSelection] = None


class RecalculationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    recalculation_type: Optional[int] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    product_selection: Optional[ProductSelection] = None


class RecalculationRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    recalculation_type: int
    priority: int
    is_active: bool
    trigger_type: str
    trigger_config: Optional[Dict[str, Any]] = None
    parameters: Dict[str, Any]
    product_selection: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecalculationSearchRequest(BaseModel):
    search: Optional[str] = None
    recalculation_type: Optional[int] = None
    trigger_type: Optional[str] = None
    is_active: Optional[bool] = None
    sort_by: Optional[str] = None
    page: int = 1
    page_size: int = 100
