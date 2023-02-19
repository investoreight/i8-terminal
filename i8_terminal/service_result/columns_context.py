from typing import List

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.service_result.column_info import ColumnInfo


class ColumnsContext:
    def __init__(self, col_infos: List[ColumnInfo]):
        self._col_infos = col_infos
        self._enrich_col_infos()

    def _enrich_col_infos(self):
        # Fetch metadata and enrich col info
        metrics_df = get_all_metrics_df()
        return

    def get_col_infos(self) -> List[ColumnInfo]:
        return self._col_infos

    def get_col_info(self) -> ColumnInfo:
        return None
