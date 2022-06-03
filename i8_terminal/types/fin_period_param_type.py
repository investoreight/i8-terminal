from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_fin_periods() -> List[Tuple[str, str]]:
    all_periods = [("FY", "Anual")]
    for i in range(1, 5):
        all_periods.append((f"Q{i}", f"Fiscal Quarter {i}"))
        all_periods.append((f"Q{i}TTM", f"Trailing 12 Months Ending Q{i}"))
        all_periods.append((f"Q{i}YTD", f"Year to Date Ending Q{i}"))
    return all_periods


class FinancialsPeriodParamType(AutoCompleteChoice):
    name = "financialsperiod"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_fin_periods())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "FINANCIALSPERIOD"
