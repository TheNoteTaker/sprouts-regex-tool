from setuptools import setup, find_packages

setup(
    name='sprouts',
    version='0.1',
    description='A utility package for various tasks.',
    author="Austin Kaufman",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    entry_points={
            'console_scripts': [
                'sprouts=sprouts.main:main',
            ],
        },
)
