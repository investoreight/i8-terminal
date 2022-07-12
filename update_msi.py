import codecs
import os
from typing import Any, Dict, Optional

import requests
import wget


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


def is_latest_version(latest_version: str) -> Any:
    if latest_version:
        app_version = get_version()
        return app_version == latest_version
    return None


def get_latest_release_metadata() -> Optional[Dict[str, Any]]:
    resp = requests.get("https://api.github.com/repos/investoreight/i8-terminal/releases/latest")
    if resp.status_code != 200:
        print("No new release found.")
        return None
    msi_url = None
    release_metadata = resp.json()
    if release_metadata.get("assets"):
        msi_url = release_metadata.get("assets")[0].get("browser_download_url")

    return {"version": release_metadata["tag_name"][1:], "msi_url": msi_url}


def run_update() -> Any:
    release_metadata = get_latest_release_metadata()
    if not release_metadata:
        return None
    if not is_latest_version(latest_version=release_metadata["version"]):
        if not release_metadata["msi_url"]:
            print("Error while finding latest release!")
            return
        local_file = f"i8-terminal-{release_metadata['version']}-win64.msi"
        try:
            downloaded_msi = wget.download(release_metadata["msi_url"], local_file)
            if downloaded_msi:
                os.system(local_file)  # Open downloaded MSI
        except:
            print("No new release found.")
    else:
        print("Latest version of i8-terminal is already installed.")


if __name__ == "__main__":
    run_update()
