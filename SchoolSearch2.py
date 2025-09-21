import time
import json
import xml.etree.ElementTree as ET
import sys
import os

class Student:
    def __init__(self, line):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 7:
            raise ValueError("Invalid student record format")
        self.last_name = parts[0]
        self.first_name = parts[1]
        self.grade = int(parts[2])
        self.classroom = int(parts[3])
        self.bus = int(parts[4])
        self.teacher_last = parts[5]
        self.teacher_first = parts[6]

    def __repr__(self):
        return f"{self.last_name}, {self.first_name}, Grade {self.grade}, Class {self.classroom}, Bus {self.bus}, Teacher {self.teacher_first} {self.teacher_last}"

class StudentNormalized:
    def __init__(self, line):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 5:
            raise ValueError("Invalid student record format in list.txt")
        self.last_name = parts[0]
        self.first_name = parts[1]
        self.grade = int(parts[2])
        self.classroom = int(parts[3])
        self.bus = int(parts[4])

    def __repr__(self):
        return f"{self.last_name}, {self.first_name}, Grade {self.grade}, Class {self.classroom}, Bus {self.bus}"

class Teacher:
    def __init__(self, line):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            raise ValueError("Invalid teacher record format in teachers.txt")
        self.last_name = parts[0]
        self.first_name = parts[1]
        self.classroom = int(parts[2])

    def __repr__(self):
        return f"Teacher: {self.first_name} {self.last_name}, Classroom: {self.classroom}"

#Завантаження даних

