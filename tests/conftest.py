"""Shared pytest configuration for the UPI Risk project.

Adds the repository root to ``sys.path`` so that top-level packages
``src`` and ``api`` can be imported regardless of how pytest resolves
rootdir.
"""

import os
import sys

# tests/conftest.py -> repository root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
