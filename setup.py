# -*- coding: utf-8 -*-
"""
setup.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BatteryDataExtractor setup
author: Shu Huang (sh2009@cam.ac.uk)
"""
from setuptools import setup, find_packages

with open('LICENSE', encoding='utf-8') as f:
    license = f.read()

setup(
    name='batterydataextractor',
    version='0.0.5',
    author='Shu Huang',
    author_email='sh2009@cam.ac.uk',
    license=license,
    url='https://github.com/ShuHuang/batterydataextractor',
    packages=find_packages(),
    description='BatteryDataExtractor: battery-aware text-mining software embedded with BERT models',
    long_description='''BatteryDataExtractor is the first property-specific text-mining tool for auto-generating 
    databases of materials and their property, device, and associated characteristics. The software has been 
    constructed by embedding the BatteryBERT model.''',
    keywords='bde',
    zip_safe=False,
    install_requires=[
        'selenium>=4.1.0',
        'requests>=2.27.1',
        'beautifulsoup4>=4.10.0',
        'numpy>=1.22.0',
        'torch>=1.11.0',
        'torchvision>=0.12.0',
        'torchaudio>=0.11.0',
        'transformers>1.18.0',
        'lxml>=4.7.1',
        'cssselect>=1.1.0',
        'appdirs>=1.4.4',
        'scispacy>=0.4.0',
        'spacy==3.0.7',
        'six'
    ],
    dependency_links=[
    'https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
)
