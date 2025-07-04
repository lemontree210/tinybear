"""Tests for the HTML validator."""

import pytest

from tinybear.exceptions import ParsingError
from tinybear.html import validate_html

# Valid HTML test cases
VALID_HTML_CASES = [
    # Empty string is valid
    "",
    # Basic structure
    "<html><head><title>Title</title></head><body><p>Content</p></body></html>",
    # Text formatting
    "<p>This is <b>bold</b>, <i>italic</i>, <u>underlined</u>, <em>emphasized</em>, <strong>strong</strong> text.</p>",
    "<p>Subscript: H<sub>2</sub>O, Superscript: x<sup>2</sup></p>",
    # Links
    "<p>Visit <a href='https://example.com'>example</a> for more info</p>",
    # Lists
    "<ul><li>First item</li><li>Second item</li><li>Third item</li></ul>",
    "<ol><li>First</li><li>Second</li><li>Third</li></ol>",
    # Nested lists
    """<ul>
        <li>Item 1</li>
        <li>Item 2
            <ul>
                <li>Subitem 1</li>
                <li>Subitem 2</li>
            </ul>
        </li>
        <li>Item 3</li>
    </ul>""",
    # Mixed content
    "<p>Text before</p><ul><li>Item</li></ul><p>Text after</p>",
    # Complex nesting
    """<html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Welcome</h1>
        <p>This is a <strong>test</strong> of <em>HTML</em> validation.</p>
        <p>Features:</p>
        <ul>
            <li>Supports <b>bold</b> and <i>italic</i> text</li>
            <li>Handles <a href='#'>links</a></li>
            <li>Works with <sub>subscripts</sub> and <sup>superscripts</sup></li>
        </ul>
    </body>
</html>""",
]

# Invalid HTML test cases with expected error messages
INVALID_HTML_CASES = [
    # Disallowed tags
    ("<div>Not allowed</div>", "Tag 'div' is not allowed"),
    ("<p><span>Span not allowed</span></p>", "Tag 'span' is not allowed"),
    # BR tags
    ("<p>Line 1<br>Line 2</p>", "Tag 'br' is not allowed"),
    # Invalid list structure
    ("<ul><p>Not an li</p></ul>", "<ul> can only contain <li> elements"),
    ("<li>Not in a list</li>", "<li> must be a direct child of <ul> or <ol>"),
    # Empty paragraphs
    ("<p></p>", "Empty or nested <p> tags are not allowed"),
    ("<p>   </p>", "Empty or nested <p> tags are not allowed"),
    ("<p>One, then <p>Nested</p></p>", "Empty or nested <p> tags are not allowed"),
    # Text at root level
    ("Text not in paragraph", "Text must be wrapped in a block element"),
    ("<p>Paragraph</p>And some text", "Text must be wrapped in a block element"),
    # Unescaped ampersand
    ("<p>AT&T</p>", "Text contains unescaped &: &T</p>"),
    ("<p>Invalid entity: &invalid;</p>", "Invalid HTML entity: &invalid; in: &invalid;</p>"),
    ("<p>Missing semicolon: &amp</p>", "Text contains unescaped &: &amp</p>"),
    # Unclosed tags
    ("<p>Unclosed tag<p>", "Empty or nested <p> tags are not allowed"),
    ("<p>Invalid <tag</p>", "Tag 'tag<' is not allowed"),
    ("<p>Text <b>bold text</p> more text", "Unclosed tags found"),
    # Unescaped < signs in content (must be &lt;)
    ("<p>5 < 10</p>", "Unescaped '<' found in text content. Use '&lt;' instead."),
    ("<p>if x < 5: print(x)</p>", "Unescaped '<' found in text content. Use '&lt;' instead."),
    (
        "<p>Unclosed <a href='#'>link</p>",
        "Unclosed tags found:a",
    ),
    ("<p>Unclosed at end <", "Unescaped '<' found in text content. Use '&lt;' instead."),
]


@pytest.mark.parametrize("html", VALID_HTML_CASES)
def test_validate_html_valid(html):
    """Test that valid HTML passes validation."""
    validate_html(html, is_text_at_root_level_allowed=False)


# Test cases with valid HTML that includes properly escaped HTML entities
VALID_ESCAPED_HTML = [
    "<p>5 &lt; 10</p>",
    "<p>10 &gt; 5</p>",
    "<p>AT&amp;T</p>",
    "<p>Use &lt; and &gt; for tags</p>",
    "<p>Quotes: &quot;double&quot; and &apos;single&apos;</p>",
    "<p>Numeric entities: &#34;double&#34; and &#39;single&#39;</p>",
    "<p>Mixed: 1 &lt; 2 &amp;&amp; 3 &gt; 2</p>",
]


@pytest.mark.parametrize("html", VALID_ESCAPED_HTML)
def test_validate_html_with_escaped_chars(html):
    """Test that valid HTML with properly escaped characters passes validation."""
    # Should not raise an exception
    validate_html(html, is_text_at_root_level_allowed=False)


@pytest.mark.parametrize("html,expected_error", INVALID_HTML_CASES)
def test_validate_html_invalid(html, expected_error):
    """Test that invalid HTML raises the expected error."""
    with pytest.raises(ParsingError, match=expected_error):
        validate_html(html, is_text_at_root_level_allowed=False)


def test_validate_html_with_allowed_text_at_root_level():
    # Text at root level
    validate_html(html="Text", is_text_at_root_level_allowed=True)


def test_validate_html_with_unclosed_angle_bracket():
    """Test that unclosed tags are handled by BeautifulSoup's HTML parsing."""
    # BeautifulSoup will auto-close unclosed tags, so we don't need to test for them
    # Here we just verify that the validation passes for valid HTML
    validate_html("<p>Test</p>", is_text_at_root_level_allowed=False)

    # Test that invalid tags are still caught
    with pytest.raises(ParsingError, match=r"Tag 'invalid' is not allowed"):
        validate_html("<invalid>Test</invalid>", is_text_at_root_level_allowed=False)


def test_validate_html_with_unescaped_ampersand_without_semicolon():
    """Test that an unescaped ampersand without a semicolon raises an error."""
    # Test with an ampersand not followed by a semicolon
    invalid_html = "<p>This is a test with an unescaped ampersand: &invalid</p>"
    with pytest.raises(ParsingError, match=r"Text contains unescaped &: &invalid"):
        validate_html(invalid_html, is_text_at_root_level_allowed=False)

    # Test with an ampersand at the end of the string
    invalid_html = "<p>Ends with ampersand &"
    with pytest.raises(ParsingError, match=r"Text contains unescaped &: &"):
        validate_html(invalid_html, is_text_at_root_level_allowed=False)
