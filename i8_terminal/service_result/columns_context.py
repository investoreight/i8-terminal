from typing import List

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.i8_exception import I8Exception
from i8_terminal.service_result.column_info import ColumnInfo


class ColumnsContext:
    def __init__(self, col_infos: List[ColumnInfo]):
        self._col_infos = col_infos
        self._enrich_col_infos()

    def _enrich_col_infos(self):
        all_metrics_dict = self.get_metrics_dict()

        for ci in self._col_infos:
            if ci.col_type == "metric":
                if ci.name not in all_metrics_dict:
                    raise I8Exception(
                        f"Metric `{ci.name}` is not a known metric! You need to explicitly define the metadata!"
                    )
                ci.enrich(all_metrics_dict[ci.name])
        return

    def get_metrics_dict(self):
        metrics_df = get_all_metrics_df()
        metrics_dict = {}
        for _, r in metrics_df.iterrows():
            metrics_df[r["metric_name"]] = ColumnInfo(
                r["metric_name"], "metric", r["display_name"], r["data_format"], r["unit"]
            )
        return metrics_dict

    def get_col_infos(self) -> List[ColumnInfo]:
        return self._col_infos
