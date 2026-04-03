try:
    with open("Source.txt", "r") as source_file:
        data = source_file.read()
    
    with open("Dest.txt", "w") as dest_file:
        dest_file.write(data)
    
    print("File copied successfully!")
    
except FileNotFoundError:
    print("Error: Source.txt file not found!")
except Exception as e:
    print(f"An error occurred: {e}")