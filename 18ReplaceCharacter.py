def replace_char(s, c1, c2):
    new_s = s.replace(c1, c2)
    return new_s



string = input("Enter a string: ")
char1 = input("Enter character to replace: ")
char2 = input("Enter new character: ")

result = replace_char(string, char1, char2)

print("Updated string:", result)