import codecs
import os
from typing import Any

import wget
from investor8_sdk import SettingsApi


def read(rel_path: str) -> str:
    """
    Read a file.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version() -> Any:
    """
    Read app version from a file.
    """
    file_path = "version.txt"
    if not os.path.exists(file_path):
        file_path = "i8_terminal/version.txt"
    for line in read(file_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def get_latest_version() -> Any:
    resp = None
    try:
        resp = SettingsApi().check_i8t_version(get_version())
    except:
        pass
    if resp:
        return resp.to_dict().get("latest_version")

    return resp


def is_latest_version() -> Any:
    latest_version = get_latest_version()
    if latest_version:
        app_version = get_version()
        return app_version == latest_version
    return None


if __name__ == "__main__":
    if not is_latest_version():
        msi_url = (
            f"https://www.investoreight.com/media/i8-terminal-{get_latest_version()}-win64.msi"  # get latest msi url
        )
        local_file = f"i8-terminal-{get_latest_version()}-win64.msi"
        try:
            downloaded_msi = wget.download(msi_url, local_file)
            if downloaded_msi:
                os.system(local_file)  # Open downloaded MSI
        except:
            print("No new release found.")
    else:
        print("Latest version of i8-terminal is already installed.")
