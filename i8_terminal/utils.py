import codecs
import os
from typing import Any, Callable, Dict, List, TypeVar

from rich.console import Console

T = TypeVar("T")


def read(rel_path: str) -> str:
    """
    Read a file.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version() -> Any:
    """
    Read version from a file.
    """
    for line in read("version.txt").splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def find_dicts_diff(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for k in dict1:
        if k in dict2:
            if type(dict1[k]) is dict:
                res = find_dicts_diff(dict1[k], dict2[k])
                if res:
                    result[k] = res
            if dict1[k] != dict2[k]:
                result[k] = dict1[k]
        else:
            result[k] = dict1[k]
    for k in dict2:
        if k not in dict1:
            result[k] = dict2[k]
    return result


def concat_and(items: List[str]) -> str:
    return " and ".join(", ".join(items).rsplit(", ", 1))


def status(text: str = "Fetching data...", spinner: str = "material") -> Callable[..., Callable[..., T]]:
    def decorate(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            console = Console()
            with console.status(text, spinner=spinner):
                return func(*args, **kwargs)

        return wrapper

    return decorate