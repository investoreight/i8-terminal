from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_output_param_types() -> List[Tuple[str, str]]:
    return [("terminal", "Generate table"), ("plot", "Generate chart")]


class OutputParamType(AutoCompleteChoice):
    name = "outputtype"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_output_param_types())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "OUTPUTTYPE"
