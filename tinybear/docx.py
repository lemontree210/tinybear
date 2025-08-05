import logging
from pathlib import Path

import mammoth

from tinybear._paths import DEFAULT_OUTPUT_DIR, DEFAULT_INPUT_DIR

logging.basicConfig(level=logging.INFO)

STYLE_MAP = """
b => strong
i => em
p[style-name='Title'] => h1
p[style-name='Heading1'] => h2
p[style-name='Heading2'] => h2
p[style-name='Heading3'] => h3
p[style-name='Heading4'] => h4
r[style-name='Code'] => code
"""


def convert_one_to_html(path_to_file: Path, output_dir: Path = DEFAULT_OUTPUT_DIR, print_html: bool = True) -> Path:

    with path_to_file.open(mode="rb") as docx_file:
        result = mammoth.convert_to_html(docx_file, style_map=STYLE_MAP)
        html = result.value

    output_path = output_dir / f"{path_to_file.stem}.html"

    if print_html:
        logging.info(html)

    with output_path.open(mode="w+", encoding="utf-8") as output_file:
        output_file.write(html)

    return output_path


def convert_all(input_dir: Path = DEFAULT_INPUT_DIR, output_dir: Path = DEFAULT_OUTPUT_DIR, print_html: bool = True) -> None:
    for file in input_dir.glob("*.doc*"):
        logging.info(f"Converting {file.name}")
        convert_one_to_html(path_to_file=file, output_dir=output_dir, print_html=print_html)


if __name__ == '__main__':
    convert_all()
