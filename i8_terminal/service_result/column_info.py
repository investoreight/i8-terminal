from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ColumnInfo:
    name: str
    col_type: str
    display_name: Optional[str]
    data_type: Optional[str]
    unit: Optional[str]
    colorable: Optional[bool]

    def __init__(
        self,
        name: str,
        col_type: str,
        display_name: Optional[str] = None,
        data_type: Optional[str] = None,
        unit: Optional[str] = None,
        colorable: Optional[bool] = None,
    ):
        self.name = name
        self.col_type = col_type
        self.display_name = display_name
        self.data_type = data_type
        self.unit = unit
        self.colorable = colorable

    def enrich(self, other: ColumnInfo) -> None:
        if not self.display_name:
            self.display_name = other.display_name
        if not self.data_type:
            self.data_type = other.data_type
        if not self.unit:
            self.unit = other.unit
        if not self.colorable:
            self.colorable = other.colorable
