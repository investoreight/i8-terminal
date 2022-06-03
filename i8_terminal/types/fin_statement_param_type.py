from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_statements() -> List[Tuple[str, str]]:
    return [
        ("income", "Income Statment"),
        ("cash_flow", "Cash Flow Statment"),
        ("balance_sheet", "Balance Sheet Statment"),
    ]


class FinancialStatementParamType(AutoCompleteChoice):
    name = "financialstatement"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_statements())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "FINANCIALSTATEMENT"
