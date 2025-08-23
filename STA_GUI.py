import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import os
import csv

# Optional: Pillow for image handling (resizing)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

DB_PATH = "college_db.sqlite3"

# ---------- Database helper ----------

def connectDB():
    try:
        con = sqlite3.connect(DB_PATH)
        return con
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))
        return None

# ---------- Background handling ----------

_bg_photo = None
_bg_path = None

def set_background_image(root, path=None):
    """Set a background image for the main window. If Pillow not available, display an error.
    If path is None, prompt the user to choose an image file.
    """
    global _bg_photo, _bg_path
    if path is None:
        path = filedialog.askopenfilename(title="Select background image",
                                          filetypes=[("PNG/JPG images", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*")])
        if not path:
            return
    if not PIL_AVAILABLE:
        messagebox.showwarning("Pillow missing", "Pillow is not installed. Install it (see requirements.txt) to use background images.")
        return
    try:
        img = Image.open(path)
        # Resize to window size
        w = root.winfo_width() or 800
        h = root.winfo_height() or 600
        img = img.resize((w, h), Image.LANCZOS)
        _bg_photo = ImageTk.PhotoImage(img)
        _bg_path = path
        # Place label at the bottom of stacking order
        if hasattr(root, 'bg_label') and root.bg_label:
            root.bg_label.configure(image=_bg_photo)
        else:
            root.bg_label = tk.Label(root, image=_bg_photo)
            root.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        messagebox.showerror("Image Error", f"Failed to load image: {e}")

# ---------- Admin functions (reuse previous implementations) ----------

# I'll keep the core admin functions as small wrappers that create Toplevels and call DB logic.

def add_student_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("Add Student")
    labels = ["Roll No", "Reg No", "Name", "Phone", "Email", "Dept", "Session"]
    entries = []
    for i, label in enumerate(labels):
        ttk.Label(win, text=label).grid(row=i, column=0, sticky='e', padx=6, pady=4)
        entry = ttk.Entry(win)
        entry.grid(row=i, column=1, padx=6, pady=4)
        entries.append(entry)
    def submit():
        values = [e.get().strip() for e in entries]
        if not all(values):
            messagebox.showerror("Input Error", "All fields are required.")
            return
        try:
            con = connectDB()
            cur = con.cursor()
            cur.execute("INSERT INTO student(roll_no,reg_no,name,phone,email,dept,session) VALUES(?,?,?,?,?,?,?)", tuple(values))
            cur.execute("INSERT INTO c_gpa(roll_no, reg_no, name, c_gpa) VALUES(?,?,?,0.0)", (values[0], values[1], values[2]))
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Success", "Student added.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(win, text="Submit", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=10)


def update_student_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("Update Student")
    ttk.Label(win, text="Roll No to update:").grid(row=0, column=0, padx=6, pady=4)
    roll_entry = ttk.Entry(win)
    roll_entry.grid(row=0, column=1)
    ttk.Label(win, text="New phone (blank skip):").grid(row=1, column=0)
    phone_entry = ttk.Entry(win)
    phone_entry.grid(row=1, column=1)
    ttk.Label(win, text="New email (blank skip):").grid(row=2, column=0)
    email_entry = ttk.Entry(win)
    email_entry.grid(row=2, column=1)
    ttk.Label(win, text="New dept (blank skip):").grid(row=3, column=0)
    dept_entry = ttk.Entry(win)
    dept_entry.grid(row=3, column=1)
    def submit():
        roll = roll_entry.get().strip()
        phone = phone_entry.get().strip()
        email = email_entry.get().strip()
        dept = dept_entry.get().strip()
        if not roll:
            messagebox.showerror("Input Error", "Roll No is required.")
            return
        con = connectDB()
        cur = con.cursor()
        try:
            if phone:
                cur.execute("UPDATE student SET phone=? WHERE roll_no=?", (phone, roll))
            if email:
                cur.execute("UPDATE student SET email=? WHERE roll_no=?", (email, roll))
            if dept:
                cur.execute("UPDATE student SET dept=? WHERE roll_no=?", (dept, roll))
            con.commit()
            messagebox.showinfo("Success", "Student updated.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Submit", command=submit).grid(row=4, column=0, columnspan=2, pady=10)


def delete_student_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("Delete Student")
    ttk.Label(win, text="Roll No to delete:").pack(padx=6, pady=6)
    roll_entry = ttk.Entry(win)
    roll_entry.pack(padx=6, pady=6)
    def submit():
        roll = roll_entry.get().strip()
        if not roll:
            messagebox.showerror("Input Error", "Roll No is required.")
            return
        con = connectDB()
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM student WHERE roll_no=?", (roll,))
            con.commit()
            messagebox.showinfo("Success", "Student deleted (if existed).")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Delete", command=submit).pack(pady=10)


def show_all_students_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("All Students")
    cols = ("Roll", "Reg", "Name", "Phone", "Email", "Dept", "Session")
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill='both', expand=True)
    con = connectDB()
    cur = con.cursor()
    cur.execute("SELECT roll_no, reg_no, name, phone, email, dept, session FROM student ORDER BY roll_no")
    for row in cur.fetchall():
        tree.insert('', 'end', values=row)
    cur.close()
    con.close()

# --- Teacher CRUD & Actions (kept as before, but adapted to notebook layout) ---

def add_teacher_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("Add Teacher")
    labels = ["Teacher ID", "Name", "Subject", "Dept", "Password", "Exam Control Power (session, comma separated)"]
    entries = []
    for i, label in enumerate(labels):
        ttk.Label(win, text=label).grid(row=i, column=0, sticky='e', padx=6, pady=4)
        entry = ttk.Entry(win)
        entry.grid(row=i, column=1, padx=6, pady=4)
        entries.append(entry)
    def submit():
        values = [e.get().strip() for e in entries]
        if not all(values):
            messagebox.showerror("Input Error", "All fields are required.")
            return
        try:
            con = connectDB()
            cur = con.cursor()
            cur.execute("INSERT INTO teacher(id,name,subject,dept,password,exam_control_power) VALUES(?,?,?,?,?,?)", tuple(values))
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Success", "Teacher added.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(win, text="Submit", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=10)


def update_teacher_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("Update Teacher")
    ttk.Label(win, text="Teacher ID to update:").grid(row=0, column=0, padx=6, pady=4)
    id_entry = ttk.Entry(win)
    id_entry.grid(row=0, column=1)
    ttk.Label(win, text="New name (blank skip):").grid(row=1, column=0)
    name_entry = ttk.Entry(win)
    name_entry.grid(row=1, column=1)
    ttk.Label(win, text="New subject (blank skip):").grid(row=2, column=0)
    subject_entry = ttk.Entry(win)
    subject_entry.grid(row=2, column=1)
    ttk.Label(win, text="New dept (blank skip):").grid(row=3, column=0)
    dept_entry = ttk.Entry(win)
    dept_entry.grid(row=3, column=1)
    def submit():
        id = id_entry.get().strip()
        name = name_entry.get().strip()
        subject = subject_entry.get().strip()
        dept = dept_entry.get().strip()
        if not id:
            messagebox.showerror("Input Error", "Teacher ID is required.")
            return
        con = connectDB()
        cur = con.cursor()
        try:
            if name:
                cur.execute("UPDATE teacher SET name=? WHERE id=?", (name, id))
            if subject:
                cur.execute("UPDATE teacher SET subject=? WHERE id=?", (subject, id))
            if dept:
                cur.execute("UPDATE teacher SET dept=? WHERE id=?", (dept, id))
            con.commit()
            messagebox.showinfo("Success", "Teacher updated.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Submit", command=submit).grid(row=4, column=0, columnspan=2, pady=10)


def delete_teacher_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("Delete Teacher")
    ttk.Label(win, text="Teacher ID to delete:").pack(padx=6, pady=6)
    id_entry = ttk.Entry(win)
    id_entry.pack(padx=6, pady=6)
    def submit():
        id = id_entry.get().strip()
        if not id:
            messagebox.showerror("Input Error", "Teacher ID is required.")
            return
        con = connectDB()
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM teacher WHERE id=?", (id,))
            con.commit()
            messagebox.showinfo("Success", "Teacher deleted (if existed).")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Delete", command=submit).pack(pady=10)


def show_all_teachers_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("All Teachers")
    cols = ("ID", "Name", "Subject", "Dept", "Exam Control")
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill='both', expand=True)
    con = connectDB()
    cur = con.cursor()
    cur.execute("SELECT id, name, subject, dept, exam_control_power FROM teacher ORDER BY id")
    for row in cur.fetchall():
        tree.insert('', 'end', values=row)
    cur.close()
    con.close()

# ---------- Teacher action helpers (attendance, mids, session results) ----------

def teacher_get_subject(tid):
    con = connectDB()
    if not con:
        return ""
    cur = con.cursor()
    cur.execute("SELECT subject FROM teacher WHERE id=?", (tid,))
    r = cur.fetchone()
    cur.close()
    con.close()
    return r[0] if r else ""


def teacher_update_attendance(tid):
    subj = teacher_get_subject(tid)
    if not subj:
        messagebox.showerror("Error", "Teacher subject not found.")
        return
    win = tk.Toplevel(root)
    win.title("Update Attendance")
    ttk.Label(win, text=f"Updating attendance for subject: {subj}").grid(row=0, column=0, columnspan=2, padx=6, pady=6)
    ttk.Label(win, text="Student Roll No:").grid(row=1, column=0)
    roll_entry = ttk.Entry(win)
    roll_entry.grid(row=1, column=1)
    ttk.Label(win, text="Attendance points:").grid(row=2, column=0)
    att_entry = ttk.Entry(win)
    att_entry.grid(row=2, column=1)
    def submit():
        roll = roll_entry.get().strip()
        att = att_entry.get().strip()
        if not roll or not att:
            messagebox.showerror("Input Error", "Both fields required.")
            return
        try:
            att_val = int(att)
        except ValueError:
            messagebox.showerror("Input Error", "Attendance must be an integer.")
            return
        con = connectDB()
        cur = con.cursor()
        try:
            cur.execute(
                "UPDATE attendance SET attendance=?, name=(SELECT name FROM student WHERE roll_no=?), reg_no=(SELECT reg_no FROM student WHERE roll_no=?) WHERE roll_no=? AND subject=?",
                (att_val, roll, roll, roll, subj)
            )
            if cur.rowcount == 0:
                cur.execute(
                    "INSERT INTO attendance(roll_no, reg_no, name, subject, attendance) SELECT s.roll_no, s.reg_no, s.name, ?, ? FROM student s WHERE s.roll_no=?",
                    (subj, att_val, roll)
                )
            con.commit()
            messagebox.showinfo("Success", "Attendance updated.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Submit", command=submit).grid(row=3, column=0, columnspan=2, pady=8)


def teacher_update_mid(tid):
    subj = teacher_get_subject(tid)
    if not subj:
        messagebox.showerror("Error", "Teacher subject not found.")
        return
    win = tk.Toplevel(root)
    win.title("Update Mid Marks")
    ttk.Label(win, text=f"Updating mids for subject: {subj}").grid(row=0, column=0, columnspan=2, padx=6, pady=6)
    ttk.Label(win, text="Student Roll No:").grid(row=1, column=0)
    roll_entry = ttk.Entry(win)
    roll_entry.grid(row=1, column=1)
    ttk.Label(win, text="Which mid? (1/2/3):").grid(row=2, column=0)
    which_entry = ttk.Entry(win)
    which_entry.grid(row=2, column=1)
    ttk.Label(win, text="Marks:").grid(row=3, column=0)
    mark_entry = ttk.Entry(win)
    mark_entry.grid(row=3, column=1)
    def submit():
        roll = roll_entry.get().strip()
        which = which_entry.get().strip()
        mark = mark_entry.get().strip()
        if not roll or not which or not mark:
            messagebox.showerror("Input Error", "All fields required.")
            return
        try:
            which_i = int(which)
            mark_i = int(mark)
        except ValueError:
            messagebox.showerror("Input Error", "Which and Marks must be integers.")
            return
        if which_i < 1 or which_i > 3:
            messagebox.showerror("Input Error", "Which must be 1, 2, or 3.")
            return
        col = f"mid{which_i}"
        con = connectDB()
        cur = con.cursor()
        try:
            cur.execute(f"UPDATE mid_mark SET {col}=?, name=(SELECT name FROM student WHERE roll_no=?), reg_no=(SELECT reg_no FROM student WHERE roll_no=?) WHERE roll_no=? AND subject=?", (mark_i, roll, roll, roll, subj))
            if cur.rowcount == 0:
                cur.execute("INSERT INTO mid_mark(roll_no, reg_no, name, subject, mid1, mid2, mid3) SELECT s.roll_no, s.reg_no, s.name, ?, 0, 0, 0 FROM student s WHERE s.roll_no=?", (subj, roll))
                cur.execute(f"UPDATE mid_mark SET {col}=? WHERE roll_no=? AND subject=?", (mark_i, roll, subj))
            con.commit()
            messagebox.showinfo("Success", f"Mid-{which_i} updated.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Submit", command=submit).grid(row=4, column=0, columnspan=2, pady=8)


def teacher_update_session_semester_result(tid):
    con = connectDB()
    cur = con.cursor()
    cur.execute("SELECT exam_control_power FROM teacher WHERE id=?", (tid,))
    row = cur.fetchone()
    if not row or not row[0]:
        messagebox.showerror("Unauthorized", "You do not have exam control power for any session.")
        cur.close()
        con.close()
        return
    allowed_sessions = [s.strip() for s in row[0].split(',') if s.strip()]
    cur.close()
    con.close()
    win = tk.Toplevel(root)
    win.title("Update Session-Semester Result")
    ttk.Label(win, text="Session to set result for:").grid(row=0, column=0, padx=6, pady=4)
    session_entry = ttk.Entry(win)
    session_entry.grid(row=0, column=1)
    ttk.Label(win, text="Student Roll No:").grid(row=1, column=0)
    roll_entry = ttk.Entry(win)
    roll_entry.grid(row=1, column=1)
    ttk.Label(win, text="Semester (e.g. Fall-2024):").grid(row=2, column=0)
    sem_entry = ttk.Entry(win)
    sem_entry.grid(row=2, column=1)
    ttk.Label(win, text="Result (numeric):").grid(row=3, column=0)
    res_entry = ttk.Entry(win)
    res_entry.grid(row=3, column=1)
    def submit():
        session = session_entry.get().strip()
        roll = roll_entry.get().strip()
        semester = sem_entry.get().strip()
        result = res_entry.get().strip()
        if not session or not roll or not semester or not result:
            messagebox.showerror("Input Error", "All fields required.")
            return
        if session not in allowed_sessions:
            messagebox.showerror("Unauthorized", "You are not authorized to set results for this session.")
            return
        con = connectDB()
        cur = con.cursor()
        cur.execute("SELECT DISTINCT subject FROM attendance WHERE roll_no=?", (roll,))
        subjects = [r[0] for r in cur.fetchall()]
        if not subjects:
            messagebox.showerror("No Subjects", "No subjects found for this student.")
            cur.close()
            con.close()
            return
        subj = simpledialog.askstring("Subject", f"Subjects: {', '.join(subjects)}\nEnter subject to set result for:")
        if not subj or subj not in subjects:
            messagebox.showerror("Input Error", "Invalid subject selected.")
            cur.close()
            con.close()
            return
        try:
            cur.execute("DELETE FROM session_semester_result WHERE session=? AND roll_no=? AND semester=?", (session, roll, semester + f" ({subj})"))
            cur.execute("INSERT INTO session_semester_result(session, roll_no, semester, result, controller_id) VALUES(?,?,?,?,?)", (session, roll, semester + f" ({subj})", result, tid))
            con.commit()
            messagebox.showinfo("Success", "Result updated.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Submit", command=submit).grid(row=4, column=0, columnspan=2, pady=8)


def teacher_show_semester_results():
    win = tk.Toplevel(root)
    win.title("Semester Results (by Session)")
    session = simpledialog.askstring("Session", "Enter session to view results for:")
    if not session:
        return
    cols = ("Roll", "Name", "Semester", "Result")
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill='both', expand=True)
    con = connectDB()
    cur = con.cursor()
    cur.execute("SELECT s.roll_no, s.name, ssr.semester, ssr.result FROM session_semester_result ssr JOIN student s ON s.roll_no = ssr.roll_no WHERE ssr.session = ? ORDER BY s.roll_no, ssr.semester", (session,))
    for row in cur.fetchall():
        tree.insert('', 'end', values=row)
    cur.close()
    con.close()


