from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Poetry:
    """Poetry data structure."""
    lines: List[str]
    author: Optional[str] = None
    title: Optional[str] = None
    source: str = "curated"
    theme: Optional[str] = None
    created_at: Optional[datetime] = None 