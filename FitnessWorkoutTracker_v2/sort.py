# sort.py

def insertion_sort(exercises, key='duration'):
    # Make a copy so we don’t change the original list
    arr = list(exercises)
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1

        # Move bigger items one step right
        while j >= 0 and getattr(arr[j], key) > getattr(current, key):
            arr[j + 1] = arr[j]
            j -= 1

        # Insert current in the correct spot
        arr[j + 1] = current

    return arr
