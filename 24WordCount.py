try:
    with open("Sample.txt", "r") as file:
        data = file.read()
        words = data.split()
    
    print(f"Number of words in the file: {len(words)}")
    
except FileNotFoundError:
    print("Error: Sample.txt file not found!")