import math

def sin_series(x, terms):
    result = 0
    for n in range(terms):
        term = ((-1)**n) * (x**(2*n + 1)) / math.factorial(2*n + 1)
        result += term
    return result


x = float(input("Enter value of x (in radians): "))
terms = int(input("Enter number of terms: "))


approx = sin_series(x, terms)
actual = math.sin(x)

print("Sin(x) using series:", approx)
print("Actual Sin(x):", actual)