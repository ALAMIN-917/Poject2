
import sqlite3
import sys

# ====== DB CONFIG - change for your SQLite3 ======
DB_PATH = "college_db.sqlite3"  # Path to your SQLite database file
# ===============================================

def connectDB():
    try:
        con = sqlite3.connect(DB_PATH)
        return con
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite3: {e}")
        sys.exit(1)

def pauseLine():
    input("\nPress ENTER to continue...")

def askInt(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid. Try again: ")

def askStr(prompt):
    return input(prompt)

def printRowLine(w=80):
    print('-' * w)

# ------- ADMIN PANEL -------
def adminAddStudent(con):
    roll = askInt("Roll No: ")
    reg = askStr("Reg No: ")
    name = askStr("Name: ")
    phone = askStr("Phone: ")
    email = askStr("Email: ")
    dept = askStr("Dept: ")
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO student(roll_no,reg_no,name,phone,email,dept) VALUES(%s,%s,%s,%s,%s,%s)",
            (roll, reg, name, phone, email, dept)
        )
        cur.execute(
            "INSERT INTO c_gpa(roll_no, reg_no, name, c_gpa) VALUES(%s,%s,%s,0.0)",
            (roll, reg, name)
        )
        con.commit()
        print("Student added.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def adminUpdateStudent(con):
    roll = askInt("Roll No to update: ")
    phone = askStr("New phone (or blank to skip): ")
    email = askStr("New email (or blank to skip): ")
    dept  = askStr("New dept (or blank to skip): ")
    cur = con.cursor()
    try:
        if phone:
            cur.execute("UPDATE student SET phone=%s WHERE roll_no=%s", (phone, roll))
        if email:
            cur.execute("UPDATE student SET email=%s WHERE roll_no=%s", (email, roll))
        if dept:
            cur.execute("UPDATE student SET dept=%s WHERE roll_no=%s", (dept, roll))
        con.commit()
        print("Student updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def adminDeleteStudent(con):
    roll = askInt("Roll No to delete: ")
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM student WHERE roll_no=%s", (roll,))
        con.commit()
        print("Deleted (if existed). Related rows cascade removed.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def adminAddTeacher(con):
    id = askInt("Teacher ID: ")
    name = askStr("Name: ")
    subject = askStr("Subject: ")
    dept = askStr("Dept: ")
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO teacher(id,name,subject,dept) VALUES(%s,%s,%s,%s)",
            (id, name, subject, dept)
        )
        con.commit()
        print("Teacher added.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def adminUpdateTeacher(con):
    id = askInt("Teacher ID to update: ")
    name = askStr("New name (blank skip): ")
    subject = askStr("New subject (blank skip): ")
    dept = askStr("New dept (blank skip): ")
    cur = con.cursor()
    try:
        if name:
            cur.execute("UPDATE teacher SET name=%s WHERE id=%s", (name, id))
        if subject:
            cur.execute("UPDATE teacher SET subject=%s WHERE id=%s", (subject, id))
        if dept:
            cur.execute("UPDATE teacher SET dept=%s WHERE id=%s", (dept, id))
        con.commit()
        print("Teacher updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def adminDeleteTeacher(con):
    id = askInt("Teacher ID to delete: ")
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM teacher WHERE id=%s", (id,))
        con.commit()
        print("Deleted (if existed).")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def adminUpdateCGPA(con):
    roll = askInt("Roll No: ")
    cg = float(askStr("New C-GPA (e.g. 3.75): "))
    cur = con.cursor()
    try:
        cur.execute("UPDATE c_gpa SET c_gpa=%s WHERE roll_no=%s", (cg, roll))
        con.commit()
        print("C-GPA updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def adminPanel(con):
    while True:
        printRowLine()
        print("ADMIN PANEL\n"
              "1) Add Student\n2) Update Student\n3) Delete Student\n"
              "4) Add Teacher\n5) Update Teacher\n6) Delete Teacher\n"
              "7) Update C-GPA\n0) Back")
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
            adminUpdateCGPA(con)
        pauseLine()

# ------- TEACHER PANEL -------
def teacherSubjectById(con, tid):
    cur = con.cursor()
    cur.execute("SELECT subject FROM teacher WHERE id=%s", (tid,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else ""

def teacherUpdateAttendance(con, tid):
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
            "UPDATE attendance SET attendance=%s, name=(SELECT name FROM student WHERE roll_no=%s), reg_no=(SELECT reg_no FROM student WHERE roll_no=%s) WHERE roll_no=%s AND subject=%s",
            (att, roll, roll, roll, subj)
        )
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO attendance(roll_no, reg_no, name, subject, attendance) "
                "SELECT s.roll_no, s.reg_no, s.name, %s, %s FROM student s WHERE s.roll_no=%s",
                (subj, att, roll)
            )
        con.commit()
        print("Attendance updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def teacherUpdateMid(con, tid):
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
            f"UPDATE mid_mark SET {col}=%s, name=(SELECT name FROM student WHERE roll_no=%s), reg_no=(SELECT reg_no FROM student WHERE roll_no=%s) WHERE roll_no=%s AND subject=%s",
            (mark, roll, roll, roll, subj)
        )
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO mid_mark(roll_no, reg_no, name, subject, mid1, mid2, mid3) "
                "SELECT s.roll_no, s.reg_no, s.name, %s, 0, 0, 0 FROM student s WHERE s.roll_no=%s",
                (subj, roll)
            )
            cur.execute(
                f"UPDATE mid_mark SET {col}=%s WHERE roll_no=%s AND subject=%s",
                (mark, roll, subj)
            )
        con.commit()
        print(f"Mid-{which} updated.")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    cur.close()

def teacherPanel(con):
    tid = askInt("Enter Teacher ID: ")
    while True:
        printRowLine()
        print(f"TEACHER PANEL (ID={tid})\n"
              "1) Update Attendance\n2) Update Mid (1/2/3)\n0) Back")
        ch = askInt("Choose: ")
        if ch == 0:
            break
        if ch == 1:
            teacherUpdateAttendance(con, tid)
        elif ch == 2:
            teacherUpdateMid(con, tid)
        pauseLine()

# ------- STUDENT PANEL -------
def studentPanel(con):
    roll = askInt("Enter your Roll No: ")
    printRowLine()
    print("STUDENT INFO\n")
    cur = con.cursor()
    # Attendance
    print("\nAttendance:")
    cur.execute("SELECT subject, attendance FROM attendance WHERE roll_no=%s ORDER BY subject", (roll,))
    for subject, attendance in cur.fetchall():
        print(f"  {subject} : {attendance}")
    # Mid marks
    print("\nMid Marks:")
    cur.execute("SELECT subject, mid1, mid2, mid3 FROM mid_mark WHERE roll_no=%s ORDER BY subject", (roll,))
    for subject, mid1, mid2, mid3 in cur.fetchall():
        print(f"  {subject} : mid1={mid1}, mid2={mid2}, mid3={mid3}")
    # C-GPA
    print("\nC-GPA:")
    cur.execute("SELECT c_gpa FROM c_gpa WHERE roll_no=%s", (roll,))
    row = cur.fetchone()
    print(f"  {row[0] if row else 'Not set.'}\n")
    cur.close()
    pauseLine()

# ------- ATTENDANCE SHEET PANEL -------
def attendanceSheetPanel(con):
    subj = askStr("Subject: ")
    printRowLine()
    print(f"ATTENDANCE SHEET for {subj}")
    cur = con.cursor()
    cur.execute(
        "SELECT a.roll_no, a.reg_no, a.name, a.attendance "
        "FROM attendance a WHERE a.subject=%s ORDER BY a.roll_no", (subj,)
    )
    print(f"{'Roll':<10}{'Reg':<16}{'Name':<24}Attendance")
    for roll, reg, name, attendance in cur.fetchall():
        print(f"{roll:<10}{reg:<16}{name:<24}{attendance}")
    cur.close()
    pauseLine()

# ------- TOTAL INTERNAL PANEL -------
def totalInternalPanel(con):
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
        "LEFT JOIN attendance a ON a.roll_no=s.roll_no AND a.subject=%s "
        "LEFT JOIN mid_mark  m ON m.roll_no=s.roll_no AND m.subject=%s "
        "ORDER BY s.roll_no", (subj, subj)
    )
    print(f"{'Roll':<8}{'Reg':<14}{'Name':<22}{'Att':<6}{'M1':<6}{'M2':<6}{'M3':<6}Total")
    for row in cur.fetchall():
        print(f"{row[0]:<8}{row[1]:<14}{row[2]:<22}{row[3]:<6}{row[4]:<6}{row[5]:<6}{row[6]:<6}{row[7]}")
    cur.close()
    pauseLine()

# ------- MAIN MENU -------
def main():
    con = connectDB()
    while True:
        printRowLine()
        print("MAIN MENU\n"
              "1) Admin Panel\n"
              "2) Teacher Panel\n"
              "3) Student Panel\n"
              "4) Attendance Sheet Panel\n"
              "5) Total Internal Panel\n"
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
    con.close()

if __name__ == "__main__":
    main()
