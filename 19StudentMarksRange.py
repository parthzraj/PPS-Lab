try:
    marks = int(input("Enter marks: "))
    
    if marks < 0 or marks > 100:
        raise ValueError("Marks should be between 0 and 100.")
    
    print("Valid marks entered.")
    
except ValueError as ve:
    if "Marks should be" in str(ve):
        print("Invalid marks! Marks must be between 0 and 100.")
    else:
        print("Error: Please enter a valid number for marks.")
except Exception as e:
    print(f"Unexpected error: {e}")