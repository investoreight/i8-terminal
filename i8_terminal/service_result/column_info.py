from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ColumnInfo:
    name: str
    col_type: str
    display_name: Optional[str] = None
    data_type: Optional[str] = None
    unit: Optional[str] = None
    colorable: Optional[bool] = None

    def enrich(self, other: ColumnInfo) -> None:
        if not self.display_name:
            self.display_name = other.display_name
        if not self.data_type:
            self.data_type = other.data_type
        if not self.unit:
            self.unit = other.unit
        if not self.colorable:
            self.colorable = other.colorable
