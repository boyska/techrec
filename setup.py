#!/usr/bin/env python

from setuptools import setup

requires = [
    line.strip()
    for line in open("server/requirements.txt").read().split("\n")
    if line.strip()
]
setup(
    name="techrec",
    version="1.1",
    description="A Python2 web application "
    "that assist radio speakers in recording their shows",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="boyska",
    author_email="piuttosto@logorroici.org",
    packages=["techrec"],
    package_dir={"techrec": "server"},
    install_requires=requires,
    entry_points={
        "console_scripts": [
            "techrec = techrec.cli:main",
        ]
    },
)
