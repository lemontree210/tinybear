from bs4 import BeautifulSoup, Tag

from tinybear.exceptions import ParsingError


def validate_html(html: str, is_text_at_root_level_allowed: bool) -> None:
    """
    Validate that HTML conforms to our requirements.

    Requirements:
    - Only <p>, <ul>, <ol>, and <li> tags are allowed
    - No <br> tags (should be converted to paragraphs)
    - <ul> and <ol> must only contain <li> elements
    - <li> elements must be direct children of <ul> or <ol>
    - No empty <p> tags
    - No nested <p> tags
    - No text nodes at the root level (must be wrapped in a block element)
    - No `<` or `>` signs that aren't HTML entities
    - No unescaped & characters

    Raises:
        ParsingError: If the HTML doesn't conform to the requirements
    """
    if not html:
        return  # Empty string is valid

    _check_absence_of_unescaped_ampersand(html)

    soup = BeautifulSoup(html, "html.parser")

    if not is_text_at_root_level_allowed:
        _check_absence_of_root_level_text(soup)

    _validate_tags(soup)
    _validate_list_structure(soup)
    _validate_paragraphs(soup)


def _check_absence_of_root_level_text(soup: BeautifulSoup) -> None:
    """Validate that there's no text at the root level."""
    for child in soup.children:
        if isinstance(child, str) and child.strip():
            raise ParsingError(f"Text must be wrapped in a block element, found: {child[:50]}...")


def _check_absence_of_unescaped_ampersand(html: str) -> None:
    """Check that there are no unescaped ampersands."""
    position = 0

    while position < len(html):
        if html[position] == "&":
            semicolon_pos = _validate_entity_with_ampersand(html, position)
            position = semicolon_pos + 1
        else:
            position += 1


def _validate_entity_with_ampersand(html: str, position: int) -> int:
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


def _validate_list_structure(soup: BeautifulSoup) -> None:
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


def _validate_paragraphs(soup: BeautifulSoup) -> None:
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


def _validate_tags(soup: BeautifulSoup) -> None:
    """Validate that only allowed tags are present in the HTML."""
    allowed_tags = {"p", "ul", "ol", "li", "a", "i", "b", "em", "strong", "u", "sup", "sub"}
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            raise ParsingError(
                f"Tag '{tag.name}' is not allowed. "
                f"Only {', '.join(f'<{t}>' for t in sorted(allowed_tags))} are allowed."
            )
