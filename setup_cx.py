from cx_Freeze import Executable, setup
from setuptools import find_packages

from setup import COMMON_ARGS, PACKAGE_NAME

upgrade_code = "{5CA39ABE-9649-34E5-8DA3-138D74AE7E40}"
bdist_msi_options = {
    "add_to_path": True,
    "upgrade_code": upgrade_code,
}
build_exe_options = {
    "packages": find_packages(),
    "include_files": [
        f"{PACKAGE_NAME}/assets/favicon.ico",
        f"{PACKAGE_NAME}/config.yml",
        f"{PACKAGE_NAME}/version.txt",
    ],
    "excludes": ["mypy", "isort", "black", "pyflakes"],
}

setup(
    **COMMON_ARGS,
    executables=[
        Executable(
            f"{PACKAGE_NAME}/main.py", base=None, target_name="i8.exe", icon=f"{PACKAGE_NAME}/assets/favicon.ico"
        ),
        Executable(
            "update_msi.py",
            base=None,
            target_name="i8update.exe",
        ),
    ],
    options={"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
)
