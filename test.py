students = []
try:
        student_id = int(input("Enter Student ID: "))
        
        
        for student in students:
            if student["id"] == student_id:
                print("Student with this ID already exists!")
        
        name = input("Enter Student Name: ")
        student_class = input("Enter Class: ")
        
        marks = {}
        subjects_count = int(input("How many subjects? "))
        
        for _ in range(subjects_count):
            subject = input("Enter Subject Name: ")
            score = float(input(f"Enter marks for {subject}: "))
            marks[subject] = score
        
        print(marks)
        
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

