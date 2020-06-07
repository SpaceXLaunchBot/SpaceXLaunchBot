from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


def read_local_file(f_name):
    with open(path.join(here, f_name), encoding="utf-8") as f:
        contents = f.read()
    # If on win, get rid of CR from CRLF
    return contents.replace("\r", "")


long_description = read_local_file("README.md")
requirements = read_local_file("requirements.txt").split("\n")

setup(
    name="SpaceXLaunchBot",
    version="0.0.1",
    description="A Discord bot for getting news, information, and notifications about upcoming SpaceX launches.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/r-spacex/SpaceXLaunchBot",
    packages=find_packages(exclude=["contrib", "docs", "tests", "examples"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": ["spacexlaunchbot = spacexlaunchbot.__main__:main"]
    },
)
