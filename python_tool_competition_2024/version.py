"""Caluclates the version number of this package."""


import importlib.metadata
from typing import Final

VERSION: Final = importlib.metadata.version(__package__)
