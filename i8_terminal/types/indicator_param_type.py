from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_indicators() -> List[Tuple[str, str]]:
    return [
        ("ma5", "5 Days Moving Average"),
        ("ma12", "12 Days Moving Average"),
        ("ma26", "26 Days Moving Average"),
        ("ma52", "26 Days Moving Average"),
        ("ema5", "5 Days Exponential Moving Average"),
        ("ema12", "12 Days Exponential Moving Average"),
        ("ema26", "26 Days Exponential Moving Average"),
        ("ema52", "52 Days Exponential Moving Average"),
        ("rsi", "Relative strength index (14 Days)"),
        ("rsi_7d", "Relative strength index (7 Days)"),
        ("rsi_1m", "Relative strength index (1 Month)"),
        ("rsi_3m", "Relative strength index (3 Months)"),
        ("alpha", "Alpha (1 Year)"),
        ("alpha_1w", "Alpha (1 Week)"),
        ("alpha_2w", "Alpha (2 Weeks)"),
        ("alpha_1m", "Alpha (1 Months)"),
        ("alpha_3m", "Alpha (3 Months)"),
        ("alpha_6m", "Alpha (6 Months)"),
        ("alpha_2y", "Alpha (2 Years)"),
        ("alpha_5y", "Alpha (5 Years)"),
        ("beta", "Beta (1 Year)"),
        ("beta_1w", "Beta (1 Week)"),
        ("beta_2w", "Beta (2 Weeks)"),
        ("beta_1m", "Beta (1 Months)"),
        ("beta_3m", "Beta (3 Months)"),
        ("beta_6m", "Beta (6 Months)"),
        ("beta_2y", "Beta (2 Years)"),
        ("beta_5y", "Beta (5 Years)"),
        ("volume", "Volume"),
    ]


class IndicatorParamType(AutoCompleteChoice):
    name = "indicator"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_indicators())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "INDICATOR"
