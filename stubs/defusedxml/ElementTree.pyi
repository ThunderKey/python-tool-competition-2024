from pathlib import Path
from xml.etree.ElementTree import ElementTree

def parse(source: str | Path) -> ElementTree: ...
