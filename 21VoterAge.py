try:
    age = int(input("Enter your age: "))
    
    if age < 18:
        raise ValueError("Age must be 18 or above to vote.")
    
    print("You are eligible to vote.")
    
except ValueError as ve:
    if "Age must be" in str(ve):
        print("Not eligible to vote.")
    else:
        print("Error: Please enter a valid age (number only).")
except Exception as e:
    print(f"Unexpected error: {e}")