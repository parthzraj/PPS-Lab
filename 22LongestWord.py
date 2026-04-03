try:
    with open("Sample.txt", "r") as file:
        data = file.read()
        words = data.split()
    
    if words:
        longest_word = max(words, key=len)
        print(f"Longest word: {longest_word}")
        print(f"Length of longest word: {len(longest_word)}")
    else:
        print("The file is empty.")
        
except FileNotFoundError:
    print("Error: Sample.txt file not found!")