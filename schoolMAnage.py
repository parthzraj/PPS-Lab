# 1. Add Student
# 2. Update Marks
# 3. Delete Student
# 4. Search Student
# 5. Display Topper
# 6. Sort by Marks
# 7. Exit




students = []


def add_student():
    try:
        student_id = int(input("Enter Student ID: "))
        
        
        for student in students:
            if student["id"] == student_id:
                print("Student with this ID already exists!")
                return
        
        name = input("Enter Student Name: ")
        student_class = input("Enter Class: ")
        
        marks = {}
        subjects_count = int(input("How many subjects? "))
        
        for _ in range(subjects_count):
            subject = input("Enter Subject Name: ")
            score = float(input(f"Enter marks for {subject}: "))
            marks[subject] = score
        
        new_student = {
            "id": student_id,
            "name": name,
            "class": student_class,
            "marks": marks
        }
        
        students.append(new_student)
        print("Student added successfully!\n")
    
    except ValueError:
        print("Invalid input! Please enter correct data types.\n")



def display_students():
    if not students:
        print("No student records found.\n")
        return
    
    for student in students:
        print("ID:", student["id"])
        print("Name:", student["name"])
        print("Class:", student["class"])
        print("Marks:", student["marks"])
        print("-" * 30)



def search_student():
    search_id = int(input("Enter Student ID to search: "))
    
    for student in students:
        if student["id"] == search_id:
            print("Student Found:")
            print(student)
            return
    
    print("Student not found.\n")



def update_marks():
    search_id = int(input("Enter Student ID to update: "))
    
    for student in students:
        if student["id"] == search_id:
            subject = input("Enter Subject to update: ")
            
            if subject in student["marks"]:
                new_marks = float(input("Enter new marks: "))
                student["marks"][subject] = new_marks
                print("Marks updated successfully!\n")
            else:
                print("Subject not found.\n")
            return
    
    print("Student not found.\n")



def delete_student():
    search_id = int(input("Enter Student ID to delete: "))
    
    for student in students:
        if student["id"] == search_id:
            students.remove(student)
            print("Student deleted successfully!\n")
            return
    
    print(" Student not found.\n")



def calculate_average(student):
    total = sum(student["marks"].values())
    return total / len(student["marks"])



def display_topper():
    if not students:
        print("No student records found.\n")
        return
    
    topper = students[0]
    highest_avg = calculate_average(topper)
    
    for student in students:
        avg = calculate_average(student)
        if avg > highest_avg:
            highest_avg = avg
            topper = student
    
    print(" Topper Details:")
    print("Name:", topper["name"])
    print("Average Marks:", highest_avg)
    print("-" * 30)


def sort_students():
    if not students:
        print("No student records found.\n")
        return
    
    sorted_list = sorted(students, key=calculate_average, reverse=True)
    
    print(" Students Ranked by Average Marks:")
    for student in sorted_list:
        print(student["name"], "- Average:", calculate_average(student))
    print("-" * 30)



def main():
    while True:
        print("\n====== Student Management System ======")
        print("1. Add Student")
        print("2. Display All Students")
        print("3. Search Student")
        print("4. Update Marks")
        print("5. Delete Student")
        print("6. Display Topper")
        print("7. Sort Students by Average")
        print("8. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_student()
        elif choice == "2":
            display_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            update_marks()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            display_topper()
        elif choice == "7":
            sort_students()
        elif choice == "8":
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.\n")



main()
