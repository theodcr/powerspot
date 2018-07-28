from setuptools import setup

setup(
    name='powerspot',
    version='0.1',
    py_modules=['powerspot'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        powerspot=main:main
    ''',
)
