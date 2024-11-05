from __future__ import annotations

import pytest

from toolreg.tools import iterate


def test_reduce_list():
    assert iterate.reduce_list([1, 2, 2, 3, 4, 4, 4, 5]) == [1, 2, 3, 4, 5]
    assert iterate.reduce_list([]) == []
    assert iterate.reduce_list(["a", "b", "b", "c"]) == ["a", "b", "c"]


def test_flatten_dict():
    assert iterate.flatten_dict({"a": {"b": {"c": "d"}}}) == {"a/b/c": "d"}
    assert iterate.flatten_dict({"a": {"b": "c"}, "d": "e"}) == {"a/b": "c", "d": "e"}
    assert iterate.flatten_dict({}) == {}


def test_batched():
    assert list(iterate.batched("ABCDEFG", 3)) == [
        ("A", "B", "C"),
        ("D", "E", "F"),
        ("G",),
    ]
    assert list(iterate.batched([], 3)) == []
    assert list(iterate.batched([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]


def test_natsort():
    assert iterate.natsort(["A1", "B1", "A2", "A10"], key=lambda x: x) == [
        "A1",
        "A2",
        "A10",
        "B1",
    ]
    assert iterate.natsort([], key=lambda x: x) == []
    assert iterate.natsort(["B1", "A1"], key=lambda x: x, reverse=True) == [
        "B1",
        "A1",
    ]


def test_do_any():
    assert iterate.do_any([True, False, False]) is True
    assert iterate.do_any([False, False, False]) is False
    assert iterate.do_any([]) is False
    assert iterate.do_any([0, 1, 2], attribute="real") is True


def test_groupby_first_letter():
    data = ["apple", "banana", "cherry", "avocado", "carrot", "blueberry"]
    grouped = iterate.groupby_first_letter(data)
    assert grouped == {
        "A": ["apple", "avocado"],
        "B": ["banana", "blueberry"],
        "C": ["carrot", "cherry"],
    }


def test_groupby_first_letter_with_empty_data():
    data: list[str] = []
    grouped = iterate.groupby_first_letter(data)
    assert grouped == {}


if __name__ == "__main__":
    pytest.main([__file__])
