from dataclasses import dataclass


@dataclass
class ColumnInfo:
    name: str
    col_type: str
    display_name: str
    data_type: str

    def __init__(self, name: str, col_type: str):
        self.name = name
        self.col_type = col_type
