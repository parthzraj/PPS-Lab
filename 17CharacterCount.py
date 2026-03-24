def count(s, character):
    con = 0
    
    for i in range(0, len(s)):
        if s[i] == character:
            con += 1
            
    return con

string = input("Enter a string: ")
char = input("Enter a character to count: ")

result = count(string, char)

print("Number of times", char, "appears:", result)