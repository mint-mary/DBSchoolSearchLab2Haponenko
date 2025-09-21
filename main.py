import time
import json
import xml.etree.ElementTree as ET
import sys

class Student:
    def __init__(self, line):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 5:
            raise ValueError("Invalid student record format")
        self.last_name = parts[0]
        self.first_name = parts[1]
        self.grade = int(parts[2])
        self.classroom = int(parts[3])
        self.bus = int(parts[4])

    def __repr__(self):
        return f"{self.last_name}, {self.first_name}, {self.grade}, {self.classroom}, {self.bus}"

class Teacher:
    def __init__(self, line):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            raise ValueError("Invalid teacher record format")
        self.last_name = parts[0]
        self.first_name = parts[1]
        self.classroom = int(parts[2])

    def __repr__(self):
        return f"{self.last_name}, {self.first_name}, {self.classroom}"

# завантаження учнів
def load_students(filename="list.txt"):
    students = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                students.append(Student(line))
    return students

# завантаження вчителів
def load_teachers(filename="teachers.txt"):
    teachers = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                teachers.append(Teacher(line))
    return teachers

# словник classroom → [вчителі]
def map_class_teachers(teachers):
    mapping = {}
    for t in teachers:
        mapping.setdefault(t.classroom, []).append(t)
    return mapping

# Декоратори для замірів часу
def timed_search(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
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

# --- ПОШУКИ ---

@timed_search
def search_student(students, teachers_map, last_name):
    result = []
    for s in students:
        if s.last_name == last_name:
            ts = teachers_map.get(s.classroom, [])
            for t in ts:
                result.append(f"{s.last_name}, {s.first_name}, {s.grade}, {s.classroom}, {t.last_name}, {t.first_name}")
    return result

@timed_search
def search_student_bus(students, _, last_name):
    return [f"{s.last_name}, {s.first_name}, {s.bus}" for s in students if s.last_name == last_name]

@timed_search
def search_teacher(students, teachers_map, last_name):
    result = []
    for s in students:
        ts = teachers_map.get(s.classroom, [])
        for t in ts:
            if t.last_name == last_name:
                result.append(f"{s.last_name}, {s.first_name}")
    return result

@timed_search
def search_classroom(students, _, number):
    return [f"{s.last_name}, {s.first_name}" for s in students if s.classroom == number]

@timed_search
def search_bus(students, _, number):
    return [f"{s.last_name}, {s.first_name}, {s.grade}, {s.classroom}" for s in students if s.bus == number]

# --- НОВІ ПОШУКИ ---

@timed_search
def search_by_grade(students, _, grade):
    return [f"{s.last_name}, {s.first_name}, {s.grade}, {s.classroom}, {s.bus}" for s in students if s.grade == grade]

@timed_search
def search_classroom_teacher(_, teachers_map, classroom):
    ts = teachers_map.get(classroom, [])
    return [f"{t.last_name}, {t.first_name}" for t in ts]

@timed_search
def search_grade_teachers(students, teachers_map, grade):
    result = set()
    for s in students:
        if s.grade == grade:
            ts = teachers_map.get(s.classroom, [])
            for t in ts:
                result.add(f"{t.last_name}, {t.first_name}")
    return sorted(result)

# --- Збереження ---

@timed_action
def save_json(students, teachers, filename="students.json"):
    data = [s.__dict__ for s in students]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"students": data, "teachers": [t.__dict__ for t in teachers]}, f, indent=4)

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

# --- Головна програма ---

def main():
    students = load_students("list.txt")
    teachers = load_teachers("teachers.txt")
    teachers_map = map_class_teachers(teachers)

    print("Schoolsearch system ready.")

    while True:
        cmd = input(">>> ").strip()
        if not cmd:
            continue
        if cmd.startswith("Q"):
            print("Quit bye!")
            break
        elif cmd.startswith("S "):
            parts = cmd.split()
            if len(parts) == 2:
                search_student(students, teachers_map, parts[1])
            elif len(parts) == 3 and parts[2] == "B":
                search_student_bus(students, teachers_map, parts[1])
        elif cmd.startswith("T "):
            _, lname = cmd.split(maxsplit=1)
            search_teacher(students, teachers_map, lname)
        elif cmd.startswith("C "):
            parts = cmd.split()
            if len(parts) == 2:
                search_classroom(students, teachers_map, int(parts[1]))
            elif len(parts) == 3 and parts[2] == "T":
                search_classroom_teacher(students, teachers_map, int(parts[1]))
        elif cmd.startswith("B "):
            _, num = cmd.split(maxsplit=1)
            search_bus(students, teachers_map, int(num))
        elif cmd.startswith("G "):
            parts = cmd.split()
            if len(parts) == 2:
                search_by_grade(students, teachers_map, int(parts[1]))
            elif len(parts) == 3 and parts[2] == "T":
                search_grade_teachers(students, teachers_map, int(parts[1]))
        elif cmd == "SAVE JSON":
            save_json(students, teachers)
        elif cmd == "SAVE XML":
            save_xml(students, teachers)
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
