#include <bits/stdc++.h>
using namespace std;

struct Student {
    string name, id, regNo, session, dept, phone;
    string attendance, midterm, cgpa;
};

struct Teacher {
    string name, subject, dept, designation, phone, email;
};

void addStudent();
void deleteStudent();
void modifyStudent();
void addTeacher();
void deleteTeacher();
void modifyTeacher();
void sendNotice(string sender);
void setAttendance();
void updateMidterm();
void updateCGPA();
void displayAttendance();
void displayMidterm();
void displayCGPA();
void displayNotice();
void displayAllStudents();


int main() {
    int choice;
    while (true) {
        cout << "\n===== MAIN MENU =====";
        cout << "\n1. Admin";
        cout << "\n2. Teacher";
        cout << "\n3. Student";
        cout << "\n4. Exit";
        cout<<  "\n5. Display All Students";
        cout << "\nEnter choice: ";
        cin >> choice;
        cin.ignore();

        if (choice == 1) {
            int ch;
            cout << "\n--- ADMIN MENU ---";
            cout << "\n1. Add Student";
            cout << "\n2. Delete Student";
            cout << "\n3. Modify Student";
            cout << "\n4. Add Teacher";
            cout << "\n5. Delete Teacher";
            cout << "\n6. Modify Teacher";
            cout << "\n7. Send Notice";
            cout << "\nEnter choice: ";
            cin >> ch; cin.ignore();

            if (ch == 1) addStudent();
            else if (ch == 2) deleteStudent();
            else if (ch == 3) modifyStudent();
            else if (ch == 4) addTeacher();
            else if (ch == 5) deleteTeacher();
            else if (ch == 6) modifyTeacher();
            else if (ch == 7) sendNotice("Admin");

        } else if (choice == 2) {
            int ch;
            cout << "\n--- TEACHER MENU ---";
            cout << "\n1. Set Attendance";
            cout << "\n2. Update Midterm Marks";
            cout << "\n3. Update CGPA";
            cout << "\n4. Send Notice";
            cout << "\nEnter choice: ";
            cin >> ch; cin.ignore();

            if (ch == 1) setAttendance();
            else if (ch == 2) updateMidterm();
            else if (ch == 3) updateCGPA();
            else if (ch == 4) sendNotice("Teacher");

        } else if (choice == 3) {
            int ch;
            cout << "\n--- STUDENT MENU ---";
            cout << "\n1. Display Attendance";
            cout << "\n2. Display Midterm Marks";
            cout << "\n3. Display CGPA";
            cout << "\n4. Display Notice";
            cout << "\nEnter choice: ";
            cin >> ch; cin.ignore();

            if (ch == 1) displayAttendance();
            else if (ch == 2) displayMidterm();
            else if (ch == 3) displayCGPA();
            else if (ch == 4) displayNotice();

        } else if (choice == 4) break;
        else if (choice == 5) displayAllStudents();
        else cout << "Invalid choice!\n";
    }
    return 0;
}

// ================= FILE FUNCTIONS =================

void displayAllStudents() {
    ifstream file("students.dat");
    if (!file) {
        cout << "No student records found.\n";
        return;
    }

    string line;
    cout << "\n===== All Students =====\n";
    cout << left << setw(15) << "Name" 
         << setw(10) << "ID" 
         << setw(15) << "Reg No" 
         << setw(10) << "Session"
         << setw(15) << "Dept"
         << setw(15) << "Phone"
         << setw(12) << "Attendance"
         << setw(10) << "Midterm"
         << setw(6) << "CGPA" << "\n";

    cout << string(100, '-') << "\n";

    while (getline(file, line)) {
        vector<string> parts;
        stringstream ss(line);
        string part;
        while (getline(ss, part, '|')) parts.push_back(part);

        if (parts.size() >= 9) {
            cout << left << setw(15) << parts[0]
                 << setw(10) << parts[1]
                 << setw(15) << parts[2]
                 << setw(10) << parts[3]
                 << setw(15) << parts[4]
                 << setw(15) << parts[5]
                 << setw(12) << parts[6]
                 << setw(10) << parts[7]
                 << setw(6)  << parts[8] << "\n";
        }
    }
    file.close();
}

