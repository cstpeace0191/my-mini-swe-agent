def bubble_sort(arr: list, reverse: bool = False) -> list:
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if (reverse and arr[j] < arr[j + 1]) or (not reverse and arr[j] > arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

if __name__ == "__main__":
    sample_list = [64, 34, 25, 12, 22, 11, 90]
    print("Original list:", sample_list)
    sorted_list = bubble_sort(sample_list.copy())
    print("Sorted list (ascending):", sorted_list)
    sorted_list_desc = bubble_sort(sample_list.copy(), reverse=True)
    print("Sorted list (descending):", sorted_list_desc)
