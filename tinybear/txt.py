import logging
import re
from pathlib import Path
from typing import Literal, Union


def check_encoding_of_file(file: Path) -> str:
    """In this project text files can only be in utf-8 (newer ones)
    or ANSI (older ones). This function checks only these two
    alternatives.
    """
    encoding = "utf-8-sig"
    try:
        with file.open(encoding="utf-8") as fh:
            fh.read()
    except UnicodeDecodeError:
        with file.open(encoding="cp1251") as fh:
            fh.read()
            encoding = "cp1251"

    return encoding


def read_non_empty_lines_from_txt_file(path_to_file: Path) -> list[str]:
    """Creates list of lines from TXT file.  Checks for existence of file and
    correct encoding.
    """
    if not path_to_file.exists():
        raise FileNotFoundError(f"Файл {path_to_file} не найден")

    encoding = check_encoding_of_file(path_to_file)

    with path_to_file.open(encoding=encoding) as fh:
        return [line.strip() for line in fh if line.strip()]


def read_plain_text_from_file(path_to_file: Path) -> str:
    try:
        with path_to_file.open(encoding="utf-8-sig") as fh:
            content = fh.read()
    except UnicodeDecodeError:
        logging.info(f"Note: file {path_to_file.name} has ANSI encoding")
        with path_to_file.open(encoding="cp1251") as fh:
            content = fh.read()

    return content


def remove_extra_space(str_: str) -> str:
    """Removes leading and trailing space,
    replaces multiple spaces within string with one.
    """
    return re.sub(r"\s+", " ", str_.strip())


def write_plain_text_to_file(
    content: Union[str, list[str], tuple[str]],
    file: Path,
    overwrite: bool,
    newline_char: str = "\n",
) -> None:
    """Writes plain text to text file in UTF-8. If content is a list or a tuple,
    adds newline character at the end of each line automatically.
    """
    if not overwrite and file.exists():
        raise FileExistsError(f"File {file} already exists")

    if not isinstance(content, (str, list, tuple)):
        raise TypeError(f"Content of type {type(content)} not supported")

    with file.open(mode="w+", encoding="utf-8") as fh:
        if isinstance(content, str):
            fh.write(content)
            msg = "characters"
        elif isinstance(content, (list, tuple)):
            fh.writelines(f"{line}{newline_char}" for line in content)
            msg = "lines"

        logging.info(f"Written {len(content)} {msg} into file {file}.")


def move_line(
    file: Path,
    line_number_to_cut: int,
    line_number_to_insert_before: Union[int, Literal["END"]],
    output_file: Union[Path, None] = None,
) -> None:
    """Cut one line and insert it before the other."""

    with file.open(encoding="utf-8") as fh:
        lines = fh.readlines()

        if isinstance(line_number_to_insert_before, str) and line_number_to_insert_before in (
            "end",
            "END",
        ):
            line_number_to_insert_before = len(lines)
        elif not isinstance(line_number_to_insert_before, int):
            raise TypeError(
                f"{line_number_to_insert_before} is not an accepted argument. "
                'Please pass an integer or the string "END".'
            )

        lines.insert(
            line_number_to_insert_before,
            lines[line_number_to_cut],
        )

        if line_number_to_insert_before > line_number_to_cut:
            lines.pop(line_number_to_cut)
        else:
            lines.pop(line_number_to_cut + 1)

    file_to_write = output_file or file

    with file_to_write.open(mode="w+", encoding="utf8") as fh:
        fh.writelines(lines)
