__author__ = 'gbalaraman'

import sys
from setuptools import setup, find_packages
from pip.req import parse_requirements


install_reqs = parse_requirements("Requirements.txt")

setup(
    name='FinLib',
    version='0.1',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[str(ir.req) for ir in install_reqs],
    author="Gouthaman Balaraman"
)