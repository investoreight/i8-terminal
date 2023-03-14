from typing import Any, Dict


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
