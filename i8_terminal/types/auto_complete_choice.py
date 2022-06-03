import heapq
from typing import List, Optional, Tuple

from click.types import StringParamType


class AutoCompleteChoice(StringParamType):
    name = "autocompletechoice"

    def __init__(self, choices: Optional[List[Tuple[str, str]]] = None) -> None:
        self.is_loaded = False
        self.size = 10
        if choices:
            self.set_choices(choices)

    def set_choices(self, choices: List[Tuple[str, str]]) -> None:
        if choices and len(choices) > 0:
            self._choices = choices
            self._choices_l = [(c[0].lower(), c[1].lower()) for c in choices]
            self.is_loaded = True
        else:
            self._choices = []
            self._choices_l = []

    def search_keyword(self, keyword: str) -> List[Tuple[str, str]]:
        keyword = keyword.lower()

        scores: List[Tuple[float, int]] = []
        for i, val in enumerate(self._choices_l):
            # A heurestic method to rank the list of choices
            score = 0.0
            for token in val[1].replace('"', "").split(" "):
                if token.startswith(keyword):
                    score += 1 + 1 / len(token)
            for token in val[0].replace('"', "").split("_"):
                if token.startswith(keyword):
                    score += 3 + 1 / len(val[0])
            if val[0].startswith(keyword):
                score += 5 + 1 / len(val[0])
            if val[0] == keyword:
                score += 10

            if score > 0:
                if len(scores) < self.size:
                    heapq.heappush(scores, (score, i))
                else:
                    heapq.heappushpop(scores, (score, i))

        scores_sorted = sorted(scores, key=lambda x: -x[0])
        return [self._choices[i[1]] for i in scores_sorted]

    def get_suggestions(self, keyword: str, pre_populate: bool = False) -> List[Tuple[str, str]]:
        if self._choices:
            if pre_populate and keyword.strip() == "":
                return self._choices[: self.size]
            return self.search_keyword(keyword)
        return []

    def __repr__(self) -> str:
        return "AUTOCOMPLETECHOICE"
