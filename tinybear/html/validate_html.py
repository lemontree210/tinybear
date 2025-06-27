from collections.abc import Iterable

from bs4 import BeautifulSoup, Tag

from tinybear.exceptions import ParsingError


def validate_html(
    html: str,
    allowed_tags: Iterable[str] = (
        "a",
        "b",
        "body",
        "em",
        "head",
        "html",
        "i",
        "li",
        "ol",
        "p",
        "strong",
        "sub",
        "sup",
        "u",
        "ul",
    ),
    is_text_at_root_level_allowed: bool = False,
) -> None:
    """
    Validate that the HTML string is well-formed and only contains allowed tags.

    Args:
        html: The HTML string to validate
        allowed_tags: Iterable of allowed HTML tag names (e.g., ['p', 'a', 'strong']).
            Defaults to a basic (quite restrictive) set of tags.
        is_text_at_root_level_allowed: If True, allow text nodes at the root level.
            If False (default), all text must be wrapped in block elements.

    Raises:
        ParsingError: If the HTML is not well-formed or contains disallowed tags
    """
    if not html:
        return  # Empty string is valid

    _check_for_unescaped_ampersand(html)

    soup = BeautifulSoup(html, "html5lib")

    _check_all_tags_are_allowed(soup=soup, allowed_tags=allowed_tags)
    _check_list_structure(soup)
    _check_paragraphs(soup)

    if not is_text_at_root_level_allowed:
        _check_for_root_level_text(soup)

    # check cases that bs4 will not catch because of autocorrection of tags
    _check_for_unclosed_tags(html)


def _check_all_tags_are_allowed(soup: BeautifulSoup, allowed_tags: Iterable[str]) -> None:
    """Validate that only allowed tags are present in the HTML."""
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            raise ParsingError(
                f"Tag '{tag.name}' is not allowed. "
                f"Only {', '.join(f'<{t}>' for t in sorted(allowed_tags))} are allowed."
            )


def _check_entity_with_ampersand(html: str, position: int) -> int:
    """Validate that an HTML entity is properly formatted.
    Return the position of the semicolon that closes the entity.
    """
    semicolon_pos = html.find(";", position + 1)
    if semicolon_pos == -1:
        raise ParsingError(f"Text contains unescaped &: {html[position:position + 50]}...")

    entity = html[position + 1 : semicolon_pos]
    if not (entity.startswith("#") and entity[1:].isdigit()) and entity not in [
        "amp",
        "lt",
        "gt",
        "quot",
        "apos",
    ]:
        raise ParsingError(
            f"Invalid HTML entity: &{entity}; in: {html[position:position + 50]}..."
        )

    return semicolon_pos


def _check_for_root_level_text(soup: BeautifulSoup) -> None:
    """Validate that there's no text at the root level or after block elements.

    This function checks for text nodes that are not properly wrapped in block elements.
    It allows text in certain inline elements but requires other text to be in block elements.
    """
    # First check direct children of the root for any text nodes
    body = soup.find("body")  # even if there's no <body> tag, html5lib will wrap content in one
    for child in body.children:
        if isinstance(child, str) and child.strip():
            raise ParsingError("Text must be wrapped in a block element")


def _check_for_unescaped_ampersand(html: str) -> None:
    """Check that there are no unescaped ampersands."""
    position = 0

    while position < len(html):
        if html[position] == "&":
            semicolon_pos = _check_entity_with_ampersand(html, position)
            position = semicolon_pos + 1
        else:
            position += 1


