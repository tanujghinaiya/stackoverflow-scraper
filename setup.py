from setuptools import setup

setup(
    name="soscrape",
    packages=["soscrape"],
    entry_points={
        "console_scripts": [
            "soscrape=soscrape.__main__:init_app"
        ]
    },
    install_requires=[
        "lxml",
        "requests",
        "beautifulsoup4"
    ]
)