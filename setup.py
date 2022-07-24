# -*- coding: utf-8 -*-
"""
setup.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BatteryDataExtractor setup
author: Shu Huang (sh2009@cam.ac.uk)
"""
import os
from setuptools import setup, find_packages

with open('LICENSE', encoding='utf-8') as f:
    license = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    reqs = f.read()

if os.path.exists('README.md'):
    long_description = open('README.md').read()
else:
    long_description = '''BatteryDataExtractor is the first property-specific text-mining tool for auto-generating 
    databases of materials and their property, device, and associated characteristics. The software has been 
    constructed by embedding the BatteryBERT model.'''

setup(
    name='batterydataextractor',
    version='1.0.0',
    author='Shu Huang',
    author_email='sh2009@cam.ac.uk',
    license=license,
    url='https://github.com/ShuHuang/batterydataextractor',
    packages=find_packages(),
    description='BatteryDataExtractor: battery-aware text-mining software embedded with BERT models',
    long_description=long_description,
    keywords='bde ',
    zip_safe=False,
    install_requires=reqs.strip().split('\n'),
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Cheminformatics',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
)