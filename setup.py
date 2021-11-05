# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

current_path = os.path.abspath(os.path.dirname(__file__))

requirements = ("numpy", "matplotlib", "scikit-image", "progressbar2")

dev_requirements = ("pytest", "pytest-runner")

doc_requirements = (
    "sphinx",
    "sphinx_rtd_theme",
    "recommonmark",
    "sphinx-autodoc-typehints",
)


setup(
    name="tracklib",
    version="1.0.0",
    description="Python module providing the main objects to manipulate GPS traces with a variety of tools, operators and functions to perform spatial analysis using these objects",
    long_description="See https://github.com/umrlastig/tracklib",
    url="https://github.com/umrlastig/tracklib",
    author="Yann Méneroux, Marie-Dominique Van Damme",
    author_email="todo@ign.fr",
    license="cecill-c",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(include=["test", "resources"]),
    install_requires=requirements,
    test_suite="tests",
    extras_require={"dev": dev_requirements, "doc": doc_requirements},
)
