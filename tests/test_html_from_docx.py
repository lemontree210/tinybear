import re

from tests.paths import DIR_WITH_TEST_FILES
from tinybear.html.from_docx import read_from_doc, convert_file_from_doc

test_docx_path = DIR_WITH_TEST_FILES / "html" / "from_docx" / "default_style.docx"


def test_read_from_doc():
    html = read_from_doc(test_docx_path)
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


def test_convert_file_from_doc(tmp_path):
    output_path = convert_file_from_doc(test_docx_path, output_dir=tmp_path, print_html=False)
    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    # Spot check for a couple of tags
    assert "<h1" in html and "document title" in html
    assert "<strong>bold text</strong>" in html
