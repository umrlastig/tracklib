# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

current_path = os.path.abspath(os.path.dirname(__file__))

requirements = (
        "numpy==1.23.5", 
        "matplotlib", 
        "scikit-image", 
        "progressbar2"
)

dev_requirements = (
        "numpy==1.23.5", 
        "pytest", 
        "pytest-runner", 
        "coverage"
)

doc_requirements = (
    "sphinx",
    "sphinx_rtd_theme",
    "recommonmark",
    "sphinx-autodoc-typehints",
	"nbsphinx",
	"ipykernel",
    "autodocsumm"
)

setup (
    name="tracklib",
    version="0.6",
    description="Tracklib library provide a variety of tools, operators and functions to manipulate GPS trajectories",
    long_description="See https://github.com/umrlastig/tracklib",
    url="https://github.com/umrlastig/tracklib",
    download_url= 'https://github.com/umrlastig/tracklib/archive/refs/tags/v0.6.0.tar.gz',
    author="Yann Méneroux, Marie-Dominique Van Damme",
    author_email="todo@ign.fr",
    keywords=['gps', 'track', 'python'],
    license="Cecill-C",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(include=["test", "resources"]),
    install_requires=requirements,
    test_suite="tests",
    extras_require={
            "dev": dev_requirements, 
            "doc": doc_requirements
    },
)
