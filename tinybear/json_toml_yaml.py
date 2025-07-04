import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any, Union

# stubs exist but somehow mypy doesn't see them even after installation
import toml  # type: ignore
import yaml  # type: ignore
from yaml.parser import ParserError as YamlParserError  # type: ignore

from tinybear.exceptions import ParsingError

YAML_INDENT = " " * 2


def check_yaml_file(path_to_file: Path, verbose: bool = True) -> None:
    """Checks YAML file and throws exception if some problem occurs while
    reading YAML data.
    """
    if verbose:
        logging.info(f"Checking {path_to_file.name}")

    with path_to_file.open(encoding="utf-8") as yaml_file:
        data = yaml_file.read()

    # YAML parser does not catch duplicate dict keys, it keeps the value of the last key
    # it sees. For my purposes, a check of only top-level keys will be enough:
    # an optional hyphen, a colon after the key.
    # The key can be anything but a space or hyphen (to avoid catching lower-level keys)
    pattern_for_top_level_dict_keys = re.compile(r"^(- )?(?P<key>[^\s-]+)\s?:.*")

    top_level_dict_keys = [
        pattern_for_top_level_dict_keys.match(line).group("key")  # type: ignore
        for line in data.splitlines()
        if pattern_for_top_level_dict_keys.match(line) is not None
    ]

    counter = Counter(top_level_dict_keys)
    for key in counter:
        if counter[key] > 1:
            raise ParsingError(
                f"File {path_to_file} contains more than one dictionary key <{key}> at"
                " the top level"
            )

    try:
        yaml_loaded = yaml.load(data, Loader=yaml.Loader)
    except YamlParserError as e:
        logging.info(
            e
        )  # make sure it's printed nicely and shows user where the problem in file is
        raise ParsingError(f"Error reading YAML from file {path_to_file}")

    if not isinstance(yaml_loaded, (list, dict)):
        raise ParsingError(f"Could not read file {path_to_file} because of malformed data")

    if verbose:
        logging.info(f"TEST: YAML DATA {yaml_loaded}")


def read_json_toml_yaml(path_to_file: Path) -> Union[dict[str, Any], list[str]]:
    if not path_to_file.exists():
        raise FileNotFoundError(
            f"Cannot read JSON, TOML or YAML from non-existent file {path_to_file}"
        )

    extension = path_to_file.suffix.replace(".", "")

    error_msg = f"Could not read file {path_to_file} because of malformed data"

    with path_to_file.open(encoding="utf-8") as fh:
        content = fh.read()

    if extension == "json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise ParsingError(error_msg)
    elif extension == "toml":
        try:
            data = toml.loads(content)
        except toml.TomlDecodeError:
            raise ParsingError(error_msg)
    elif extension == "yaml":
        check_yaml_file(path_to_file=path_to_file)  # error will be raised there in case of error
        data = yaml.load(content, Loader=yaml.Loader)
    else:
        raise TypeError(f"File {path_to_file.name} cannot be converted")

    if not isinstance(data, (dict, list)) or not data:
        raise ParsingError(error_msg)

    return data
