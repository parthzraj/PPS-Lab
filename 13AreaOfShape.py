print("Choose shape:")
print("1. Circle")
print("2. Rectangle")
print("3. Triangle")

choice = int(input("Enter your choice (1/2/3): "))

if choice == 1:
    r = float(input("Enter radius: "))
    area = 3.14 * r * r
    print("Area of Circle =", area)

elif choice == 2:
    l = float(input("Enter length: "))
    b = float(input("Enter breadth: "))
    area = l * b
    print("Area of Rectangle =", area)

elif choice == 3:
    b = float(input("Enter base: "))
    h = float(input("Enter height: "))
    area = 0.5 * b * h
    print("Area of Triangle =", area)

else:
    print("Invalid choice")