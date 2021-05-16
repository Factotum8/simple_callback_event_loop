#!/usr/bin/env python3
# coding=utf-8
from setuptools import setup


setup(
    python_requires='~=3.9',

    install_requires=[
        # Production requirements (always need)
        'loguru>=0.5.3'
        ],

    # tests_require - New in 41.5.0: Deprecated the test command.
    extras_require={
        # test requirements
        'test': [
            "mock>=2.0.0",
            "coverage>=5.1"
        ]
    },
)
