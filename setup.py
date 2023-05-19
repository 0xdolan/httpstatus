#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path

from setuptools import setup

myPath = path.abspath(path.dirname(__file__))
with open(path.join(myPath, "README.md"), encoding="utf-8") as rf:
    README = rf.read()

setup(
    name="httpstatus",
    version="1.0.0",
    author="Dolan",
    author_email="0xdolan@gmail.com",
    url="https://github.com/0xdolan/httpstatus",
    description=("http status helps you find out what the HTTP status code means."),
    long_description=README,
    long_description_content_type="text/markdown",
    license="GPL-3.0",
    keywords="http https status-code",
    packages=["httpstatus"],
    include_package_data=True,
    install_requires=[],
    classifiers=["Programming Language :: Python :: 3"],
)
