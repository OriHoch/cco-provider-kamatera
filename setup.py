from setuptools import setup, find_packages
from os import path
from time import time

here = path.abspath(path.dirname(__file__))

if path.exists("VERSION.txt"):
    # this file can be written by CI tools (e.g. Travis)
    with open("VERSION.txt") as version_file:
        version = version_file.read().strip().strip("v")
else:
    version = str(time())

setup(
    name='cco_provider_kamatera',
    version=version,
    description='''CKAN Cloud Operator provider for Kamatera''',
    url='https://github.com/OriHoch/cco-provider-kamatera',
    author='''Ori Hoch''',
    license='MIT',
    packages=find_packages(exclude=['examples', 'tests', '.tox']),
    install_requires=[
        'ckan_cloud_operator',
    ],
    entry_points={
      'console_scripts': [
        'cco-provider-kamatera = cco_provider_kamatera.cli:main',
      ]
    },
)
