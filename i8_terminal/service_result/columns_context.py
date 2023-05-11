from typing import Dict, List

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.i8_exception import I8Exception
from i8_terminal.service_result.column_info import ColumnInfo


class ColumnsContext:
    def __init__(self, col_infos: List[ColumnInfo]):
        self._col_infos = col_infos
        self._enrich_col_infos()
        self._col_info_dict = {ci.name: ci for ci in self._col_infos}

    def _enrich_col_infos(self) -> None:
        all_metrics_dict = self.get_metrics_dict()

        for ci in self._col_infos:
            if ci.col_type == "metric":
                if ci.name not in all_metrics_dict:
                    raise I8Exception(
                        f"Metric `{ci.name}` is not a known metric! You need to explicitly define the metadata!"
                    )
                ci.enrich(all_metrics_dict[ci.name])

    def get_metrics_dict(self) -> Dict[str, ColumnInfo]:
        metrics_df = get_all_metrics_df()
        metrics_dict: Dict[str, ColumnInfo] = {}
        for _, r in metrics_df.iterrows():
            metrics_dict[r["metric_name"]] = ColumnInfo(
                r["metric_name"], "metric", r["display_name"], r["data_format"], r["unit"]  # , r["colorable"]
            )
        return metrics_dict

    def get_col_infos(self) -> List[ColumnInfo]:
        return self._col_infos

    def get_col_info_dict(self) -> Dict[str, ColumnInfo]:
        return self._col_info_dict

    def get_col_info(self, name: str) -> ColumnInfo:
        if name not in self._col_info_dict:
            raise I8Exception(f"Column `{name}` is not found!")
        return self._col_info_dict[name]
