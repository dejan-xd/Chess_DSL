from setuptools import find_packages, setup

PACKAGE_NAME = "ChessDSL"
VERSION = "1.0"
AUTHOR = "Novica Nikolic, Jovan Popovic, Dejan Jovanovic"
AUTHOR_EMAIL = "jovanpop92@gmail.com"
DESCRIPTION = "DSL for playing chess game"
KEYWORDS = "textX DSL python domain specific languages workflow"
LICENSE = "MIT"
URL = "https://github.com/dejan-xd/Chess_DSL"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["*.tx"]},
    install_requires=["textx_ls_core"],
    entry_points={"textx_languages": ["chess = textX:chess"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
