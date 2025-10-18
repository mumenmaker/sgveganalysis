from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Restaurant(BaseModel):
    """Model for restaurant data from HappyCow"""
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_vegan: bool = False
    is_vegetarian: bool = False
    has_veg_options: bool = False
    features: List[str] = Field(default_factory=list)  # e.g., "outdoor seating", "delivery"
    hours: Optional[str] = None
    happycow_url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