void addStudent() {
    Student s;
    cout << "Enter Name: "; getline(cin, s.name);
    cout << "Enter ID: "; getline(cin, s.id);
    cout << "Enter Registration No: "; getline(cin, s.regNo);
    cout << "Enter Session: "; getline(cin, s.session);
    cout << "Enter Department: "; getline(cin, s.dept);
    cout << "Enter Phone: "; getline(cin, s.phone);

    int subCount;
    cout << "Enter number of subjects: ";
    cin >> subCount; cin.ignore();

    string subjects = "";
    for (int i = 0; i < subCount; i++) {
        string sub;
        cout << "Enter subject name: ";
        getline(cin, sub);
        subjects += sub + ":N/A";
        if (i != subCount - 1) subjects += ",";
    }

    string midterm = "N/A", cgpa = "N/A";

    ofstream file("students.dat", ios::app);
    file << s.name << "|" << s.id << "|" << s.regNo << "|" << s.session << "|"
         << s.dept << "|" << s.phone << "|" << subjects << "|" << midterm << "|" << cgpa << "\n";
    file.close();

    cout << "Student added successfully!\n";
}


void deleteStudent() {
    string id;
    cout << "Enter Student ID to delete: ";
    getline(cin, id);

    ifstream file("students.dat");
    ofstream temp("temp.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        if (line.find("|" + id + "|") == string::npos) {
            temp << line << "\n";
        } else {
            found = true;
        }
    }
    file.close();
    temp.close();
    remove("students.dat");
    rename("temp.dat", "students.dat");

    if (found) cout << "Student deleted successfully!\n";
    else cout << "Student not found!\n";
}

void modifyStudent() {
    string id;
    cout << "Enter Student ID to modify: ";
    getline(cin, id);

    ifstream file("students.dat");
    ofstream temp("temp.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        if (line.find("|" + id + "|") != string::npos) {
            found = true;
            Student s;
            cout << "Enter New Name: "; getline(cin, s.name);
            cout << "Enter New Registration No: "; getline(cin, s.regNo);
            cout << "Enter New Session: "; getline(cin, s.session);
            cout << "Enter New Department: "; getline(cin, s.dept);
            cout << "Enter New Phone: "; getline(cin, s.phone);
            s.id = id;
            s.attendance = "N/A";
            s.midterm = "N/A";
            s.cgpa = "N/A";
            temp << s.name << "|" << s.id << "|" << s.regNo << "|" << s.session << "|" 
                 << s.dept << "|" << s.phone << "|" << s.attendance << "|" << s.midterm << "|" << s.cgpa << "\n";
        } else {
            temp << line << "\n";
        }
    }
    file.close();
    temp.close();
    remove("students.dat");
    rename("temp.dat", "students.dat");

    if (found) cout << "Student modified successfully!\n";
    else cout << "Student not found!\n";
}

void addTeacher() {
    Teacher t;
    cout << "Enter Name: "; getline(cin, t.name);
    cout << "Enter Subject: "; getline(cin, t.subject);
    cout << "Enter Department: "; getline(cin, t.dept);
    cout << "Enter Designation: "; getline(cin, t.designation);
    cout << "Enter Phone: "; getline(cin, t.phone);
    cout << "Enter G-mail: "; getline(cin, t.email);

    ofstream file("teachers.dat", ios::app);
    file << t.name << "|" << t.subject << "|" << t.dept << "|" 
         << t.designation << "|" << t.phone << "|" << t.email << "\n";
    file.close();
    cout << "Teacher added successfully!\n";
}

void deleteTeacher() {
    string name;
    cout << "Enter Teacher Name to delete: ";
    getline(cin, name);

    ifstream file("teachers.dat");
    ofstream temp("temp.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        if (line.find(name + "|") == string::npos) {
            temp << line << "\n";
        } else {
            found = true;
        }
    }
    file.close();
    temp.close();
    remove("teachers.dat");
    rename("temp.dat", "teachers.dat");

    if (found) cout << "Teacher deleted successfully!\n";
    else cout << "Teacher not found!\n";
}

