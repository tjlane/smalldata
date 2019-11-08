# -*- coding: utf8 -*-

import os
from setuptools import setup, find_packages


setup(
    name='smalldata',
    version='0.2',
    author='Lane, OGrady',
    author_email='thomas.joseph.lane@gmail.com',
    url='https://github.com/tjlane/smalldata',

    # Packages and depencies
    packages=['smalldata'],
    package_dir={'smalldata': 'smalldata'},
    install_requires=[
        'numpy',
    ],

    # Other configurations
    zip_safe=False,
    platforms='any',
)


