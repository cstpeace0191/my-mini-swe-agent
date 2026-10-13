import pytest
from binary_search import binary_search


def test_empty_list():
    assert binary_search([], 5) == -1


def test_single_element_found():
    assert binary_search([42], 42) == 0


def test_single_element_not_found():
    assert binary_search([42], 10) == -1


def test_element_found_beginning():
    assert binary_search([1, 2, 3, 4, 5], 1) == 0


def test_element_found_end():
    assert binary_search([1, 2, 3, 4, 5], 5) == 4


def test_element_found_middle():
    assert binary_search([1, 2, 3, 4, 5], 3) == 2


def test_element_not_found_smaller():
    assert binary_search([10, 20, 30, 40], 5) == -1


def test_element_not_found_larger():
    assert binary_search([10, 20, 30, 40], 50) == -1


def test_element_not_found_between():
    assert binary_search([10, 20, 30, 40], 25) == -1


def test_even_length_list():
    assert binary_search([2, 4, 6, 8, 10, 12], 8) == 3


def test_odd_length_list():
    assert binary_search([1, 3, 5, 7, 9], 7) == 3


def test_negative_numbers():
    assert binary_search([-10, -5, 0, 5, 10], -5) == 1


def test_floats():
    assert binary_search([0.5, 1.1, 2.718, 3.14], 2.718) == 2


def test_strings():
    assert binary_search(["apple", "banana", "cherry", "date"], "cherry") == 2
