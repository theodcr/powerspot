import os
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='powerspot',
    version='0.1',
    description='CLI for automated operations with Spotify',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6.0',
    url='https://github.com/theolamayo/powerspot',
    py_modules=['powerspot'],
    entry_points='''
        [console_scripts]
        powerspot=main:main
    ''',
    install_requires=[
        'Click',
        'spotipy',
        'tabulate',
    ],
    licence='MIT',
)
