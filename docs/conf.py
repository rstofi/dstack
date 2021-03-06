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
import re
#sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('./..'))

add_module_names = False

# -- Project information -----------------------------------------------------

project = 'dstack'
copyright = '2020, Kristof Rozgonyi'
author = 'Kristof Rozgonyi'

def get_version():
    version_file = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),'../dstack/','__version__.py'))

    with open(version_file, "r") as f:
        lines = f.read()
        version = re.search(r"^_*version_* = ['\"]([^'\"]*)['\"]", lines, re.M).group(1)
        f.close()
        return version

dstack_version = get_version()

# The short X.Y version
version = dstack_version

# The full version, including alpha/beta/rc tags
release = dstack_version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages'
]
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']