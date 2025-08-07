import re

from tests.paths import DIR_WITH_TEST_FILES
from tinybear.html.from_docx import read_from_doc, convert_file_from_doc, convert_all_docs

CUSTOM_STYLE_MAP = """
b => b
i => i
p[style-name='Title'] => h1
p[style-name='Heading1'] => h2
p[style-name='Heading 1'] => h2
p[style-name='Heading2'] => h3
p[style-name='Heading 2'] => h3
p[style-name='Heading3'] => h4
p[style-name='Heading 3'] => h4
p[style-name='Heading4'] => strong
p[style-name='Heading 4'] => strong
"""

TEST_DOCS_DIR = DIR_WITH_TEST_FILES / "html" / "from_docx"
TEST_DOCX_FILE = TEST_DOCS_DIR / "default_style.docx"


def test_read_from_doc():
    html = read_from_doc(TEST_DOCX_FILE)
    patterns = [
        (r"<h1>This is the document title</h1>", "Title -> h1"),
        (r"<h1>Heading level 1</h1>", "Heading1 -> h1"),
        (r"<h2>Heading level 2</h2>", "Heading2 -> h2"),
        (r"<h3>Heading level 3</h3>", "Heading3 -> h3"),
        (r"<h4>Heading level 4</h4>", "Heading4 -> h4"),
        (r"<strong>bold text</strong>", "Bold text -> <strong>"),
        (r"<em>italic text</em>", "Italic text -> <em>"),
        (
            r"<strong><em>bold italic text</em></strong>|<em><strong>bold italic text</strong></em>",
            "Bold italic text -> <strong><em> or <em><strong>",
        ),
    ]
    for pattern, desc in patterns:
        assert re.search(pattern, html), f"Missing or incorrect: {desc}"


def test_read_from_doc_with_custom_style_map():

    html = read_from_doc(TEST_DOCX_FILE, style_map=CUSTOM_STYLE_MAP)
    patterns = [
        (r"<h1>This is the document title</h1>", "Title -> h1"),
        (r"<h2>Heading level 1</h2>", "Heading1 -> h2"),
        (r"<h3>Heading level 2</h3>", "Heading2 -> h3"),
        (r"<h4>Heading level 3</h4>", "Heading3 -> h4"),
        (r"<strong>Heading level 4</strong>", "Heading4 -> strong"),
        (r"<b>bold text</b>", "Bold text -> <b>"),
        (r"<i>italic text</i>", "Italic text -> <i>"),
        (
            r"<b><i>bold italic text</i></b>|<i><b>bold italic text</i></b>",
            "Bold italic text -> <b><i> or <i><b>",
        ),
    ]
    for pattern, desc in patterns:
        assert re.search(pattern, html), f"Missing or incorrect: {desc}"


def test_convert_file_from_doc(tmp_path):
    output_path = convert_file_from_doc(TEST_DOCX_FILE, output_dir=tmp_path, print_html=False)
    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    # Spot check for a couple of tags
    assert "<h1>Heading level 1</h1>" in html
    assert "<strong>bold text</strong>" in html


def test_convert_file_from_doc_with_custom_style_map(tmp_path):
    output_path = convert_file_from_doc(
        TEST_DOCX_FILE, output_dir=tmp_path, print_html=False, style_map=CUSTOM_STYLE_MAP
    )
    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    # Check for custom mapping effect
    assert "<h2>Heading level 1</h2>" in html or "<h2>Heading level 1" in html
    assert "<b>bold text</b>" in html


def test_convert_file_from_doc_prints_html(tmp_path, caplog):
    with caplog.at_level("INFO"):
        output_path = convert_file_from_doc(TEST_DOCX_FILE, output_dir=tmp_path, print_html=True)
    assert output_path.exists()
    # Check that HTML was logged
    assert any("document title" in message for message in caplog.messages)


def test_convert_all_docs_logs_conversion(tmp_path, caplog):
    with caplog.at_level("INFO"):
        convert_all_docs(input_dir=TEST_DOCS_DIR, output_dir=tmp_path, print_html=False)
    # Check that "Converting" and the file name are in the logs
    assert any(
        "Converting" in message and TEST_DOCX_FILE.name in message for message in caplog.messages
    )
