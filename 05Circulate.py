lst = [10, 20, 30, 40, 50]

k = int(input("Enter number of rotations: "))

n = len(lst)
k = k % n
# print(k)

lst = lst[-k:] + lst[:-k]

print("After rotation:", lst)