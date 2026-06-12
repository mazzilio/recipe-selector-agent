"""Data models for Gousto recipes."""

from typing import List, Optional

from pydantic import BaseModel


class Recipe(BaseModel):
    name: str
    cook_time_mins: Optional[int] = None
    calories: Optional[int] = None
    dietary_tags: List[str] = []   # e.g. ["GF", "DF", "V", "PB"]
    categories: List[str] = []     # e.g. ["10-Minute", "Calorie Controlled"]
    has_extra_cost: bool = False
    extra_cost_gbp: Optional[float] = None
    is_customisable: bool = False