void modifyTeacher() {
    string name;
    cout << "Enter Teacher Name to modify: ";
    getline(cin, name);

    ifstream file("teachers.dat");
    ofstream temp("temp.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        if (line.find(name + "|") != string::npos) {
            found = true;
            Teacher t;
            cout << "Enter New Subject: "; getline(cin, t.subject);
            cout << "Enter New Department: "; getline(cin, t.dept);
            cout << "Enter New Designation: "; getline(cin, t.designation);
            cout << "Enter New Phone: "; getline(cin, t.phone);
            cout << "Enter New G-mail: "; getline(cin, t.email);
            t.name = name;
            temp << t.name << "|" << t.subject << "|" << t.dept << "|" 
                 << t.designation << "|" << t.phone << "|" << t.email << "\n";
        } else {
            temp << line << "\n";
        }
    }
    file.close();
    temp.close();
    remove("teachers.dat");
    rename("temp.dat", "teachers.dat");

    if (found) cout << "Teacher modified successfully!\n";
    else cout << "Teacher not found!\n";
}

void sendNotice(string sender) {
    string notice;
    cout << "Enter Notice: ";
    getline(cin, notice);

    ofstream file("notice.txt", ios::app);
    file << sender << ": " << notice << "\n";
    file.close();
    cout << "Notice sent!\n";
}

void setAttendance() {
    string id;
    cout << "Enter Student ID: ";
    getline(cin, id);

    ifstream file("students.dat");
    ofstream temp("temp.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        vector<string> parts;
        stringstream ss(line);
        string part;
        while (getline(ss, part, '|')) parts.push_back(part);

        if (parts.size() >= 9 && parts[1] == id) {
            found = true;

            // Extract subjects
            vector<string> subjectList;
            stringstream subStream(parts[6]);
            string subPart;
            while (getline(subStream, subPart, ',')) subjectList.push_back(subPart);

            cout << "\nSubjects for " << parts[0] << ":\n";
            for (int i = 0; i < subjectList.size(); i++) {
                cout << i+1 << ". " << subjectList[i] << "\n";
            }

            int choice;
            cout << "Enter subject number to update: ";
            cin >> choice;
            cin.ignore();

            if (choice >= 1 && choice <= subjectList.size()) {
                string &selected = subjectList[choice - 1];
                size_t pos = selected.find(':');
                if (pos != string::npos) {
                    string newAtt;
                    cout << "Enter new attendance (%): ";
                    getline(cin, newAtt);
                    selected = selected.substr(0, pos+1) + newAtt;
                }
            }

            // Rebuild subject string
            string updatedSubjects = "";
            for (int i = 0; i < subjectList.size(); i++) {
                updatedSubjects += subjectList[i];
                if (i != subjectList.size()-1) updatedSubjects += ",";
            }

            temp << parts[0] << "|" << parts[1] << "|" << parts[2] << "|" << parts[3] << "|"
                 << parts[4] << "|" << parts[5] << "|" << updatedSubjects << "|" 
                 << parts[7] << "|" << parts[8] << "\n";
        }
        else {
            temp << line << "\n";
        }
    }
    file.close();
    temp.close();
    remove("students.dat");
    rename("temp.dat", "students.dat");

    if (found) cout << "Attendance updated!\n";
    else cout << "Student not found!\n";
}
void updateMidterm() {
    string id;
    cout << "Enter Student ID: ";
    getline(cin, id);

    ifstream file("students.dat");
    ofstream temp("temp.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        vector<string> parts;
        stringstream ss(line);
        string part;
        while (getline(ss, part, '|')) parts.push_back(part);

        if (parts.size() >= 9 && parts[1] == id) {
            found = true;

            // Extract subjects from parts[6]
            vector<string> subjects;
            stringstream subStream(parts[6]);
            string subPart;
            while (getline(subStream, subPart, ',')) subjects.push_back(subPart);

            cout << "\nSubjects for " << parts[0] << ":\n";
            for (int i = 0; i < subjects.size(); i++) {
                size_t pos = subjects[i].find(':');
                string subjectName = (pos != string::npos) ? subjects[i].substr(0, pos) : subjects[i];
                cout << i + 1 << ". " << subjectName << "\n";
            }

            int choice;
            cout << "Enter subject number to update: ";
            cin >> choice;
            cin.ignore();

            if (choice >= 1 && choice <= subjects.size()) {
                size_t pos = subjects[choice - 1].find(':');
                string subjectName = (pos != string::npos) ? subjects[choice - 1].substr(0, pos) : subjects[choice - 1];
                
                string marks;
                cout << "Enter new midterm mark: ";
                getline(cin, marks);

                // Update marks in parts[7]
                if (parts[7] == "N/A") {
                    parts[7] = subjectName + ":" + marks;
                } else {
                    parts[7] += "," + subjectName + ":" + marks;
                }
            }

            // Write back to file with updated marks in parts[7]
            temp << parts[0] << "|" << parts[1] << "|" << parts[2] << "|" << parts[3] << "|"
                 << parts[4] << "|" << parts[5] << "|" << parts[6] << "|" 
                 << parts[7] << "|" << parts[8] << "\n";
        }
        else {
            temp << line << "\n";
        }
    }
    file.close();
    temp.close();
    remove("students.dat");
    rename("temp.dat", "students.dat");

    if (found) cout << "Midterm marks updated!\n";
    else cout << "Student not found!\n";
}

