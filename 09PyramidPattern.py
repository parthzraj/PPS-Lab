n = 5
num = 0

for i in range(1, n + 1):
    
    for j in range(n - i):
        print(" ", end=" ")

    
    for j in range(2 * i - 1):
        print(num, end=" ")
        num += 1

    print()