def teacher_delete_semester_result():
    win = tk.Toplevel(root)
    win.title("Delete Semester Result")
    ttk.Label(win, text="Session:").grid(row=0, column=0, padx=6, pady=4)
    session_entry = ttk.Entry(win)
    session_entry.grid(row=0, column=1)
    ttk.Label(win, text="Student Roll No:").grid(row=1, column=0)
    roll_entry = ttk.Entry(win)
    roll_entry.grid(row=1, column=1)
    ttk.Label(win, text="Semester:").grid(row=2, column=0)
    sem_entry = ttk.Entry(win)
    sem_entry.grid(row=2, column=1)
    def submit():
        session = session_entry.get().strip()
        roll = roll_entry.get().strip()
        semester = sem_entry.get().strip()
        if not session or not roll or not semester:
            messagebox.showerror("Input Error", "All fields required.")
            return
        con = connectDB()
        cur = con.cursor()
        cur.execute("SELECT DISTINCT subject FROM attendance WHERE roll_no=?", (roll,))
        subjects = [r[0] for r in cur.fetchall()]
        if not subjects:
            messagebox.showerror("No Subjects", "No subjects found for this student.")
            cur.close()
            con.close()
            return
        subj = simpledialog.askstring("Subject", f"Subjects: {', '.join(subjects)}\nEnter subject to delete result for:")
        if not subj or subj not in subjects:
            messagebox.showerror("Input Error", "Invalid subject selected.")
            cur.close()
            con.close()
            return
        try:
            cur.execute("DELETE FROM session_semester_result WHERE session=? AND roll_no=? AND semester=?", (session, roll, semester + f" ({subj})"))
            con.commit()
            messagebox.showinfo("Success", "Result deleted (if existed).")
            win.destroy()
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            cur.close()
            con.close()