def _check_for_unclosed_tags(html: str) -> None:
    """Check for unclosed HTML tags in the raw HTML text.

    This checks for patterns that indicate unclosed tags, such as:
    - Unclosed angle brackets: <tag without matching > or just a less than sign
    - Unclosed tags: <p> without </p>


    This problem cannot be caught by bs4, so we have to analyze the raw HTML.
    """
    current_pos = 0

    while current_pos < len(html):
        if html[current_pos] != "<":
            current_pos += 1
            continue

        tag_name, tag_end_pos, is_closing_tag = _find_tag_end(html, current_pos)
        if not tag_name:
            current_pos += 1
            continue

        # Handle special tags like !doctype or comments
        if _is_special_tag(tag_name):
            closing_angle_pos = html.find(">", current_pos)
            if closing_angle_pos == -1:
                raise ParsingError(
                    f"Unclosed tag at position {current_pos}: "
                    f"{html[max(0, current_pos-20):current_pos+20]}..."
                )
            current_pos = closing_angle_pos + 1
            continue

        # Find the end of the current tag
        closing_angle_pos = html.find(">", current_pos)
        if closing_angle_pos == -1:
            raise ParsingError(
                f"Unclosed angle bracket at position {current_pos}: "
                f"{html[max(0, current_pos-20):current_pos+20]}..."
            )

        # Check for unclosed tags if it's an opening tag that's not self-closing
        if not is_closing_tag and not _is_self_closing_tag(tag_name):
            _check_nested_tags(html=html, tag_name=tag_name, start_pos=current_pos)

        current_pos = closing_angle_pos + 1


def _check_list_structure(soup: BeautifulSoup) -> None:
    """Validate the structure of lists and list items."""
    # Check list structure
    for list_tag in soup(["ul", "ol"]):
        for child in list_tag.children:
            if isinstance(child, Tag) and child.name != "li":
                raise ParsingError(
                    f"<{list_tag.name}> can only contain <li> elements, "
                    f"found <{child.name}>: {child}"
                )

    # Check that <li> elements are direct children of <ul> or <ol>
    for li in soup("li"):
        parent = li.parent
        if parent.name not in ["ul", "ol"]:
            raise ParsingError(
                f"<li> must be a direct child of <ul> or <ol>, "
                f"found inside <{parent.name}>: {li}"
            )


def _check_nested_tags(html: str, tag_name: str, start_pos: int) -> None:
    """Check for properly nested tags."""
    closing_tag = f"</{tag_name}>"
    next_open = html.find(f"<{tag_name}", start_pos + 1)
    next_close = html.find(closing_tag, start_pos + 1)

    if next_open == -1 or (next_close != -1 and next_close < next_open):
        if next_close == -1:
            raise ParsingError(
                f"Unclosed <{tag_name}> tag at position {start_pos}: "
                f"{html[max(0, start_pos-20):start_pos+20]}..."
            )
        return

    # Handle nested tags
    nested_level = 1
    pos = start_pos + 1
    while pos < len(html) and nested_level > 0:
        next_open = html.find(f"<{tag_name}", pos)
        next_close = html.find(f"</{tag_name}", pos)

        if next_open != -1 and (next_close == -1 or next_open < next_close):
            nested_level += 1
            pos = next_open + 1
        elif next_close != -1:
            nested_level -= 1
            pos = next_close + 1
        else:
            break

    if nested_level > 0:
        raise ParsingError(
            f"Unclosed <{tag_name}> tag starting at position {start_pos}: "
            f"{html[max(0, start_pos-20):start_pos+20]}..."
        )


def _check_paragraphs(soup: BeautifulSoup) -> None:
    """Validate paragraph structure and content."""
    paragraphs = soup("p")

    # Check for empty or nested paragraphs
    # Due to how parser works, nested paragraphs will end up being transformed into
    # sequence of paragraphs with empty paragraph at the end.
    for p in paragraphs:
        if not p.get_text(strip=True):
            raise ParsingError("Empty or nested <p> tags are not allowed")


def _find_tag_end(html: str, start_pos: int) -> tuple[str, int, bool]:
    """Extract tag name, end position, and if it's a closing tag."""
    if start_pos >= len(html) or html[start_pos] != "<":
        return "", start_pos, False

    tag_start = start_pos + 1
    is_closing = tag_start < len(html) and html[tag_start] == "/"
    if is_closing:
        tag_start += 1

    tag_end = tag_start
    while tag_end < len(html) and (html[tag_end].isalnum() or html[tag_end] in "-_"):
        tag_end += 1

    tag_name = html[tag_start:tag_end].lower()
    return tag_name, tag_end, is_closing


def _is_self_closing_tag(tag_name: str) -> bool:
    """Check if a tag is self-closing."""
    return tag_name in ("br", "img", "hr", "input", "meta", "link")


def _is_special_tag(tag_name: str) -> bool:
    """Check if a tag is a special tag like !doctype or comment."""
    return tag_name in ("!doctype", "!--")
