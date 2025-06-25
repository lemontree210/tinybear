import pytest

from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard

from tests.paths import DIR_WITH_TEST_FILES
from tinybear.csv_xls import write_csv


def test_check_existence_of_output_csv_file_and_compare_with_gold_standard_unlinks_output_file_after_comparison():  # noqa E501
    dummy_gold_standard_file = DIR_WITH_TEST_FILES / "helpers_dummy_gold_standard.csv"
    dummy_output_file = DIR_WITH_TEST_FILES / "helpers_dummy_output.csv"

    rows = [["id", "en"], ["1", "foo"]]

    for path in dummy_output_file, dummy_gold_standard_file:
        write_csv(rows, path, overwrite=True, delimiter=",")

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=dummy_output_file,
        gold_standard_file=dummy_gold_standard_file,
    )

    assert not dummy_output_file.exists()
    assert dummy_gold_standard_file.exists()
    dummy_gold_standard_file.unlink()
