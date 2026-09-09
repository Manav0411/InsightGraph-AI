"""utils/content_cleaner.py — pure regex cleanup."""
from utils.content_cleaner import clean_html_noise, normalize_content, truncate_content


class TestCleanHtmlNoise:
    def test_strips_trailing_boilerplate(self):
        text = "Real content here.\nRead more about this elsewhere"
        assert clean_html_noise(text).strip() == "Real content here."

    def test_case_insensitive_and_multiple_patterns(self):
        text = "Body.\nADVERTISEMENT stuff\nRelated stories: a, b, c"
        out = clean_html_noise(text)
        assert "ADVERTISEMENT" not in out
        assert "Related stories" not in out
        assert "Body." in out

    def test_empty(self):
        assert clean_html_noise("") == ""
        assert clean_html_noise(None) == ""


class TestNormalizeContent:
    def test_collapses_whitespace_and_newlines(self):
        # \n+ -> \n, then ' +' -> ' ', then outer strip()
        assert normalize_content("a\n\n\nb   c\n") == "a\nb c"
        assert normalize_content("x    y") == "x y"

    def test_empty(self):
        assert normalize_content("") == ""


class TestTruncateContent:
    def test_under_limit_unchanged(self):
        assert truncate_content("short", max_length=100) == "short"

    def test_over_limit_adds_ellipsis(self):
        assert truncate_content("abcdef", max_length=3) == "abc..."
