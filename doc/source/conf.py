# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

#sys.path.insert(0, os.path.abspath("../.."))
#sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../.."))
sys.path.append(os.path.abspath("../../tracklib"))
#print (sys.path)

# -- Project information -----------------------------------------------------

project = "TrackLib"
copyright = (
    "2022, LASTIG lab, French National Institute of Geographic and Forest Information"
)
author = "Yann Méneroux, Marie-Dominique Van Damme"

# The full version, including alpha/beta/rc tags
release = "1.0"


# -- General configuration ---------------------------------------------------

mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS-MML_HTMLorMML'
mathjax3_config = {
    'tex': {'tags': 'ams', 'useLabelIds': True},
}

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "recommonmark",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
	"nbsphinx",
    "autodocsumm",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx.ext.mathjax"
]





# I execute the notebooks manually in advance. If notebooks test the code,
# they should be run at build time.
#nbsphinx_execute = 'never'
#nbsphinx_allow_errors = True

# Add type of source files
# '.ipynb'
source_suffix = ['.rst', '.md']


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "public", "_static", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
#html_theme = "pydata_sphinx_theme"

#html_static_path = ['_static']
html_logo = "_static/TracklibLogo.png"




# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

autodoc_default_options = {
    "member-order": "bysource",
    "special-members": "__init__, __str__",
    "undoc-members": True,
    "private-members": True,
}


autodoc_mock_imports = []
