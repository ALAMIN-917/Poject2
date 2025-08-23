def delete_semester_result(con):
    """Delete a semester result for a student (by session, roll, subject, and semester)."""
    session = askStr("Session: ")
    roll = askInt("Student Roll No: ")
    cur = con.cursor()
    cur.execute("SELECT DISTINCT subject FROM attendance WHERE roll_no=?", (roll,))
    subjects = [row[0] for row in cur.fetchall()]
    if not subjects:
        print("No subjects found for this student.")
        cur.close()
        pauseLine()
        return
    print("Subjects for this student:")
    for idx, subj in enumerate(subjects, 1):
        print(f"{idx}) {subj}")
    subj_choice = askInt("Select subject number to delete result for: ")
    if subj_choice < 1 or subj_choice > len(subjects):
        print("Invalid subject selection.")
        cur.close()
        pauseLine()
        return
    subject = subjects[subj_choice - 1]
    semester = askStr("Semester: ")
    try:
        cur.execute(
            "DELETE FROM session_semester_result WHERE session=? AND roll_no=? AND semester=?",
            (session, roll, semester + f" ({subject})")
        )
        con.commit()
        print(f"Result for subject '{subject}' deleted for student {roll} in semester '{semester}'.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()
        pauseLine()
def show_semester_result(con):
    """Display all students' semester results for a session."""
    session = askStr("Enter session to view results for: ")
    cur = con.cursor()
    cur.execute("""
        SELECT s.roll_no, s.name, ssr.semester, ssr.result
        FROM session_semester_result ssr
        JOIN student s ON s.roll_no = ssr.roll_no
        WHERE ssr.session = ?
        ORDER BY s.roll_no, ssr.semester
    """, (session,))
    printRowLine()
    print(f"{'Roll':<8}{'Name':<22}{'Semester':<18}{'Result':<14}")
    for row in cur.fetchall():
        print(f"{row[0]:<8}{row[1]:<22}{row[2]:<18}{row[3]:<14}")
    cur.close()
    pauseLine()
def show_all_teacher(con):
    """Display all teachers in the database."""
    print("------------------------------All Teachers Data----------------------")
    cur = con.cursor()
    cur.execute("SELECT id, name, subject, dept, exam_control_power FROM teacher ORDER BY id")
    printRowLine()
    print(f"{'ID':<6}{'Name':<22}{'Subject':<18}{'Dept':<12}{'Exam Controlller':<20}")
    for row in cur.fetchall():
        print(f"{row[0]:<6}{row[1]:<22}{row[2]:<18}{row[3]:<12}{row[4]:<20}")
    cur.close()
    pauseLine()
def show_all_student(con):
    """Display all students in the database."""
    cur = con.cursor()
    cur.execute("SELECT roll_no, reg_no, name, phone, email, dept, session FROM student ORDER BY roll_no")
    printRowLine()
    print(f"{'Roll':<8}{'':<6}{'Reg':<16}{'Name':<22}{'Phone':<14}{'Email':<24}{'Dept':<10}{'Session':<12}")
    for row in cur.fetchall():
        # row[0]=roll, row[1]=reg, row[2]=name, row[3]=phone, row[4]=email, row[5]=dept, row[6]=session
        print(f"{row[0]:<8}{'':<6}{row[1]:<16}{row[2]:<22}{row[3]:<14}{row[4]:<24}{row[5]:<10}{row[6]:<12}")
    cur.close()
    pauseLine()
def initialize_db(con):
    """Create required tables if they do not exist."""
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_name TEXT NOT NULL,
        credits INTEGER NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS student (
        roll_no INTEGER PRIMARY KEY,
        reg_no TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        dept TEXT,
        session TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS c_gpa (
        roll_no INTEGER PRIMARY KEY,
        reg_no TEXT NOT NULL,
        name TEXT NOT NULL,
        c_gpa REAL DEFAULT 0.0
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS teacher (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        dept TEXT,
        password TEXT NOT NULL,
        exam_control_power TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS session_semester_result (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session TEXT NOT NULL,
        roll_no INTEGER NOT NULL,
        semester TEXT NOT NULL,
        result TEXT NOT NULL,
        controller_id INTEGER NOT NULL,
        UNIQUE(session, roll_no, semester),
        FOREIGN KEY (roll_no) REFERENCES student(roll_no),
        FOREIGN KEY (controller_id) REFERENCES teacher(id)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
        roll_no INTEGER,
        reg_no TEXT,
        name TEXT,
        subject TEXT,
        attendance INTEGER DEFAULT 0,
        PRIMARY KEY (roll_no, subject)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS mid_mark (
        roll_no INTEGER,
        reg_no TEXT,
        name TEXT,
        subject TEXT,
        mid1 INTEGER DEFAULT 0,
        mid2 INTEGER DEFAULT 0,
        mid3 INTEGER DEFAULT 0,
        PRIMARY KEY (roll_no, subject)
    )''')
    con.commit()
    cur.close()

import sqlite3
import sys

# ====== DB CONFIG - change for your SQLite3 ======
DB_PATH = "college_db.sqlite3"  # Path to your SQLite database file
# ===============================================

def connectDB():
    """Establish a connection to the SQLite database."""
    try:
        con = sqlite3.connect(DB_PATH)
        return con
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite3: {e}")
        sys.exit(1)

def pauseLine():
    """Pause execution until the user presses ENTER."""
    input("\nPress ENTER to continue...")

def askInt(prompt):
    """Prompt the user for an integer input."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid. Try again: ")

def askStr(prompt):
    """Prompt the user for a string input."""
    return input(prompt)

def printRowLine(w=80):
    """Print a horizontal line for UI separation."""
    print('-' * w)

def show_total_cgpa_for_semester(con):
    """Show total CGPA for each student in a given session and semester, averaging all subjects' CGPA for that semester."""
    session = askStr("Enter session: ")
    semester = askStr("Enter semester: ")
    cur = con.cursor()
    # Get all students in this session who have results in this semester
    cur.execute("SELECT DISTINCT s.roll_no, s.name FROM student s JOIN session_semester_result ssr ON s.roll_no = ssr.roll_no WHERE s.session = ? AND ssr.semester LIKE ? ORDER BY s.roll_no", (session, semester + ' (%',))
    students = cur.fetchall()
    if not students:
        print("No students found for this session and semester.")
        cur.close()
        pauseLine()
        return
    printRowLine()
    print(f"Total CGPA for all students in session '{session}', semester '{semester}'")
    print(f"{'Roll':<8}{'Name':<22}{'CGPA':<8}")
    for roll, name in students:
        # Get all subjects for this student in this session and semester
        cur.execute("SELECT semester, result FROM session_semester_result WHERE roll_no=? AND session=? AND semester LIKE ?", (roll, session, semester + ' (%',))
        subject_results = cur.fetchall()
        total_points = 0
        subject_count = 0
        for sem, result in subject_results:
            # Extract subject from semester string
            if '(' in sem and sem.endswith(')'):
                subject = sem[sem.find('(')+1:-1]
            else:
                subject = sem
            # Get internal marks
            cur.execute("SELECT COALESCE(a.attendance,0), COALESCE(m.mid1,0), COALESCE(m.mid2,0), COALESCE(m.mid3,0) FROM attendance a LEFT JOIN mid_mark m ON m.roll_no=a.roll_no AND m.subject=a.subject WHERE a.roll_no=? AND a.subject=?", (roll, subject))
            row = cur.fetchone()
            total_internal = sum(row) if row else 0
            try:
                semester_result = float(result)
                total_marks = (total_internal / 40.0 * 40.0) + (semester_result / 60.0 * 60.0)
                if total_marks > 100:
                    total_marks = 100
                cgpa = (total_marks / 100.0) * 4.0
                total_points += cgpa
                subject_count += 1
            except ValueError:
                continue
        avg_cgpa = round(total_points / subject_count, 2) if subject_count > 0 else 'N/A'
        print(f"{roll:<8}{name:<22}{avg_cgpa:<8}")
    cur.close()
    pauseLine()

def calculate_and_show_course_cgpa(con):
    """Calculate and display CGPA for all students who took a given course in a given semester."""
    course = askStr("Enter course (subject) name: ")
    semester = askStr("Enter semester: ")
    cur = con.cursor()
    # Get all students who took this course in this semester
    cur.execute("SELECT DISTINCT s.roll_no, s.name FROM student s JOIN attendance a ON s.roll_no = a.roll_no WHERE a.subject=?", (course,))
    students = cur.fetchall()
    if not students:
        print("No students found for this course.")
        cur.close()
        pauseLine()
        return
    # Get course credits
    cur.execute("SELECT credits FROM subject WHERE sub_name=?", (course,))
    row = cur.fetchone()
    credits = row[0] if row else 3  # Default to 3 if not found
    printRowLine()
    print(f"CGPA for all students in course '{course}' (Semester: {semester})")
    print(f"{'Roll':<8}{'Name':<22}{'CGPA':<8}")
    for roll, name in students:
        # Internal marks
        cur.execute("SELECT COALESCE(a.attendance,0), COALESCE(m.mid1,0), COALESCE(m.mid2,0), COALESCE(m.mid3,0) FROM attendance a LEFT JOIN mid_mark m ON m.roll_no=a.roll_no AND m.subject=a.subject WHERE a.roll_no=? AND a.subject=?", (roll, course))
        row = cur.fetchone()
        total_internal = sum(row) if row else 0
        # Semester result
        cur.execute("SELECT result FROM session_semester_result WHERE roll_no=? AND semester=?", (roll, semester + f" ({course})"))
        sem_row = cur.fetchone()
        if not sem_row:
            cgpa = 'N/A'
        else:
            try:
                semester_result = float(sem_row[0])
                # Calculate total marks (internal out of 40, semester out of 60)
                total_marks = (total_internal / 40.0 * 40.0) + (semester_result / 60.0 * 60.0)
                if total_marks > 100:
                    total_marks = 100
                # Convert to grade point (out of 4.0)
                cgpa = round((total_marks / 100.0) * 4.0, 2)
            except ValueError:
                cgpa = 'N/A'
        print(f"{roll:<8}{name:<22}{cgpa:<8}")
    cur.close()
    pauseLine()
    """Print a horizontal line for UI separation."""

    print('-' * w)

def calculate_and_show_course_cgpa(con):
    """Calculate and display CGPA for all students who took a given course in a given semester."""
    course = askStr("Enter course (subject) name: ")
    semester = askStr("Enter semester: ")
    cur = con.cursor()
    # Get all students who took this course in this semester
    cur.execute("SELECT DISTINCT s.roll_no, s.name FROM student s JOIN attendance a ON s.roll_no = a.roll_no WHERE a.subject=?", (course,))
    students = cur.fetchall()
    if not students:
        print("No students found for this course.")
        cur.close()
        pauseLine()
        return
    # Get course credits
    cur.execute("SELECT credits FROM subject WHERE sub_name=?", (course,))
    row = cur.fetchone()
    credits = row[0] if row else 3  # Default to 3 if not found
    printRowLine()
    print(f"CGPA for all students in course '{course}' (Semester: {semester})")
    print(f"{'Roll':<8}{'Name':<22}{'CGPA':<8}")
    for roll, name in students:
        # Internal marks
        cur.execute("SELECT COALESCE(a.attendance,0), COALESCE(m.mid1,0), COALESCE(m.mid2,0), COALESCE(m.mid3,0) FROM attendance a LEFT JOIN mid_mark m ON m.roll_no=a.roll_no AND m.subject=a.subject WHERE a.roll_no=? AND a.subject=?", (roll, course))
        row = cur.fetchone()
        total_internal = sum(row) if row else 0
        # Semester result
        cur.execute("SELECT result FROM session_semester_result WHERE roll_no=? AND semester=?", (roll, semester + f" ({course})"))
        sem_row = cur.fetchone()
        if not sem_row:
            cgpa = 'N/A'
        else:
            try:
                semester_result = float(sem_row[0])
                # Calculate total marks (internal out of 40, semester out of 60)
                total_marks = (total_internal / 40.0 * 40.0) + (semester_result / 60.0 * 60.0)
                if total_marks > 100:
                    total_marks = 100
                # Convert to grade point (out of 4.0)
                cgpa = round((total_marks / 100.0) * 4.0, 2)
            except ValueError:
                cgpa = 'N/A'
        print(f"{roll:<8}{name:<22}{cgpa:<8}")
    cur.close()
    pauseLine()

# ------- ADMIN PANEL -------
def adminAddStudent(con):
    """Add a new student to the database."""
    roll = askInt("Roll No: ")
    reg = askStr("Reg No: ")
    name = askStr("Name: ")
    phone = askStr("Phone: ")
    email = askStr("Email: ")
    dept = askStr("Dept: ")
    session = askStr("Session: ")
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO student(roll_no,reg_no,name,phone,email,dept,session) VALUES(?,?,?,?,?,?,?)",
            (roll, reg, name, phone, email, dept, session)
        )
        cur.execute(
            "INSERT INTO c_gpa(roll_no, reg_no, name, c_gpa) VALUES(?,?,?,0.0)",
            (roll, reg, name)
        )
        con.commit()
        print("Student added.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def adminUpdateStudent(con):
    """Update student information."""
    roll = askInt("Roll No to update: ")
    phone = askStr("New phone (or blank to skip): ")
    email = askStr("New email (or blank to skip): ")
    dept  = askStr("New dept (or blank to skip): ")
    cur = con.cursor()
    try:
        if phone:
            cur.execute("UPDATE student SET phone=? WHERE roll_no=?", (phone, roll))
        if email:
            cur.execute("UPDATE student SET email=? WHERE roll_no=?", (email, roll))
        if dept:
            cur.execute("UPDATE student SET dept=? WHERE roll_no=?", (dept, roll))
        con.commit()
        print("Student updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def adminDeleteStudent(con):
    """Delete a student from the database."""
    roll = askInt("Roll No to delete: ")
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM student WHERE roll_no=?", (roll,))
        con.commit()
        print("Deleted (if existed). Related rows cascade removed.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def adminAddTeacher(con):
    """Add a new teacher to the database."""
    id = askInt("Teacher ID: ")
    name = askStr("Name: ")
    subject = askStr("Subject: ")
    dept = askStr("Dept: ")
    password = askStr("Password: ")
    exam_control_power = askStr("Exam Control Power (session, comma separated if multiple, blank if none): ")
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO teacher(id,name,subject,dept,password,exam_control_power) VALUES(?,?,?,?,?,?)",
            (id, name, subject, dept, password, exam_control_power)
        )
        con.commit()
        print("Teacher added.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def update_session_semester_result(con, controller_id):
    """Allow exam controllers to update semester results for students in their session (no duplicates)."""
    # Get controller's allowed sessions
    cur = con.cursor()
    cur.execute("SELECT exam_control_power FROM teacher WHERE id=?", (controller_id,))
    row = cur.fetchone()
    if not row or not row[0]:
        print("You do not have exam control power for any session.")
        cur.close()
        pauseLine()
        return
    allowed_sessions = [s.strip() for s in row[0].split(',') if s.strip()]
    session = askStr("Session to set result for: ")
    if session not in allowed_sessions:
        print("You are not authorized to set results for this session.")
        cur.close()
        pauseLine()
        return
    roll = askInt("Student Roll No: ")
    # Get all subjects for this student
    cur.execute("SELECT DISTINCT subject FROM attendance WHERE roll_no=?", (roll,))
    subjects = [row[0] for row in cur.fetchall()]
    if not subjects:
        print("No subjects found for this student.")
        cur.close()
        pauseLine()
        return
    print("Subjects for this student:")
    for idx, subj in enumerate(subjects, 1):
        print(f"{idx}) {subj}")
    subj_choice = askInt("Select subject number to update result for: ")
    if subj_choice < 1 or subj_choice > len(subjects):
        print("Invalid subject selection.")
        cur.close()
        pauseLine()
        return
    subject = subjects[subj_choice - 1]
    semester = askStr("Semester: ")
    result = askStr("Result: ")
    # Remove any existing result for this student/session/semester/subject
    try:
        cur.execute(
            "DELETE FROM session_semester_result WHERE session=? AND roll_no=? AND semester=?",
            (session, roll, semester + f" ({subject})")
        )
        cur.execute(
            "INSERT INTO session_semester_result(session, roll_no, semester, result, controller_id) VALUES(?,?,?,?,?)",
            (session, roll, semester + f" ({subject})", result, controller_id)
        )
        con.commit()
        print(f"Result for subject '{subject}' updated for student {roll} in semester '{semester}'.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()
        pauseLine()

def adminUpdateTeacher(con):
    """Update teacher information."""
    id = askInt("Teacher ID to update: ")
    name = askStr("New name (blank skip): ")
    subject = askStr("New subject (blank skip): ")
    dept = askStr("New dept (blank skip): ")
    cur = con.cursor()
    try:
        if name:
            cur.execute("UPDATE teacher SET name=? WHERE id=?", (name, id))
        if subject:
            cur.execute("UPDATE teacher SET subject=? WHERE id=?", (subject, id))
        if dept:
            cur.execute("UPDATE teacher SET dept=? WHERE id=?", (dept, id))
        con.commit()
        print("Teacher updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def adminDeleteTeacher(con):
    """Delete a teacher from the database."""
    id = askInt("Teacher ID to delete: ")
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM teacher WHERE id=?", (id,))
        con.commit()
        print("Deleted (if existed).")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()



def show_sessionwise_cgpa(con, roll):
    """Display sessionwise CGPA for a student, calculated automatically from results."""
    cur = con.cursor()
    cur.execute("SELECT DISTINCT session FROM session_semester_result WHERE roll_no=? ORDER BY session", (roll,))
    sessions = [row[0] for row in cur.fetchall()]
    if not sessions:
        print("No session results found for this student.")
        cur.close()
        return
    for session in sessions:
        cur.execute("SELECT DISTINCT semester FROM session_semester_result WHERE roll_no=? AND session=? ORDER BY semester", (roll, session))
        semesters = [row[0] for row in cur.fetchall()]
        print(f"Session: {session}")
        for semester in semesters:
            cur.execute("SELECT semester, result FROM session_semester_result WHERE roll_no=? AND session=? AND semester=?", (roll, session, semester))
            subject_results = cur.fetchall()
            if not subject_results:
                continue
            total_points = 0
            subject_count = 0
            for sem, result in subject_results:
                # Extract subject from semester string
                if '(' in sem and sem.endswith(')'):
                    subject = sem[sem.find('(')+1:-1]
                else:
                    subject = sem
                # Get internal marks
                cur.execute("""
                    SELECT COALESCE(a.attendance,0), COALESCE(m.mid1,0), COALESCE(m.mid2,0), COALESCE(m.mid3,0)
                    FROM attendance a
                    LEFT JOIN mid_mark m ON m.roll_no=a.roll_no AND m.subject=a.subject
                    WHERE a.roll_no=? AND a.subject=?
                """, (roll, subject))
                row = cur.fetchone()
                total_internal = sum(row) if row else 0
                try:
                    semester_result = float(result)
                except ValueError:
                    continue
                total_marks = (total_internal / 40.0 * 40.0) + (semester_result / 60.0 * 60.0)
                if total_marks > 100:
                    total_marks = 100
                cgpa = (total_marks / 100.0) * 4.0
                total_points += cgpa
                subject_count += 1
            if subject_count > 0:
                avg_cgpa = round(total_points / subject_count, 2)
                print(f"  Semester: {semester} | CGPA: {avg_cgpa}")
        print()
    cur.close()

def adminAddSubject(con):
    """Admin adds a subject to the subject table."""
    sub_name = askStr("Subject name: ")
    credits = askInt("Credits: ")
    cur = connectDB().cursor()
    try:
        cur.execute("INSERT INTO subject(sub_name, credits) VALUES (?, ?)", (sub_name, credits))
        cur.connection.commit()
        print("Subject added.")
    except Exception as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def adminPanel(con):
    while True:
        printRowLine()
        print("ADMIN PANEL\n"
              "1) Add Student\n2) Update Student\n3) Delete Student\n"
              "4) Add Teacher\n5) Update Teacher\n6) Delete Teacher\n"
              "7) Show All Teachers\n8) Add Subject\n0) Back")
        ch = askInt("Choose: ")
        if ch == 0:
            break
        if ch == 1:
            adminAddStudent(con)
        elif ch == 2:
            adminUpdateStudent(con)
        elif ch == 3:
            adminDeleteStudent(con)
        elif ch == 4:
            adminAddTeacher(con)
        elif ch == 5:
            adminUpdateTeacher(con)
        elif ch == 6:
            adminDeleteTeacher(con)
        elif ch == 7:
            show_all_teacher(con)
        elif ch == 8:
            adminAddSubject(con)
        pauseLine()

# ------- TEACHER PANEL -------
def teacherSubjectById(con, tid):
    """Get the subject taught by a teacher given their ID."""
    cur = con.cursor()
    cur.execute("SELECT subject FROM teacher WHERE id=?", (tid,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else ""

def teacherUpdateAttendance(con, tid):
    """Update a student's attendance for a subject."""
    subj = teacherSubjectById(con, tid)
    if not subj:
        print("Teacher not found.")
        return
    print(f"You can update for subject: {subj}")
    roll = askInt("Student Roll No: ")
    att = askInt("Attendance points: ")
    cur = con.cursor()
    try:
        cur.execute(
            "UPDATE attendance SET attendance=?, name=(SELECT name FROM student WHERE roll_no=?), reg_no=(SELECT reg_no FROM student WHERE roll_no=?) WHERE roll_no=? AND subject=?",
            (att, roll, roll, roll, subj)
        )
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO attendance(roll_no, reg_no, name, subject, attendance) "
                "SELECT s.roll_no, s.reg_no, s.name, ?, ? FROM student s WHERE s.roll_no=?",
                (subj, att, roll)
            )
        con.commit()
        print("Attendance updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def teacherUpdateMid(con, tid):
    """Update a student's midterm marks for a subject."""
    subj = teacherSubjectById(con, tid)
    if not subj:
        print("Teacher not found.")
        return
    print(f"You can update for subject: {subj}")
    roll = askInt("Student Roll No: ")
    which = askInt("Which mid? (1/2/3): ")
    if which < 1 or which > 3:
        print("Invalid mid.")
        return
    mark = askInt("Marks: ")
    col = f"mid{which}"
    cur = con.cursor()
    try:
        cur.execute(
            f"UPDATE mid_mark SET {col}=?, name=(SELECT name FROM student WHERE roll_no=?), reg_no=(SELECT reg_no FROM student WHERE roll_no=?) WHERE roll_no=? AND subject=?",
            (mark, roll, roll, roll, subj)
        )
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO mid_mark(roll_no, reg_no, name, subject, mid1, mid2, mid3) "
                "SELECT s.roll_no, s.reg_no, s.name, ?, 0, 0, 0 FROM student s WHERE s.roll_no=?",
                (subj, roll)
            )
            cur.execute(
                f"UPDATE mid_mark SET {col}=? WHERE roll_no=? AND subject=?",
                (mark, roll, subj)
            )
        con.commit()
        print(f"Mid-{which} updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        cur.close()

def teacherPanel(con):
    tid = askInt("Enter Teacher ID: ")
    password = askStr("Enter Password: ")
    cur = con.cursor()
    cur.execute("SELECT password FROM teacher WHERE id=?", (tid,))
    row = cur.fetchone()
    cur.close()
    if not row or row[0] != password:
        print("Invalid ID or password.")
        pauseLine()
        return
    while True:
        printRowLine()
        print(f"TEACHER PANEL (ID={tid})\n"
              "1) Update Attendance\n2) Update Mid (1/2/3)\n3) Update Session Semester Result\n4) Show Semester Results (by Session)\n5) Delete Semester Result\n0) Back")
        ch = askInt("Choose: ")
        if ch == 0:
            break
        if ch == 1:
            teacherUpdateAttendance(con, tid)
        elif ch == 2:
            teacherUpdateMid(con, tid)
        elif ch == 3:
            update_session_semester_result(con, tid)
        elif ch == 4:
            show_semester_result(con)
        elif ch == 5:
            delete_semester_result(con)
        pauseLine()

# ------- STUDENT PANEL -------
def studentPanel(con):
    """Display student information including attendance, mid marks, and C-GPA."""
    roll = askInt("Enter your Roll No: ")
    while True:
        printRowLine()
        print("STUDENT PANEL\n"
              "1) Show Attendance\n"
              "2) Show Mid Marks\n"
              "3) Show Sessionwise CGPA\n"
              "4) Show Total CGPA for a Semester\n"
              "0) Back")
        ch = askInt("Choose: ")
        if ch == 0:
            break
        if ch == 1:
            print("\nAttendance:")
            cur = con.cursor()
            cur.execute("SELECT subject, attendance FROM attendance WHERE roll_no=? ORDER BY subject", (roll,))
            for subject, attendance in cur.fetchall():
                print(f"  {subject} : {attendance}")
            cur.close()
            pauseLine()
        elif ch == 2:
            print("\nMid Marks:")
            cur = con.cursor()
            cur.execute("SELECT subject, mid1, mid2, mid3 FROM mid_mark WHERE roll_no=? ORDER BY subject", (roll,))
            for subject, mid1, mid2, mid3 in cur.fetchall():
                print(f"  {subject} : mid1={mid1}, mid2={mid2}, mid3={mid3}")
            cur.close()
            pauseLine()
        elif ch == 3:
            print("\nSessionwise CGPA:")
            show_sessionwise_cgpa(con, roll)
            pauseLine()
        elif ch == 4:
            show_total_cgpa_for_semester_student(con, roll)
            pauseLine()

def show_total_cgpa_for_semester_student(con, roll):
    """Show total CGPA for a specific student in a given semester, averaging all subjects' CGPA for that semester."""
    semester = askStr("Enter semester: ")
    cur = con.cursor()
    # Get all subjects for this student in this semester
    cur.execute("SELECT semester, result FROM session_semester_result WHERE roll_no=? AND semester LIKE ?", (roll, semester + ' (%',))
    subject_results = cur.fetchall()
    if not subject_results:
        print("No results found for this semester.")
        cur.close()
        return
    total_points = 0
    subject_count = 0
    for sem, result in subject_results:
        # Extract subject from semester string
        if '(' in sem and sem.endswith(')'):
            subject = sem[sem.find('(')+1:-1]
        else:
            subject = sem
        # Get internal marks
        cur.execute("SELECT COALESCE(a.attendance,0), COALESCE(m.mid1,0), COALESCE(m.mid2,0), COALESCE(m.mid3,0) FROM attendance a LEFT JOIN mid_mark m ON m.roll_no=a.roll_no AND m.subject=a.subject WHERE a.roll_no=? AND a.subject=?", (roll, subject))
        row = cur.fetchone()
        total_internal = sum(row) if row else 0
        try:
            semester_result = float(result)
            total_marks = (total_internal / 40.0 * 40.0) + (semester_result / 60.0 * 60.0)
            if total_marks > 100:
                total_marks = 100
            cgpa = (total_marks / 100.0) * 4.0
            total_points += cgpa
            subject_count += 1
        except ValueError:
            continue
    avg_cgpa = round(total_points / subject_count, 2) if subject_count > 0 else 'N/A'
    printRowLine()
    print(f"Total CGPA for semester '{semester}': {avg_cgpa}")
    cur.close()

def attendanceSheetPanel(con):
    """Display the attendance sheet for a subject."""
    subj = askStr("Subject: ")
    printRowLine()
    print(f"ATTENDANCE SHEET for {subj}")
    cur = con.cursor()
    cur.execute(
        "SELECT a.roll_no, a.reg_no, a.name, a.attendance "
        "FROM attendance a WHERE a.subject=? ORDER BY a.roll_no", (subj,)
    )
    print(f"{'Roll':<10}{'Reg':<16}{'Name':<24}Attendance")
    for roll, reg, name, attendance in cur.fetchall():
        print(f"{roll:<10}{reg:<16}{name:<24}{attendance}")
    cur.close()
    pauseLine()

def totalInternalPanel(con):
    """Display total internal marks for a subject."""
    subj = askStr("Subject: ")
    printRowLine()
    print(f"TOTAL INTERNAL for {subj} (attendance + mid1 + mid2 + mid3)")
    cur = con.cursor()
    cur.execute(
        "SELECT s.roll_no, s.reg_no, s.name, "
        "COALESCE(a.attendance,0) AS att, "
        "COALESCE(m.mid1,0) AS m1, COALESCE(m.mid2,0) AS m2, COALESCE(m.mid3,0) AS m3, "
        "(COALESCE(a.attendance,0)+COALESCE(m.mid1,0)+COALESCE(m.mid2,0)+COALESCE(m.mid3,0)) AS total "
        "FROM student s "
        "JOIN attendance a ON a.roll_no=s.roll_no AND a.subject=? "
        "LEFT JOIN mid_mark  m ON m.roll_no=s.roll_no AND m.subject=? "
        "ORDER BY s.roll_no", (subj, subj)
    )
    print(f"{'Roll':<8}{'Reg':<14}{'Name':<22}{'Att':<6}{'M1':<6}{'M2':<6}{'M3':<6}Total")
    for row in cur.fetchall():
        print(f"{row[0]:<8}{row[1]:<14}{row[2]:<22}{row[3]:<6}{row[4]:<6}{row[5]:<6}{row[6]:<6}{row[7]}")
    cur.close()
    pauseLine()
# ------- MAIN MENU -------
def main():
    """Main entry point for the application."""
    con = connectDB()
    initialize_db(con)
    try:
        while True:
            printRowLine()
            print("MAIN MENU\n"
                  "1) Admin Panel\n"
                  "2) Teacher Panel\n"
                  "3) Student Panel\n"
                  "4) Attendance Sheet Panel\n"
                  "5) Total Internal Panel\n"
                  "6) Show All Students\n"
                  "8) Show CGPA for Course (by Semester)\n"
                  "9) Show Total CGPA for Semester\n"
                  "0) Exit")
            ch = askInt("Choose: ")
            if ch == 0:
                break
            if ch == 1:
                adminPanel(con)
            elif ch == 2:
                teacherPanel(con)
            elif ch == 3:
                studentPanel(con)
            elif ch == 4:
                attendanceSheetPanel(con)
            elif ch == 5:
                totalInternalPanel(con)
            elif ch == 6:
                show_all_student(con)
            elif ch == 8:
                calculate_and_show_course_cgpa(con)
            elif ch == 9:
                show_total_cgpa_for_semester(con)
    finally:
        con.close()

if __name__ == "__main__":
    main()
