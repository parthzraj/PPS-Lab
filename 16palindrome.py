texts = input("Enter a string: ")


reverse_text = texts[::-1]


if texts == reverse_text:
    print("The string is a Palindrome")
else:
    print("The string is NOT a Palindrome")