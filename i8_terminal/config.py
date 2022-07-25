import logging
import os
import shutil
import sys
import uuid
from typing import Any, Dict

import yaml
from mergedeep import merge
from rich.style import Style

from i8_terminal.i8_exception import I8Exception
from i8_terminal.utils import find_dicts_diff

PACKAGE_PATH = os.path.dirname(__file__)
EXECUTABLE_APP_DIR = os.path.join(os.path.dirname(sys.executable))
OS_HOME_PATH = os.path.expanduser("~")
SETTINGS_FOLDER = os.path.join(OS_HOME_PATH, ".i8_terminal")
USER_SETTINGS_PATH = os.path.join(SETTINGS_FOLDER, "user.yml")
APP_SETTINGS_PATH = os.path.join(SETTINGS_FOLDER, "config.yml")
ASSETS_PATH = os.path.join(PACKAGE_PATH, "assets")
I8_TERMINAL_LOGO_URL = "https://www.investoreight.com/media/i8t-chart-logo.png"


def init_settings() -> None:
    if not os.path.exists(SETTINGS_FOLDER):
        try:
            os.mkdir(SETTINGS_FOLDER)
        except:
            logging.error(
                f"Cannot initialize app. Application needs write access to create app directory in the following path: '{OS_HOME_PATH}'"
            )

    if not os.path.exists(USER_SETTINGS_PATH):
        try:
            user_setting = {"app_instance_id": uuid.uuid4().hex}
            with open(USER_SETTINGS_PATH, "w") as f:
                yaml.dump(user_setting, f)
        except:
            logging.error(
                f"Cannot initalize user settings. Make sure you have write access to the path: '{USER_SETTINGS_PATH}'"
            )

    if not os.path.exists(APP_SETTINGS_PATH):
        try:
            app_settings_src_path = os.path.join(PACKAGE_PATH, "config.yml")
            if os.path.exists(app_settings_src_path):
                shutil.copyfile(app_settings_src_path, APP_SETTINGS_PATH)
            else:
                shutil.copyfile(f"{EXECUTABLE_APP_DIR}/config.yml", APP_SETTINGS_PATH)
        except Exception as e:
            logging.error(
                f"Cannot initalize app settings. Make sure you have write access to the path: '{APP_SETTINGS_PATH}'\n {e}"
            )


def load_user_settings() -> Any:
    if not os.path.exists(USER_SETTINGS_PATH):
        return {}
    with open(USER_SETTINGS_PATH, "r") as f:
        return yaml.safe_load(f) or {}


def load_app_settings() -> Any:
    if not os.path.exists(APP_SETTINGS_PATH):
        return {}
    with open(APP_SETTINGS_PATH, "r") as f:
        return yaml.safe_load(f) or {}


def load_latest_app_settings() -> Any:
    app_settings_src_path = os.path.join(PACKAGE_PATH, "config.yml")
    with open(app_settings_src_path, "r") as f:
        return yaml.safe_load(f) or {}


def save_user_settings(data: Dict[str, Any]) -> None:
    current_user_settings = load_user_settings()
    new_user_settings = {**current_user_settings, **data}
    with open(USER_SETTINGS_PATH, "w") as f:
        yaml.dump(new_user_settings, f)


def delete_user_settings() -> None:
    file = open(USER_SETTINGS_PATH, "w")
    file.close()


def restore_user_settings() -> None:
    current_user_settings = load_user_settings()
    restored_user_setting = {"app_instance_id": current_user_settings.get("app_instance_id")}
    with open(USER_SETTINGS_PATH, "w") as f:
        yaml.dump(restored_user_setting, f)


def update_settings() -> None:
    current_app_settings = load_app_settings()
    latest_app_settings = load_latest_app_settings()
    app_new_settings = find_dicts_diff(latest_app_settings, current_app_settings)
    user_new_settings = find_dicts_diff(current_app_settings, latest_app_settings)
    if app_new_settings or user_new_settings:
        new_settings = merge({}, latest_app_settings, current_app_settings)
        with open(APP_SETTINGS_PATH, "w") as f:
            yaml.dump(new_settings, f)


def get_table_style(profile_name: str = "default") -> Dict[str, Any]:
    styles = APP_SETTINGS["styles"]["table"][profile_name]
    try:
        return {
            "header_style": Style(**styles["header"]),
            "row_styles": [Style(**styles["row"]), Style(**styles["alternate_row"])],
            "show_lines": styles.get("show_lines", False),
        }
    except:
        raise I8Exception(
            "Cannot parse table style settings from the configuration file! Check to see if the configuration file is formatted correctly!"
        )


def is_user_logged_in() -> bool:
    if not USER_SETTINGS.get("i8_core_api_key") or not USER_SETTINGS.get("i8_core_token"):
        return False
    return True


if "USER_SETTINGS" not in globals():
    init_settings()
    update_settings()
    USER_SETTINGS = load_user_settings()
    APP_SETTINGS = load_app_settings()

if not USER_SETTINGS.get("app_instance_id"):
    user_setting = {"app_instance_id": uuid.uuid4().hex}
    save_user_settings(user_setting)
