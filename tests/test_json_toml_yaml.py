import pytest

from tests.paths import DIR_WITH_TEST_FILES
from tinybear.exceptions import ParsingError
from tinybear.json_toml_yaml import (
    check_yaml_file,
    read_json_toml_yaml,
)


def test_check_yaml_file_passes_with_valid_data():
    for file in DIR_WITH_TEST_FILES.glob("yaml_OK*.yaml"):
        # no assert needed because exception will be thrown if something is wrong
        check_yaml_file(file)


def test_check_yaml_file_fails_with_invalid_data():
    for file in DIR_WITH_TEST_FILES.glob("yaml_bad*.yaml"):
        with pytest.raises(ParsingError) as e:
            check_yaml_file(file)

        print("TEST: error message received - ", e)


def test_read_json_toml_yaml():
    for file_name in (
        "json_OK_language_names_to_new_ids.json",
        "socio_aromanian_gold_standard.yaml",
        "toml_OK_simple.toml",
    ):
        file_path = DIR_WITH_TEST_FILES / file_name
        data = read_json_toml_yaml(file_path)
        assert isinstance(data, (dict, list))

        if file_name.endswith(".toml"):  # For TOML, check specific structure
            assert "section1" in data
            assert data["section1"]["key1"] == "value1"

    for file in DIR_WITH_TEST_FILES.glob("yaml_OK*.yaml"):
        print(f"TEST: file {file}")
        assert isinstance(read_json_toml_yaml(file), (dict, list))


def test_read_json_toml_yaml_raises_file_not_found_for_nonexistent_file(tmp_path):
    non_existent_file = tmp_path / "nonexistent_file.json"
    with pytest.raises(FileNotFoundError, match=str(non_existent_file)):
        read_json_toml_yaml(non_existent_file)


def test_read_json_toml_yaml_raises_exception_with_unsupported_file_type():
    for file_name in (
        "test_convert_excel_to_csv_gold_standard.csv",
        "read_plain_text_utf8.txt",
    ):
        with pytest.raises(TypeError):
            read_json_toml_yaml(DIR_WITH_TEST_FILES / file_name)


def test_read_json_toml_yaml_raises_exception_with_bad_yaml():
    for file in DIR_WITH_TEST_FILES.glob("yaml_bad*.yaml"):
        print(f"TEST: file {file}")
        with pytest.raises(ParsingError):
            read_json_toml_yaml(file)


def test_read_json_toml_yaml_raises_parser_error_for_malformed_toml():
    """Test that malformed TOML files raise ParsingError."""
    with pytest.raises(ParsingError, match="malformed data"):
        read_json_toml_yaml(DIR_WITH_TEST_FILES / "toml_bad_syntax.toml")


def test_read_json_toml_yaml_raises_parser_error_for_empty_toml():
    """Test that empty TOML files raise ParsingError."""

    for empty_file in ("json_empty.json", "toml_empty.toml", "yaml_empty.yaml"):
        with pytest.raises(ParsingError, match="malformed data"):
            read_json_toml_yaml(DIR_WITH_TEST_FILES / empty_file)
