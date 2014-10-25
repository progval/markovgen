#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='markovgen',
    version='0.3',
    description='Another text generator based on Markov chains.',
    url='https://github.com/ProgVal/markovgen',
    author='Valentin Lorentz',
    author_email='progval@progval.net',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=[
        'markovgen',
    ],
    extras_require = {
        'encoding_guessing': ['chardet'], # Or charade
    },
)