void updateCGPA() {
    string id, cgpa;
    cout << "Enter Student ID: ";
    getline(cin, id);
    cout << "Enter CGPA: ";
    getline(cin, cgpa);

    ifstream file("students.dat");
    ofstream temp("temp.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        vector<string> parts;
        stringstream ss(line);
        string part;
        while (getline(ss, part, '|')) parts.push_back(part);

        if (parts.size() >= 9 && parts[1] == id) {
            found = true;
            parts[8] = cgpa;
            temp << parts[0] << "|" << parts[1] << "|" << parts[2] << "|" << parts[3] << "|" 
                 << parts[4] << "|" << parts[5] << "|" << parts[6] << "|" << parts[7] << "|" << parts[8] << "\n";
        } else temp << line << "\n";
    }
    file.close();
    temp.close();
    remove("students.dat");
    rename("temp.dat", "students.dat");

    if (found) cout << "CGPA updated!\n";
    else cout << "Student not found!\n";
}

void displayAttendance() {
    string id;
    cout << "Enter Student ID: ";
    getline(cin, id);

    ifstream file("students.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        vector<string> parts;
        stringstream ss(line);
        string part;
        while (getline(ss, part, '|')) parts.push_back(part);

        if (parts.size() >= 9 && parts[1] == id) {
            found = true;

            cout << "\nAttendance for " << parts[0] << ":\n";
            stringstream subStream(parts[6]);
            string subPart;
            while (getline(subStream, subPart, ',')) {
                cout << " - " << subPart << "%\n";
            }
            break;
        }
    }
    file.close();
    if (!found) cout << "Student not found!\n";
}


void displayMidterm() {
    string id;
    cout << "Enter Student ID: ";
    getline(cin, id);

    ifstream file("students.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        vector<string> parts;
        stringstream ss(line);
        string part;

        while (getline(ss, part, '|')) {
            parts.push_back(part);
        }

        if (parts.size() >= 9 && parts[1] == id) {
            found = true;
            cout << "\nMidterm Marks for " << parts[0] << ":\n";
            cout << " - " << parts[7] << "\n";
            break;
        }
    }

    file.close();

    if (!found) {
        cout << "Student not found!\n";
    }
}



void displayCGPA() {
    string id;
    cout << "Enter Student ID: ";
    getline(cin, id);

    ifstream file("students.dat");
    string line;
    bool found = false;

    while (getline(file, line)) {
        vector<string> parts;
        stringstream ss(line);
        string part;
        while (getline(ss, part, '|')) parts.push_back(part);

        if (parts.size() >= 9 && parts[1] == id) {
            cout << "CGPA: " << parts[8] << "\n";
            found = true;
            break;
        }
    }
    file.close();
    if (!found) cout << "Student not found!\n";
}

void displayNotice() {
    ifstream file("notice.txt");
    string line;
    cout << "\n--- Notices ---\n";
    while (getline(file, line)) {
        cout << line << "\n";
    }
    file.close();
}
