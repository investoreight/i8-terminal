from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ColumnInfo:
    name: str
    col_type: str
    display_name: str
    data_type: str
    unit: str

    def __init__(self, name: str, col_type: str, display_name: str = None, data_type: str = None, unit: str = None):
        self.name = name
        self.col_type = col_type
        self.display_name = display_name
        self.data_type = data_type
        self.unit = unit

    def enrich(self, other: ColumnInfo):
        if not self.display_name:
            self.display_name = other.display_name
        if not self.data_type:
            self.data_type = other.data_type
        if not self.unit:
            self.unit = other.unit
