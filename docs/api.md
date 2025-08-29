# API Reference

---

## tinybear.csv_xls

### append_empty_column_to_csv
```python
def append_empty_column_to_csv(path_to_file: Path, name_of_new_column: str, delimiter: CSVDelimiter = ",", custom_path_to_output_file: Optional[Path] = None) -> None:
```
Adds empty column (as last column) to CSV file. **Overwrites file**, but optional output path can be specified to create a new file.

Raises:
- ValueError if column name already exists in file.
- FileExistsError if custom output file is specified and already exists.

---

### check_csv_for_malformed_rows
```python
def check_csv_for_malformed_rows(path_to_file: Path) -> None:
```
Checks whether all rows in CSV file have the same number of columns. Throws IndexError if they do not.

---

### check_csv_for_repetitions_in_column
```python
def check_csv_for_repetitions_in_column(path_to_file: Path, column_name: str) -> None:
```
Throws ValueError if there are repetitions in given column of given file.

---

### convert_xls_to_csv
```python
def convert_xls_to_csv(path_to_input_excel_file: Path, sheet_name: str, path_to_output_csv_file: Path, delimiter: CSVDelimiter = ",", overwrite: bool = True) -> None:
```
Converts sheet from Excel file to CSV format.

---

### read_column_from_csv
```python
def read_column_from_csv(path_to_file: Path, column_name: str) -> list[str]:
```
Reads one column from CSV file. Column name is taken from the top row. Raises KeyError if no such column exists.

---

### read_dicts_from_csv
```python
def read_dicts_from_csv(path_to_file: Path, delimiter: CSVDelimiter = ",") -> list[dict[str, str]]:
```
Reads CSV as list of dictionaries (top row is considered key).

---

### read_dict_from_2_csv_columns
```python
def read_dict_from_2_csv_columns(path_to_file: Path, key_col: str, val_col: str, delimiter: CSVDelimiter = ",") -> dict[str, str]:
```
Reads CSV and returns dict mapping keys from key_col to values from val_col.

---

### read_dicts_from_xls
```python
def read_dicts_from_xls(path_to_file: Path, sheet_name: str) -> list[dict[str, str]]:
```
Reads XLS sheet as list of dictionaries (top row as key).

---

### read_plain_rows_from_csv
```python
def read_plain_rows_from_csv(path_to_file: Path, delimiter: CSVDelimiter = ",", remove_1st_row: bool = False) -> list[list[str]]:
```
Reads plain rows (list of lists) from CSV.

---

### remove_rows_with_given_content_in_lookup_column
```python
def remove_rows_with_given_content_in_lookup_column(rows: list[dict[str, str]], lookup_column: str, match_value: str) -> tuple[list[dict[str, str]], tuple[int, ...]]:
```
Remove rows where lookup_column matches match_value. Returns (new list, indices of removed rows).

---

### write_csv
```python
def write_csv(rows, path_to_file: Path, overwrite: bool, delimiter: CSVDelimiter) -> None:
```
Writes rows (various formats) to CSV file. Adds header if writing dicts/NamedTuples.

---

## tinybear.json_toml_yaml

### check_yaml_file
```python
def check_yaml_file(path_to_file: Path, verbose: bool = True) -> None:
```
Validates YAML file, throws if malformed or duplicate top-level keys are found.

---

### read_json_toml_yaml
```python
def read_json_toml_yaml(path_to_file: Path) -> Union[dict[str, Any], list[str]]:
```
Auto-detects file extension and deserializes JSON, TOML, or YAML to Python types.

---

## tinybear.txt

### check_encoding_of_file
```python
def check_encoding_of_file(file: Path) -> str:
```
Check encoding (utf-8 or cp1251/ANSI); returns detected encoding.

---

### read_non_empty_lines_from_txt_file
```python
def read_non_empty_lines_from_txt_file(path_to_file: Path) -> list[str]:
```
Gets non-empty lines from TXT file as list.

---

### read_plain_text_from_file
```python
def read_plain_text_from_file(path_to_file: Path) -> str:
```
Reads plain text from file (utf-8 or cp1251 encoding).

---

### remove_extra_space
```python
def remove_extra_space(str_: str) -> str:
```
Removes leading/trailing/multiple spaces in a string.

---

### write_plain_text_to_file
```python
def write_plain_text_to_file(content: Union[str, list[str], tuple[str]], file: Path, overwrite: bool, newline_char: str = "\n") -> None:
```
Writes string or lines to text file. Optionally enforces overwrite/newlines.

---

### move_line
```python
def move_line(file: Path, line_number_to_cut: int, line_number_to_insert_before: Union[int, Literal["END"]], output_file: Union[Path, None] = None) -> None:
```
Moves a line in a text file to another position; saves to output file if given.

---

## tinybear.html.validate_html

### validate_html
```python
def validate_html(html: str, allowed_tags: Iterable[str] = (...), is_text_at_root_level_allowed: bool = False) -> None:
```
Validate HTML string for allowed tags, structure, and correct entities. Raises ParsingError on errors.

---

## tinybear.html.from_docx

### convert_file_from_doc
```python
def convert_file_from_doc(path_to_file: Path, output_dir: Path = DEFAULT_OUTPUT_DIR, style_map: str = DEFAULT_STYLE_MAP, print_html: bool = True) -> Path:
```
Read from DOC(x), write to HTML file, return output path.

---

### convert_all_docs
```python
def convert_all_docs(input_dir: Path = DEFAULT_INPUT_DIR, output_dir: Path = DEFAULT_OUTPUT_DIR, print_html: bool = True) -> None:
```
Convert all .DOC(x) files in a directory to HTML.

---

### read_from_doc
```python
def read_from_doc(path_to_file: Path, style_map: str = DEFAULT_STYLE_MAP) -> str:
```
Read binary DOCX file, return HTML string.

---

## tinybear.exceptions

### ParsingError
```python
class ParsingError(Exception):
    """Base class for all parsing errors."""
```
