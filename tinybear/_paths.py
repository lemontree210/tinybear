from pathlib import Path

DEFAULT_INPUT_DIR = Path('..') / 'input'

DEFAULT_OUTPUT_DIR = Path('..') / 'output'
if not DEFAULT_OUTPUT_DIR.exists():
    DEFAULT_OUTPUT_DIR.mkdir()
