#!/usr/bin/env python3

from setuptools import find_packages, setup

import codecs
import os.path

long_description = codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r', 'utf-8').read()

DISTUTILS_DEBUG = True

packages = find_packages(exclude=['build', 'build.*'])

setup(author='David Radford',
      author_email='croxis@gmail.com',
      name='MTG AI Card Builder',
      version='0.1',
      description='Creates Magic the Gathering cards from a nural network',
      keywords="chat",
      url='https://bitbucket.org/croxis/glitch',
      license="BSD",
      packages=packages,
      include_package_data=True,
      long_description=long_description,
      zip_safe=False,
      )
