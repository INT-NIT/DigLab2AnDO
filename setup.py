#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from setuptools import setup, find_packages
import os

# Extract central version information
with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    version = version_file.read().strip()


setup(
    name="DigLab2Tools",
    version=version,
    packages=find_packages(),

    author="Julia Sprenger, Jeremy Garcia",
    description="diglab2bids is a tool that allows automatically creating a directory where data and metadata from a "
                "neuroscientific experiment are stored, and that follows the DigLab "
                "specifications (https://github.com/INT-NIT/DigLabTools/), using as input a filled pdf form or a redcap "
                "survey/form",
    license='MIT',
    install_requires=[],
    include_package_data=True,
    python_requires='>=3.6',
    extras_require={
        'test': ['pytest']
    }
)
