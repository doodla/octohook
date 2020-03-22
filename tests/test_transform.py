import pytest

from octohook.models import _transform as transform


@pytest.mark.parametrize(
    "url, local_variables, expected",
    [
        ("url/{a}/{b}", {"a": "a", "b": "b"}, "url/a/b"),
        ("url/some/more/{a}...{b}", {"a": "a", "b": "b"}, "url/some/more/a...b"),
    ],
)
def test_no_optional(url, local_variables, expected):
    assert transform(url, local_variables) == expected


@pytest.mark.parametrize(
    "url, local_variables, expected",
    [
        ("url/a{/b}", {"b": "b"}, "url/a/b"),
        ("url/a{/b}", {"b": None}, "url/a"),
        ("url{/a}{/b}", {"a": None, "b": None}, "url"),
        ("url{/a}{/b}", {"a": "a", "b": None}, "url/a"),
        ("url{/a}{/b}", {"a": "a", "b": None}, "url/a"),
        ("url{/a}{/b}", {"a": None, "b": "b"}, "url"),
        ("url{/a}{/b}{/c}", {"a": None, "b": "b"}, "url"),
    ],
)
def test_all_optional(url, local_variables, expected):
    assert transform(url, local_variables) == expected


@pytest.mark.parametrize(
    "url, local_variables, expected",
    [
        ("url/{a}{/b}", {"a": "a", "b": "b"}, "url/a/b"),
        ("url/{a}{/b}", {"a": "a", "b": None}, "url/a"),
        ("url/{a}{/b}{/c}", {"a": "a", "b": "b", "c": "c"}, "url/a/b/c"),
        ("url/{a}{/b}{/c}", {"a": "a", "b": "b", "c": None}, "url/a/b"),
        ("url/{a}{/b}{/c}", {"a": "a", "b": None, "c": None}, "url/a"),
        ("url/{a}{/b}{/c}", {"a": "a", "b": None, "c": "c"}, "url/a"),
        ("url/{a}...{b}{/c}", {"a": "a", "b": "b", "c": "c"}, "url/a...b/c"),
        ("url/{a}...{b}{/c}", {"a": "a", "b": "b", "c": None}, "url/a...b"),
    ],
)
def test_some_optional(url, local_variables, expected):
    assert transform(url, local_variables) == expected
