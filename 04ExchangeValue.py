lst = list(map(int, input("Enter list elements (give sapce for each distinct element): ").split()))

i = int(input("Enter first index: "))
j = int(input("Enter second index: "))


if 0 <= i < len(lst) and 0 <= j < len(lst):
    lst[i], lst[j] = lst[j], lst[i]
    print("Updated list:", lst)
else:
    print("Invalid indices!")