import codecs
import os
from typing import Any, Dict


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
    return result
