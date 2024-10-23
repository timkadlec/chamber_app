# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
project = 'HAMU Chamber App'
copyright = '2024, Tim Kadlec'
author = 'Tim Kadlec'
release = 'beta'

# -- General configuration ---------------------------------------------------
import os
import sys

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']

# Add the path to your Flask app module
sys.path.insert(0, os.path.abspath('../'))

extensions = [
    'sphinx.ext.autodoc',  # Automatically document your code
    'sphinx.ext.viewcode',  # Include links to the source code in the documentation
    'sphinx.ext.napoleon',  # Support for Google-style and NumPy-style docstrings
]

templates_path = ['_templates']
exclude_patterns = []

language = 'cs'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

# Additional configurations
html_title = 'HAMU Chamber App Documentation'  # Customize the HTML title
html_short_title = 'Chamber App'  # Short title for the navigation
html_theme_options = {
    'description': 'Documentation for the HAMU Chamber App',
    'sidebar_collapse': True,
    'sidebar_includehidden': True,
}
