def binary_search(arr: list, target) -> int:
    """Perform binary search on a sorted list to find the index of target."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


if __name__ == "__main__":
    sample_list = [11, 12, 22, 25, 34, 64, 90]
    target_value = 25
    print("Sorted list:", sample_list)
    print(f"Searching for {target_value}...")
    index = binary_search(sample_list, target_value)
    if index != -1:
        print(f"Element {target_value} found at index {index}.")
    else:
        print(f"Element {target_value} not found in the list.")

    missing_target = 100
    print(f"Searching for {missing_target}...")
    missing_index = binary_search(sample_list, missing_target)
    if missing_index != -1:
        print(f"Element {missing_target} found at index {missing_index}.")
    else:
        print(f"Element {missing_target} not found in the list.")
