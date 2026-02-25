#Project using Dictionaries
#quetions 5 (experiments) - Implementing real-time/technical applications using Sets, Dictionaries. (Language, components of an automo- bile, Elements of a civil structure, etc.- operations of Sets &Dictionaries)


goodMaterials = {
    "Concrete": {"Steel", "Gravel"},
    "Steel": {"Concrete"},
    "Wood": {"Paint", "Nails"},
    "Glass": {"Aluminum"},
    "Aluminum": {"Glass"}
}


notGoodMaterials = {
    "Wood": {"Concrete"},  
    "Steel": {"Water"},    
    "Aluminum": {"Copper"} 
}

TakenMaterials = set()


def add_material():
    material = input("Enter material to add: ").title()
    TakenMaterials.add(material)
    print(f"{material} added to structure.\n")


def show_selected():
    print("\nCurrent Selected Materials:")
    print(TakenMaterials)
    print()


def check_compatibility():
    print("\n--- Compatibility Check Report ---")

    problemsMa = False

    for material in TakenMaterials:
        if material in notGoodMaterials:
            conflicts = notGoodMaterials[material].intersection(TakenMaterials)

            if conflicts:
                print(f"{material} is incompatible with {conflicts}")
                problemsMa = True

    if not problemsMa:
        print("All selected materials are compatible.")
    print()


def check_strong_bonds():
    print("\nStrong Compatibility Check")

    for material in TakenMaterials:
        if material in goodMaterials:
            matches = goodMaterials[material].intersection(TakenMaterials)
            if matches:
                print(f"{material} works well with {matches}")
    print()


def menu():
    while True:
        print("Structural Material Compatibility Checker")
        print("1. Add Material")
        print("2. Show Selected Materials")
        print("3. Check Compatibility")
        print("4. Check Strong Bonds")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_material()
        elif choice == "2":
            show_selected()
        elif choice == "3":
            check_compatibility()
        elif choice == "4":
            check_strong_bonds()
        elif choice == "5":
            print("Exiting System...")
            break
        else:
            print("Invalid choice!\n")


menu()