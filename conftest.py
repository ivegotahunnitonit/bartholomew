import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

pypi_dir = os.path.join(BASE_DIR, "pypi_package")
if pypi_dir not in sys.path:
    sys.path.insert(0, pypi_dir)