# ---------- Main GUI (Notebook layout) ----------

def main_gui():
    global root
    root = tk.Tk()
    root.title("Student Academic Tracker (GUI)")
    root.geometry("900x600")

    # Menu
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Set Background Image", command=lambda: set_background_image(root))
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    style = ttk.Style(root)
    style.theme_use('clam')

    # Background placeholder
    if not hasattr(root, 'bg_label'):
        root.bg_label = None

    # Notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=12, pady=12)

    # Admin tab
    admin_frame = ttk.Frame(notebook)
    notebook.add(admin_frame, text='Admin')
    ttk.Label(admin_frame, text="Admin Actions", font=("Arial", 14, "bold")).pack(pady=8)
    btn_frame = ttk.Frame(admin_frame)
    btn_frame.pack(pady=6)
    ttk.Button(btn_frame, text="Add Student", width=20, command=lambda: add_student_gui(root)).grid(row=0, column=0, padx=6, pady=6)
    ttk.Button(btn_frame, text="Update Student", width=20, command=lambda: update_student_gui(root)).grid(row=0, column=1, padx=6, pady=6)
    ttk.Button(btn_frame, text="Delete Student", width=20, command=lambda: delete_student_gui(root)).grid(row=1, column=0, padx=6, pady=6)
    ttk.Button(btn_frame, text="Show All Students", width=20, command=lambda: show_all_students_gui(root)).grid(row=1, column=1, padx=6, pady=6)
    ttk.Button(btn_frame, text="Add Teacher", width=20, command=lambda: add_teacher_gui(root)).grid(row=2, column=0, padx=6, pady=6)
    ttk.Button(btn_frame, text="Update Teacher", width=20, command=lambda: update_teacher_gui(root)).grid(row=2, column=1, padx=6, pady=6)
    ttk.Button(btn_frame, text="Delete Teacher", width=20, command=lambda: delete_teacher_gui(root)).grid(row=3, column=0, padx=6, pady=6)
    ttk.Button(btn_frame, text="Show All Teachers", width=20, command=lambda: show_all_teachers_gui(root)).grid(row=3, column=1, padx=6, pady=6)
    ttk.Button(btn_frame, text="Add Subject", width=20, command=lambda: add_subject_gui(root)).grid(row=4, column=0, padx=6, pady=6)

    # Teacher tab
    teacher_frame = ttk.Frame(notebook)
    notebook.add(teacher_frame, text='Teacher')
    ttk.Label(teacher_frame, text="Teacher Actions", font=("Arial", 14, "bold")).pack(pady=8)
    tbtn_frame = ttk.Frame(teacher_frame)
    tbtn_frame.pack(pady=6)
    # For teacher actions we ask for ID each time (could be extended to login once)
    ttk.Button(tbtn_frame, text="Update Attendance", width=24, command=lambda: teacher_login_action(teacher_update_attendance)).grid(row=0, column=0, padx=6, pady=6)
    ttk.Button(tbtn_frame, text="Update Mid Marks", width=24, command=lambda: teacher_login_action(teacher_update_mid)).grid(row=0, column=1, padx=6, pady=6)
    ttk.Button(tbtn_frame, text="Update Session-Semester Result", width=24, command=lambda: teacher_login_action(teacher_update_session_semester_result)).grid(row=1, column=0, padx=6, pady=6)
    ttk.Button(tbtn_frame, text="Show Semester Results (by Session)", width=24, command=teacher_show_semester_results).grid(row=1, column=1, padx=6, pady=6)
    ttk.Button(tbtn_frame, text="Delete Semester Result", width=24, command=teacher_delete_semester_result).grid(row=2, column=0, padx=6, pady=6)

    # Student tab
    student_frame = ttk.Frame(notebook)
    notebook.add(student_frame, text='Student')
    ttk.Label(student_frame, text="Student Actions", font=("Arial", 14, "bold")).pack(pady=8)
    sbtn_frame = ttk.Frame(student_frame)
    sbtn_frame.pack(pady=6)
    ttk.Button(sbtn_frame, text="Show My Info", width=24, command=lambda: student_panel()).grid(row=0, column=0, padx=6, pady=6)

    # Reports tab (Attendance / Internal / CGPA)
    reports_frame = ttk.Frame(notebook)
    notebook.add(reports_frame, text='Reports')
    ttk.Label(reports_frame, text="Reports & Sheets", font=("Arial", 14, "bold")).pack(pady=8)
    rbtn_frame = ttk.Frame(reports_frame)
    rbtn_frame.pack(pady=6)
    ttk.Button(rbtn_frame, text="Attendance Sheet (by Subject)", width=28, command=attendance_sheet_gui).grid(row=0, column=0, padx=6, pady=6)
    ttk.Button(rbtn_frame, text="Total Internal (by Subject)", width=28, command=total_internal_gui).grid(row=0, column=1, padx=6, pady=6)
    ttk.Button(rbtn_frame, text="Show All Students", width=28, command=lambda: show_all_students_gui(root)).grid(row=1, column=0, padx=6, pady=6)
    ttk.Button(rbtn_frame, text="Show CGPA for Course (Semester)", width=28, command=course_cgpa_gui).grid(row=1, column=1, padx=6, pady=6)
    ttk.Button(rbtn_frame, text="Show Total CGPA for Semester (Session)", width=60, command=semester_total_cgpa_gui).grid(row=2, column=0, columnspan=2, padx=6, pady=6)

    # footer
    footer = ttk.Label(root, text="Student Academic Tracker — GUI", anchor='center')
    footer.pack(side='bottom', fill='x')

    # handle resizing for background image
    def on_resize(event):
        if PIL_AVAILABLE and _bg_path:
            try:
                set_background_image(root, _bg_path)
            except Exception:
                pass
    root.bind('<Configure>', on_resize)

    root.mainloop()

