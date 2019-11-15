#!/usr/bin/env python

from setuptools import setup

setup(
    name="techrec",
    version="1.2.0",
    description="A Python2 web application "
    "that assist radio speakers in recording their shows",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="boyska",
    author_email="piuttosto@logorroici.org",
    packages=["techrec"],
    package_dir={"techrec": "server"},
    install_requires=["Paste~=3.2", "SQLAlchemy==0.8.3", "bottle~=0.12"],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={"console_scripts": ["techrec = techrec.cli:main"]},
    zip_safe=False,
    install_package_data=True,
    package_data={"techrec": ["static/**/*", "pages/*.html"]},
    test_suite="nose.collector",
    setup_requires=["nose>=1.0"],
    tests_requires=["nose>=1.0"],
)
