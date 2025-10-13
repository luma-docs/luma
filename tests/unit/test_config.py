import pytest

from luma.config import resolve_page, ResolvedPage


@pytest.mark.parametrize(
    "content, expected_title",
    [
        ("---\ntitle: Title\n---\n# Heading", "Title"),
        ("# Heading", "Heading"),
        ("## Subheading", "Subheading"),
        ("Paragraph.\n# Heading", "Heading"),
        ("---\ntitle: Title\n---\n# Heading", "Title"),
    ],
)
def test_page_infers_correct_title(content, expected_title, tmp_path):
    with open(tmp_path / "file.md", "w") as file:
        file.write(content)

    resolved_page = resolve_page("file.md", project_root=tmp_path)

    assert resolved_page == ResolvedPage(title=expected_title, path="file.md")
