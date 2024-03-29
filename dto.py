from pydantic import BaseModel
from typing import Optional


class SearchFilters(BaseModel):
    text: Optional[str] = None
    file_mask: Optional[str] = None
    size: Optional[dict] = None
    creation_time: Optional[dict] = None
