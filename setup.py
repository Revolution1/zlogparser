from setuptools import setup, find_packages

setup(
    name="zlogparser",
    version="1.0",
    keywords=tuple(),
    description="Zilliqa log parser",
    long_description="",
    license="MIT Licence",

    url="",
    author="revol",
    author_email="revol.cai@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[],
    scripts=[],
    entry_points={
        'console_scripts': [
            'zlogparser = zlogparser.main:main'
        ]
    }
)
