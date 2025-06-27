from bs4 import BeautifulSoup, Tag

from tinybear.exceptions import ParsingError


def validate_html(html: str, is_text_at_root_level_allowed: bool) -> None:
    """
    Validate that the HTML string is well-formed and only contains allowed tags.

    Args:
        html: The HTML string to validate
        is_text_at_root_level_allowed: If True, allow text nodes at the root level.
            If False (default), all text must be wrapped in block elements.

    Raises:
        ParsingError: If the HTML is not well-formed or contains disallowed tags
    """
    if not html:
        return  # Empty string is valid

    _check_for_unescaped_ampersand(html)

    soup = BeautifulSoup(html, "html.parser")

    if not is_text_at_root_level_allowed:
        _check_for_root_level_text(soup)

    _check_all_tags_are_allowed(soup)
    _check_list_structure(soup)
    _check_paragraphs(soup)

    # check cases that bs4 will not catch because of autocorrection of tags
    _check_for_unclosed_tags(html)


def _check_all_tags_are_allowed(soup: BeautifulSoup) -> None:
    """Validate that only allowed tags are present in the HTML."""
    allowed_tags = {"p", "ul", "ol", "li", "a", "i", "b", "em", "strong", "u", "sup", "sub"}
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
    """Validate that there's no text at the root level."""
    for child in soup.children:
        if isinstance(child, str) and child.strip():
            raise ParsingError(f"Text must be wrapped in a block element, found: {child[:50]}...")


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
    - Unclosed angle brackets: <tag without matching >
    - Unclosed tags: <p> without </p>

    This problem cannot be caught by bs4, so we have to analyze the raw HTML.
    """
    i = 0
    n = len(html)

    while i < n:
        if html[i] != "<":
            i += 1
            continue

        tag_name, tag_end, is_closing = _find_tag_end(html, i)
        if not tag_name:
            i += 1
            continue

        # Handle special tags like !doctype or comments
        if _is_special_tag(tag_name):
            gt_pos = html.find(">", i)
            if gt_pos == -1:
                raise ParsingError(f"Unclosed tag at position {i}: {html[max(0, i-20):i+20]}...")
            i = gt_pos + 1
            continue

        # Find the end of the current tag
        gt_pos = html.find(">", i)
        if gt_pos == -1:
            raise ParsingError(
                f"Unclosed angle bracket at position {i}: {html[max(0, i-20):i+20]}..."
            )

        # Check for unclosed tags if it's an opening tag that's not self-closing
        if not is_closing and not _is_self_closing_tag(tag_name):
            _check_nested_tags(html=html, tag_name=tag_name, start_pos=i)

        i = gt_pos + 1


def _check_list_structure(soup: BeautifulSoup) -> None:
    """Validate the structure of lists and list items."""
    # Check list structure
    for list_tag in soup.find_all(["ul", "ol"]):
        for child in list_tag.children:
            if isinstance(child, Tag) and child.name != "li":
                raise ParsingError(
                    f"<{list_tag.name}> can only contain <li> elements, "
                    f"found <{child.name}>: {child}"
                )

    # Check that <li> elements are direct children of <ul> or <ol>
    for li in soup.find_all("li"):
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
    paragraphs = soup.find_all("p")

    # Check for empty paragraphs
    for p in paragraphs:
        if not p.get_text(strip=True):
            raise ParsingError("Empty <p> tags are not allowed")

    # Check for nested paragraphs
    for p in paragraphs:
        if p.find_parent("p"):
            raise ParsingError("Nested <p> tags are not allowed")


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
