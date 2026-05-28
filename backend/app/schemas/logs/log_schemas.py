from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class LogEntryBase(BaseModel):
    id: int
    operation: str
    changed_at: datetime
    row_data: Dict[str, Any]

class LogFilter(BaseModel):
    search: Optional[str] = None
    operation: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: Optional[str] = None

class LogSettingsBase(BaseModel):
    id: int
    table_name: str
    time_retention_minutes: int
    count_retention_limit: int

class LogSettingsUpdate(BaseModel):
    time_retention_minutes: Optional[int] = None
    count_retention_limit: Optional[int] = None