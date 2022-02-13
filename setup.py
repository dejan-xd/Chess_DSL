from setuptools import find_packages, setup

PACKAGE_NAME = "ChessDSL"
VERSION = "2.0"
AUTHOR = "Novica Nikolic, Jovan Popovic, Dejan Jovanovic"
AUTHOR_EMAIL = "nole0223@gmail.com, jovanpop92@gmail.com, dejan.jovanovic94@gmail.com"
DESCRIPTION = "DSL for playing chess game"
KEYWORDS = "textX DSL python domain specific languages workflow"
LICENSE = "MIT"
URL = "https://github.com/dejan-xd/Chess_DSL"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["*.tx", "*.wav", "*.png", "*.json"]},
    python_requires=">=3.7",
    install_requires=[
        "setuptools==41.2.0",
        "pygame==2.0.1",
        "pygame-widgets==0.6.1",
        "future==0.18.2",
        "textX==2.3.0",
        "textx-ls-core==0.1.1",
        "termcolor==1.1.0"
    ],
    entry_points={"textx_languages": ["chess = textX:chess"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Games/Entertainment :: Board Games",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7"
    ]
)