def load_students(filename="students.txt"):
    students = []
    try:
        with open(filename, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    students.append(Student(line))
    except (FileNotFoundError, ValueError) as e:
        print("Error: students.txt missing or invalid format")
        sys.exit(1)
    return students

def load_normalized_data():
    students_norm = []
    teachers = []
    teachers_map = {}
    try:
        with open("list.txt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    students_norm.append(StudentNormalized(line))
        with open("teachers.txt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    teacher = Teacher(line)
                    teachers.append(teacher)
                    teachers_map.setdefault(teacher.classroom, []).append(teacher)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    return students_norm, teachers, teachers_map

# Декоратори

def timed_search(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        if result:
            for r in result:
                print(r)
        print(f"{int((end - start) * 1000)}ms")
        return result
    return wrapper

def timed_action(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{int((end - start) * 1000)}ms")
        return result
    return wrapper

# ПОШУК (старий і новий функціонал)

@timed_search
def search_student(students, teachers_map, last_name):
    result = []
    for s in students:
        if s.last_name == last_name:
            teachers_list = teachers_map.get(s.classroom, [])
            teachers_str = "N/A"
            if teachers_list:
                teachers_str = f"{teachers_list[0].first_name} {teachers_list[0].last_name}"
            result.append(f"{s.last_name}, {s.first_name}, Grade: {s.grade}, Class: {s.classroom}, Teacher: {teachers_str}")
    return result

@timed_search
def search_student_bus(students, _, last_name):
    return [f"{s.last_name}, {s.first_name}, Bus: {s.bus}" for s in students if s.last_name == last_name]

@timed_search
def search_teacher(students, teachers_map, last_name):
    classroom_numbers = {t.classroom for t_list in teachers_map.values() for t in t_list if t.last_name == last_name}
    result = []
    for s in students:
        if s.classroom in classroom_numbers:
            result.append(f"{s.last_name}, {s.first_name}")
    return result

@timed_search
def search_classroom(students, _, number):
    return [f"{s.last_name}, {s.first_name}" for s in students if s.classroom == number]

@timed_search
def search_bus(students, _, number):
    return [f"{s.last_name}, {s.first_name}, Grade: {s.grade}, Class: {s.classroom}" for s in students if s.bus == number]

@timed_search
def search_by_grade(students, _, grade):
    return [f"{s.last_name}, {s.first_name}, Grade: {s.grade}" for s in students if s.grade == grade]

@timed_search
def search_classroom_teacher(_, teachers_map, classroom):
    teachers = teachers_map.get(classroom, [])
    return [f"{t.last_name}, {t.first_name}" for t in teachers]

@timed_search
def search_grade_teachers(students, teachers_map, grade):
    result = set()
    for s in students:
        if s.grade == grade:
            teachers = teachers_map.get(s.classroom, [])
            for t in teachers:
                result.add(f"{t.last_name}, {t.first_name}")
    return sorted(list(result))

# Модифікація даних

@timed_action
def delete_student(students, last_name):
    before = len(students)
    students[:] = [s for s in students if s.last_name != last_name]
    after = len(students)
    print(f"Deleted {before - after} record(s).")
    return students

@timed_action
def update_student(students, last_name, field, new_value):
    updated = 0
    for s in students:
        if s.last_name == last_name:
            if field == "grade":
                s.grade = int(new_value)
            elif field == "classroom":
                s.classroom = int(new_value)
            elif field == "bus":
                s.bus = int(new_value)
            else:
                print("Unknown field.")
                return students
            updated += 1
    print(f"Updated {updated} record(s).")
    return students

@timed_action
def add_student(students_norm, teachers, teachers_map, last_name, first_name, grade, classroom, bus, teacher_last, teacher_first):
    # Додаємо нового студента
    line_student = f"{last_name},{first_name},{grade},{classroom},{bus}"
    new_student = StudentNormalized(line_student)
    students_norm.append(new_student)
    
    # Перевіряємо, чи існує викладач для цього класу
    teacher_exists = False
    if teachers_map.get(int(classroom)):
        for t in teachers_map.get(int(classroom)):
            if t.last_name == teacher_last and t.first_name == teacher_first:
                teacher_exists = True
                break
    
    # Якщо викладача немає, додаємо його до списку
    if not teacher_exists:
        line_teacher = f"{teacher_last},{teacher_first},{classroom}"
        new_teacher = Teacher(line_teacher)
        teachers.append(new_teacher)
        teachers_map.setdefault(new_teacher.classroom, []).append(new_teacher)
        save_teachers(teachers) # Зберігаємо оновлений список викладачів
    
    save_students(students_norm) # Зберігаємо оновлений список студентів
    print(f"Added student: {last_name}, {first_name} with teacher: {teacher_last}, {teacher_first}")
    return students_norm

@timed_action
def show_counts(students, teachers):
    student_set = {(s.last_name, s.first_name) for s in students}
    student_count = len(student_set)
    teacher_set = {(t.last_name, t.first_name) for t in teachers}
    teacher_count = len(teacher_set)
    print(f"Total unique students: {student_count}")
    print(f"Total unique teachers: {teacher_count}")
    
@timed_action
def save_students(students, filename="list.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for s in students:
            line = f"{s.last_name},{s.first_name},{s.grade},{s.classroom},{s.bus}\n"
            f.write(line)
    print(f"Changes saved to {filename}")

@timed_action
def save_teachers(teachers, filename="teachers.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for t in teachers:
            line = f"{t.last_name},{t.first_name},{t.classroom}\n"
            f.write(line)

@timed_action
def save_json(students, teachers, filename="students.json"):
    data = {
        "students": [s.__dict__ for s in students],
        "teachers": [t.__dict__ for t in teachers]
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Changes saved to {filename}")

@timed_action
def save_xml(students, teachers, filename="students.xml"):
    root = ET.Element("school")
    sroot = ET.SubElement(root, "students")
    for s in students:
        se = ET.SubElement(sroot, "student")
        for k, v in s.__dict__.items():
            ET.SubElement(se, k).text = str(v)
    troot = ET.SubElement(root, "teachers")
    for t in teachers:
        te = ET.SubElement(troot, "teacher")
        for k, v in t.__dict__.items():
            ET.SubElement(te, k).text = str(v)
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Changes saved to {filename}")

# Головна програма 

def main():
    if os.path.exists("list.txt") and os.path.exists("teachers.txt"):
        students, teachers, teachers_map = load_normalized_data()
        mode = "normalized"
    else:
        students = load_students()
        teachers = []
        teachers_map = {}
        for s in students:
            teacher = Teacher(f"{s.teacher_last},{s.teacher_first},{s.classroom}")
            if s.classroom not in teachers_map:
                teachers_map[s.classroom] = []
            teachers_map[s.classroom].append(teacher)
            teachers.append(teacher)
        mode = "original"
        print("Note: Using original students.txt file. Data is not normalized.")

    print("Schoolsearch system ready. Type a command (S, SB, T, C, CT, B, G, GT, D, U, A, COUNTS, SAVE JSON, SAVE XML, Q).")

    while True:
        cmd = input(">>> ").strip()
        if not cmd:
            continue
        
        parts = cmd.split()
        command = parts[0]
        args = parts[1:]

        if command == "Q":
            print("Quit bye!")
            break
        elif command == "S":
            if len(args) == 1:
                search_student(students, teachers_map, args[0])
            elif len(args) == 2 and args[1] == "B":
                search_student_bus(students, teachers_map, args[0])
            else:
                print("Incorrect Student command. Use: S <lastname> [B]")
        elif command == "T":
            if len(args) == 1:
                search_teacher(students, teachers_map, args[0])
            else:
                print("Usage: T <lastname>")
        elif command == "C":
            try:
                if len(args) == 1:
                    search_classroom(students, teachers_map, int(args[0]))
                elif len(args) == 2 and args[1] == "T":
                    search_classroom_teacher(students, teachers_map, int(args[0]))
                else:
                    print("Usage: C <number> [T]")
            except ValueError:
                print("Classroom number must be an integer.")
        elif command == "B":
            try:
                if len(args) == 1:
                    search_bus(students, teachers_map, int(args[0]))
                else:
                    print("Usage: B <number>")
            except ValueError:
                print("Bus number must be an integer.")
        elif command == "G":
            try:
                if len(args) == 1:
                    search_by_grade(students, teachers_map, int(args[0]))
                elif len(args) == 2 and args[1] == "T":
                    search_grade_teachers(students, teachers_map, int(args[0]))
                else:
                    print("Usage: G <number> [T]")
            except ValueError:
                print("Grade must be an integer.")
        elif command == "D":
            if len(args) == 1:
                students = delete_student(students, args[0])
                if mode == "normalized":
                    save_students(students)
                else:
                    print("Warning: Cannot save changes in original mode.")
            else:
                print("Usage: D <lastname>")
        elif command == "U":
            if len(args) >= 3:
                last_name, field, new_value = args[0], args[1], " ".join(args[2:])
                students = update_student(students, last_name, field, new_value)
                if mode == "normalized":
                    save_students(students)
                else:
                    print("Warning: Cannot save changes in original mode.")
            else:
                print("Usage: U <lastname> <field> <new_value>")
        elif command == "A":
            if len(args) == 7:
                try:
                    students = add_student(students, teachers, teachers_map, *args)
                except ValueError:
                    print("Invalid input. Check that grade, classroom, and bus are integers.")
            else:
                print("Usage: A <Last name> <Name> <Grade> <Classrom> <Bus> <Teacher Last name> <Teacher Name>")
        elif command == "COUNTS":
            show_counts(students, teachers)
        elif command == "SAVE":
            if len(args) == 1 and args[0] == "JSON":
                save_json(students, teachers)
            elif len(args) == 1 and args[0] == "XML":
                save_xml(students, teachers)
            else:
                print("Usage: SAVE JSON or SAVE XML")
        else:
            print("Unknown command. Use S, SB, T, C, CT, B, G, GT, D, U, A, COUNTS, SAVE JSON, SAVE XML, Q.")

if __name__ == "__main__":
    main()