try:
    a = int(input("Enter numerator: "))
    b = int(input("Enter denominator: "))
    result = a / b
    print(f"Result: {result}")
    
except ValueError:
    print("Error: Please enter valid numbers only!")
except ZeroDivisionError:
    print("Error: Cannot divide by zero!")
except Exception as e:
    print(f"Unexpected error: {e}")