# Helper: teacher login that runs action(tid) if login ok

def teacher_login_action(action):
    tid = simpledialog.askinteger("Teacher Login", "Enter Teacher ID:")
    if not tid:
        return
    password = simpledialog.askstring("Teacher Login", "Enter Password:", show='*')
    if password is None:
        return
    con = connectDB()
    if not con:
        return
    cur = con.cursor()
    cur.execute("SELECT password FROM teacher WHERE id=?", (tid,))
    row = cur.fetchone()
    cur.close()
    con.close()
    if not row or row[0] != password:
        messagebox.showerror("Login Failed", "Invalid ID or password.")
        return
    # call the action with tid
    try:
        action(tid)
    except TypeError:
        # some actions don't take tid
        action()

def add_subject_gui(parent=None):
    win = tk.Toplevel(parent or root)
    win.title("Add Subject")
    ttk.Label(win, text="Subject Name:").grid(row=0, column=0, padx=6, pady=6)
    subj_entry = ttk.Entry(win)
    subj_entry.grid(row=0, column=1, padx=6, pady=6)
    def submit():
        subj = subj_entry.get().strip()
        if not subj:
            messagebox.showerror("Input Error", "Subject name required.")
            return
        con = connectDB()
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO subject(name) VALUES(?)", (subj,))
            con.commit()
            messagebox.showinfo("Success", "Subject added.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            cur.close()
            con.close()
    ttk.Button(win, text="Add", command=submit).grid(row=1, column=0, columnspan=2, pady=8)


def student_panel():
    roll = simpledialog.askstring("Student Login", "Enter your Roll No:")
    if not roll:
        return
    con = connectDB()
    if not con:
        return
    cur = con.cursor()
    cur.execute("SELECT roll_no, reg_no, name, dept, session FROM student WHERE roll_no=?", (roll,))
    student = cur.fetchone()
    cur.close()
    con.close()
    if not student:
        messagebox.showerror("Not Found", "Student not found.")
        return
    win = tk.Toplevel(root)
    win.title(f"Student: {student[2]} ({student[0]})")
    ttk.Label(win, text=f"Name: {student[2]}").grid(row=0, column=0, sticky='w', padx=6, pady=4)
    ttk.Label(win, text=f"Roll: {student[0]}").grid(row=0, column=1, sticky='w', padx=6, pady=4)
    ttk.Label(win, text=f"Reg: {student[1]}").grid(row=1, column=0, sticky='w', padx=6, pady=4)
    ttk.Label(win, text=f"Dept: {student[3]}").grid(row=1, column=1, sticky='w', padx=6, pady=4)
    btn_frame = ttk.Frame(win)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=8)

    def show_attendance():
        a_win = tk.Toplevel(win)
        a_win.title("Attendance")
        cols = ("Subject", "Attendance")
        tree = ttk.Treeview(a_win, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
        tree.pack(fill='both', expand=True)
        con = connectDB()
        cur = con.cursor()
        cur.execute("SELECT subject, attendance FROM attendance WHERE roll_no=? ORDER BY subject", (roll,))
        for r in cur.fetchall():
            tree.insert('', 'end', values=r)
        cur.close()
        con.close()

    def show_mid_marks():
        m_win = tk.Toplevel(win)
        m_win.title("Mid Marks")
        cols = ("Subject", "Mid1", "Mid2", "Mid3")
        tree = ttk.Treeview(m_win, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
        tree.pack(fill='both', expand=True)
        con = connectDB()
        cur = con.cursor()
        cur.execute("SELECT subject, mid1, mid2, mid3 FROM mid_mark WHERE roll_no=? ORDER BY subject", (roll,))
        for r in cur.fetchall():
            tree.insert('', 'end', values=r)
        cur.close()
        con.close()

    def show_sessionwise_cgpa():
        s_win = tk.Toplevel(win)
        s_win.title("Sessionwise CGPA")
        text = tk.Text(s_win, wrap='word', height=20)
        text.pack(fill='both', expand=True)
        con = connectDB()
        cur = con.cursor()
        cur.execute("SELECT DISTINCT session FROM session_semester_result WHERE roll_no=?", (roll,))
        sessions = [r[0] for r in cur.fetchall()]
        if not sessions:
            text.insert('end', "No session results found for this student.")
            cur.close()
            con.close()
            return
        for s in sessions:
            cur.execute("SELECT semester, result FROM session_semester_result WHERE roll_no=? AND session=?", (roll, s))
            items = cur.fetchall()
            if not items:
                continue
            text.insert('end', f"Session: {s}\n")
            total = 0.0
            count = 0
            for sem, res in items:
                try:
                    val = float(res)
                except Exception:
                    val = 0.0
                text.insert('end', f"  {sem}: {res}\n")
                total += val
                count += 1
            cgpa = (total / count) / 25.0 if count else 0.0  # assume result scaled: 100 -> 4.0, so /25
            text.insert('end', f"  Session CGPA (approx): {cgpa:.2f}\n\n")
        cur.close()
        con.close()

    def show_total_cgpa_for_session_semester():
        sess = simpledialog.askstring("Session", "Enter session:")
        if not sess:
            return
        sem = simpledialog.askstring("Semester", "Enter semester:")
        if not sem:
            return
        con = connectDB()
        cur = con.cursor()
        cur.execute("SELECT DISTINCT subject FROM attendance WHERE roll_no=?", (roll,))
        subjects = [r[0] for r in cur.fetchall()]
        if not subjects:
            messagebox.showerror("No Subjects", "No subjects found for this student.")
            cur.close()
            con.close()
            return
        total_score = 0.0
        count = 0
        for subj in subjects:
            # get attendance (internal component) and mids
            cur.execute("SELECT attendance FROM attendance WHERE roll_no=? AND subject=?", (roll, subj))
            att = cur.fetchone()
            att_val = att[0] if att and att[0] is not None else 0
            cur.execute("SELECT mid1, mid2, mid3 FROM mid_mark WHERE roll_no=? AND subject=?", (roll, subj))
            mids = cur.fetchone()
            mids_sum = sum([m if m else 0 for m in mids]) if mids else 0
            internal = att_val + mids_sum
            # get semester exam result
            cur.execute("SELECT result FROM session_semester_result WHERE session=? AND roll_no=? AND semester=?", (sess, roll, sem + f" ({subj})"))
            r = cur.fetchone()
            semester_result = float(r[0]) if r and r[0] else 0.0
            # total out of 100
            total = internal + semester_result
            total_score += total
            count += 1
        cur.close()
        con.close()
        if count == 0:
            messagebox.showinfo("No Data", "No subjects with results found.")
            return
        avg = total_score / count
        approx_cgpa = (avg / 100.0) * 4.0
        messagebox.showinfo("Total CGPA", f"Avg marks: {avg:.2f}\nApprox CGPA: {approx_cgpa:.2f}")

    ttk.Button(btn_frame, text="Show Attendance", width=20, command=show_attendance).grid(row=0, column=0, padx=6, pady=6)
    ttk.Button(btn_frame, text="Show Mid Marks", width=20, command=show_mid_marks).grid(row=0, column=1, padx=6, pady=6)
    ttk.Button(btn_frame, text="Show Sessionwise CGPA", width=20, command=show_sessionwise_cgpa).grid(row=1, column=0, padx=6, pady=6)
    ttk.Button(btn_frame, text="Total CGPA (Session+Semester)", width=24, command=show_total_cgpa_for_session_semester).grid(row=1, column=1, padx=6, pady=6)

def attendance_sheet_gui():
    win = tk.Toplevel(root)
    win.title("Attendance Sheet")
    win.geometry("800x520")
    win.transient(root)
    win.grab_set()

    top_frame = ttk.Frame(win, padding=(12, 8))
    top_frame.pack(fill='x')

    ttk.Label(top_frame, text="Subject:", font=(None, 10, 'bold')).grid(row=0, column=0, sticky='w')
    subject_cb = ttk.Combobox(top_frame, state='readonly', width=40)
    subject_cb.grid(row=0, column=1, padx=6)

    ttk.Label(top_frame, text="Filter (roll or name):", font=(None, 10)).grid(row=0, column=2, sticky='w', padx=(12,0))
    filter_entry = ttk.Entry(top_frame, width=24)
    filter_entry.grid(row=0, column=3, padx=6)

    btn_frame = ttk.Frame(top_frame)
    btn_frame.grid(row=0, column=4, padx=(12,0))
    load_btn = ttk.Button(btn_frame, text="Load", width=10)
    load_btn.grid(row=0, column=0, padx=4)
    refresh_btn = ttk.Button(btn_frame, text="Refresh Subjects", width=14)
    refresh_btn.grid(row=0, column=1, padx=4)
    export_btn = ttk.Button(btn_frame, text="Export CSV", width=12)
    export_btn.grid(row=0, column=2, padx=4)

    # Treeview area
    tree_frame = ttk.Frame(win, padding=(12, 6))
    tree_frame.pack(fill='both', expand=True)

    cols = ("Roll", "Reg", "Name", "Attendance")
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings', selectmode='browse')
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor='w')

    vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    status = ttk.Label(win, text="Ready", anchor='w')
    status.pack(fill='x', padx=12, pady=(0,8))

    def load_subjects():
        con = connectDB()
        cur = con.cursor()
        try:
            # prefer subjects defined in subject table, but include any subjects from attendance as fallback
            cur.execute("SELECT sub_name FROM subject ORDER BY sub_name")
            s1 = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT DISTINCT subject FROM attendance ORDER BY subject")
            s2 = [r[0] for r in cur.fetchall()]
            subjects = sorted(list(dict.fromkeys(s1 + s2)))
            subject_cb['values'] = subjects
            if subjects:
                subject_cb.set(subjects[0])
            status.configure(text=f"Loaded {len(subjects)} subjects")
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            cur.close(); con.close()

    def clear_tree():
        for i in tree.get_children():
            tree.delete(i)

    def load_data():
        subj = subject_cb.get().strip()
        if not subj:
            messagebox.showinfo("Input", "Please select a subject first.")
            return
        filt = filter_entry.get().strip().lower()
        clear_tree()
        con = connectDB()
        cur = con.cursor()
        try:
            cur.execute("SELECT a.roll_no, a.reg_no, a.name, a.attendance FROM attendance a WHERE a.subject=? ORDER BY a.roll_no", (subj,))
            rows = cur.fetchall()
            count = 0
            for roll, reg, name, att in rows:
                display = True
                if filt:
                    if filt not in str(roll).lower() and filt not in (name or '').lower():
                        display = False
                if display:
                    tree.insert('', 'end', values=(roll, reg, name, att))
                    count += 1
            status.configure(text=f"Showing {count} rows for subject '{subj}'")
            # autosize columns a bit
            for c in cols:
                tree.column(c, width=tkFont.measure(c) + 40)
            # then expand to widest content
            for iid in tree.get_children():
                vals = tree.item(iid)['values']
                for idx, v in enumerate(vals):
                    w = tkFont.measure(str(v)) + 12
                    if tree.column(cols[idx], 'width') < w:
                        tree.column(cols[idx], width=w)
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            cur.close(); con.close()

    def export_csv():
        subj = subject_cb.get().strip()
        if not subj:
            messagebox.showinfo("Input", "Select a subject first.")
            return
        if not tree.get_children():
            messagebox.showinfo("No Data", "No rows to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')], title='Save attendance as CSV')
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for iid in tree.get_children():
                    writer.writerow(tree.item(iid)['values'])
            messagebox.showinfo('Exported', f'Attendance exported to {path}')
        except Exception as e:
            messagebox.showerror('Export Error', str(e))

    # small font helper
    try:
        import tkinter.font as tkfont
        tkFont = tkfont.Font(root=win)
    except Exception:
        class _FakeFont:
            def measure(self, s):
                return 8 * len(s)
        tkFont = _FakeFont()

    # wire buttons
    load_btn.config(command=load_data)
    refresh_btn.config(command=load_subjects)
    export_btn.config(command=export_csv)

    # allow Enter in filter to reload
    filter_entry.bind('<Return>', lambda e: load_data())

    # initial load of subjects
    load_subjects()

    # keyboard focus and accessibility
    subject_cb.focus_set()

# --- Additional Report GUIs ---

def total_internal_gui():
    win = tk.Toplevel(root)
    win.title("Total Internal")
    win.geometry("820x480")
    win.transient(root)
    win.grab_set()
    subj = simpledialog.askstring("Subject", "Enter subject:")
    if not subj:
        win.destroy(); return
    cols = ("Roll", "Reg", "Name", "Att", "M1", "M2", "M3", "Total")
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor='w')
    vsb = ttk.Scrollbar(win, orient='vertical', command=tree.yview)
    hsb = ttk.Scrollbar(win, orient='horizontal', command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    tree.pack(fill='both', expand=True, padx=8, pady=8)
    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')
    con = connectDB(); cur = con.cursor()
    try:
        cur.execute(
            "SELECT s.roll_no, s.reg_no, s.name, COALESCE(a.attendance,0) AS att, COALESCE(m.mid1,0) AS m1, COALESCE(m.mid2,0) AS m2, COALESCE(m.mid3,0) AS m3, "
            "(COALESCE(a.attendance,0)+COALESCE(m.mid1,0)+COALESCE(m.mid2,0)+COALESCE(m.mid3,0)) AS total "
            "FROM student s JOIN attendance a ON a.roll_no=s.roll_no AND a.subject=? LEFT JOIN mid_mark m ON m.roll_no=s.roll_no AND m.subject=? ORDER BY s.roll_no",
            (subj, subj)
        )
        for row in cur.fetchall():
            tree.insert('', 'end', values=row)
    except Exception as e:
        messagebox.showerror('SQL Error', str(e))
    finally:
        cur.close(); con.close()


def course_cgpa_gui():
    win = tk.Toplevel(root)
    win.title("Course CGPA")
    win.geometry("720x480")
    win.transient(root)
    win.grab_set()
    course = simpledialog.askstring("Course", "Enter course (subject) name:")
    if not course:
        win.destroy(); return
    semester = simpledialog.askstring("Semester", "Enter semester (e.g. Fall-2024):")
    if not semester:
        win.destroy(); return
    cols = ("Roll", "Name", "CGPA")
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor='w')
    tree.pack(fill='both', expand=True, padx=8, pady=8)
    con = connectDB(); cur = con.cursor()
    try:
        cur.execute("SELECT DISTINCT s.roll_no, s.name FROM student s JOIN attendance a ON s.roll_no = a.roll_no WHERE a.subject=?", (course,))
        students = cur.fetchall()
        for roll, name in students:
            cur.execute("SELECT COALESCE(a.attendance,0), COALESCE(m.mid1,0), COALESCE(m.mid2,0), COALESCE(m.mid3,0) FROM attendance a LEFT JOIN mid_mark m ON m.roll_no=a.roll_no AND m.subject=a.subject WHERE a.roll_no=? AND a.subject=?", (roll, course))
            row = cur.fetchone()
            total_internal = sum(row) if row else 0
            cur.execute("SELECT result FROM session_semester_result WHERE roll_no=? AND semester=?", (roll, semester + f" ({course})"))
            sem_row = cur.fetchone()
            if not sem_row:
                cgpa = 'N/A'
            else:
                try:
                    semester_result = float(sem_row[0])
                    total_marks = (total_internal / 40.0 * 40.0) + (semester_result / 60.0 * 60.0)
                    if total_marks > 100:
                        total_marks = 100
                    cgpa = round((total_marks / 100.0) * 4.0, 2)
                except Exception:
                    cgpa = 'N/A'
            tree.insert('', 'end', values=(roll, name, cgpa))
    except Exception as e:
        messagebox.showerror('SQL Error', str(e))
    finally:
        cur.close(); con.close()


def semester_total_cgpa_gui():
    win = tk.Toplevel(root)
    win.title("Semester Total CGPA")
    win.geometry("720x480")
    win.transient(root)
    win.grab_set()
    session = simpledialog.askstring("Session", "Enter session:")
    if not session:
        win.destroy(); return
    semester = simpledialog.askstring("Semester", "Enter semester:")
    if not semester:
        win.destroy(); return
    cols = ("Roll", "Name", "CGPA")
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor='w')
    tree.pack(fill='both', expand=True, padx=8, pady=8)
    con = connectDB(); cur = con.cursor()
    try:
        cur.execute("SELECT DISTINCT s.roll_no, s.name FROM student s JOIN session_semester_result ssr ON s.roll_no = ssr.roll_no WHERE s.session = ? AND ssr.semester LIKE ? ORDER BY s.roll_no", (session, semester + ' (%',))
        students = cur.fetchall()
        for roll, name in students:
            cur.execute("SELECT semester, result FROM session_semester_result WHERE roll_no=? AND session=? AND semester LIKE ?", (roll, session, semester + ' (%',))
            subject_results = cur.fetchall()
            total_points = 0
            subject_count = 0
            for sem, result in subject_results:
                if '(' in sem and sem.endswith(')'):
                    subject = sem[sem.find('(')+1:-1]
                else:
                    subject = sem
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
                except Exception:
                    continue
            avg_cgpa = round(total_points / subject_count, 2) if subject_count > 0 else 'N/A'
            tree.insert('', 'end', values=(roll, name, avg_cgpa))
    except Exception as e:
        messagebox.showerror('SQL Error', str(e))
    finally:
        cur.close(); con.close()

if __name__ == "__main__":
    main_gui()
