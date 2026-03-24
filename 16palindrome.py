text = input("Enter a string: ")


reverse_text = text[::-1]


if text == reverse_text:
    print("The string is a Palindrome")
else:
    print("The string is NOT a Palindrome")