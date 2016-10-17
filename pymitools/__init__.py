"""
a package of utilities for general image phenotyping tasks
"""

import os
version = {}
with open(os.path.join(os.path.dirname(__file__),"version.py")) as f0:
    exec(f0.read(), version)

__version__ = version['__version__']
