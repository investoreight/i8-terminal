from typing import List

from setuptools import find_packages, setup

from i8_terminal.utils import get_version

PACKAGE_NAME = "i8_terminal"


def get_long_description() -> str:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    return long_description


def get_requirements() -> List[str]:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = fh.read()
    return requirements.strip().split("\n")


COMMON_ARGS = dict(
    name="i8-terminal",
    version=get_version(),
    author="investoreight",
    author_email="info@investoreight.com",
    license="LICENSE.txt",
    description="Investor8 CLI",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
)


setup(
    **COMMON_ARGS,
    packages=find_packages(),
    package_dir={PACKAGE_NAME: PACKAGE_NAME, "": PACKAGE_NAME},
    install_requires=get_requirements(),
    entry_points={"console_scripts": [f"i8={PACKAGE_NAME}.main:main"]},
    include_package_data=True,
)
