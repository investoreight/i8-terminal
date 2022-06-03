from datetime import datetime
from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice
from i8_terminal.types.fin_period_param_type import FinancialsPeriodParamType
from i8_terminal.types.ticker_param_type import TickerParamType


class FinancialsIdentifierParamType(AutoCompleteChoice):
    name = "financials"

    def __init__(self) -> None:
        self._ticker_auto_comp = TickerParamType()
        self._period_auto_comp = FinancialsPeriodParamType()

    def get_suggestions(
        self, keyword: str, pre_populate: bool = False, param_type: str = None
    ) -> List[Tuple[str, str]]:
        if param_type == "ticker":
            return self._ticker_auto_comp.get_suggestions(keyword)
        elif param_type == "year":
            years = [(str(i), "") for i in range(datetime.now().year, 2008, -1)]
            if keyword.strip() == "":
                return years
            return [y for y in years if y[0].startswith(keyword)]
        else:
            return self._period_auto_comp.get_suggestions(keyword, True)

    def __repr__(self) -> str:
        return "FINANCIALS"
