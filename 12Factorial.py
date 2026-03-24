def fact(n):
    result = 1
    for i in range(1, n + 1):
        result = result * i
    return result


num = int(input("Enter a number: "))

if num < 0:
    print("Factorial does not exist for negative numbers")
else:
    print("Factorial of", num, "is", fact(num))