import pytest
from bubble_sort import bubble_sort

def test_empty_list():
    assert bubble_sort([]) == []

def test_single_element_list():
    assert bubble_sort([42]) == [42]

def test_already_sorted():
    assert bubble_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_reverse_sorted():
    assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_duplicates():
    assert bubble_sort([2, 1, 2, 1]) == [1, 1, 2, 2]

def test_negatives():
    assert bubble_sort([-1, -5, 0, 3, -2]) == [-5, -2, -1, 0, 3]

def test_reverse_true():
    assert bubble_sort([3, 1, 4, 1, 5, 9, 2, 6], reverse=True) == [9, 6, 5, 4, 3, 2, 1, 1]

def test_strings():
    assert bubble_sort(["orange", "apple", "banana"]) == ["apple", "banana", "orange"]

def test_floats():
    assert bubble_sort([3.14, 1.1, 2.718, 0.5]) == [0.5, 1.1, 2.718, 3.14]
