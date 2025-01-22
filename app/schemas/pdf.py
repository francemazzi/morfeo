from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class PDFExtractionBase(BaseModel):
    filename: str
    extracted_data: Dict[str, Any]

class PDFExtractionCreate(PDFExtractionBase):
    pass

class PDFExtraction(PDFExtractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 