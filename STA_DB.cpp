// main.cpp
#include <bits/stdc++.h>
#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/prepared_statement.h>
#include <cppconn/resultset.h>

using namespace std;

// ====== DB CONFIG - change for your MySQL ======
const string DB_URI  = "D:\project2.2\mysql-connector-c++\lib\mysqlcppconn.lib";
const string DB_USER = "root";
const string DB_PASS = "a1l2a3m4i5n6";
const string DB_NAME = "college_db";
// ===============================================

std::unique_ptr<sql::Connection> connectDB() {
    sql::Driver* driver = get_driver_instance();
    std::unique_ptr<sql::Connection> con(driver->connect(DB_URI, DB_USER, DB_PASS));
    con->setSchema(DB_NAME);
    return con;
}

// ------- small helpers -------
void pauseLine() {
    cout << "\nPress ENTER to continue..."; cin.ignore(numeric_limits<streamsize>::max(), '\n');
}
int askInt(const string& prompt) {
    cout << prompt;
    int x; while(!(cin >> x)) { cin.clear(); cin.ignore(1e9, '\n'); cout << "Invalid. Try again: "; }
    cin.ignore(1e9, '\n');
    return x;
}
string askStr(const string& prompt) {
    cout << prompt;
    string s; getline(cin, s);
    return s;
}
void printRowLine(int w=80){ cout << string(w,'-') << "\n"; }

// ------- ADMIN PANEL -------
void adminAddStudent(sql::Connection* con){
    int roll = askInt("Roll No: ");
    string reg = askStr("Reg No: ");
    string name = askStr("Name: ");
    string phone = askStr("Phone: ");
    string email = askStr("Email: ");
    string dept = askStr("Dept: ");

    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("INSERT INTO student(roll_no,reg_no,name,phone,email,dept) VALUES(?,?,?,?,?,?)")
    );
    ps->setInt(1, roll); ps->setString(2, reg); ps->setString(3, name);
    ps->setString(4, phone); ps->setString(5, email); ps->setString(6, dept);
    ps->execute();

    // also seed c_gpa row (optional but convenient)
    auto ps2 = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("INSERT INTO c_gpa(roll_no, reg_no, name, c_gpa) VALUES(?,?,?,0.0)")
    );
    ps2->setInt(1, roll); ps2->setString(2, reg); ps2->setString(3, name);
    ps2->execute();

    cout << "Student added.\n";
}

void adminUpdateStudent(sql::Connection* con){
    int roll = askInt("Roll No to update: ");
    string phone = askStr("New phone (or blank to skip): ");
    string email = askStr("New email (or blank to skip): ");
    string dept  = askStr("New dept (or blank to skip): ");

    if(!phone.empty()){
        auto ps = std::unique_ptr<sql::PreparedStatement>(
            con->prepareStatement("UPDATE student SET phone=? WHERE roll_no=?")
        );
        ps->setString(1, phone); ps->setInt(2, roll); ps->execute();
    }
    if(!email.empty()){
        auto ps = std::unique_ptr<sql::PreparedStatement>(
            con->prepareStatement("UPDATE student SET email=? WHERE roll_no=?")
        );
        ps->setString(1, email); ps->setInt(2, roll); ps->execute();
    }
    if(!dept.empty()){
        auto ps = std::unique_ptr<sql::PreparedStatement>(
            con->prepareStatement("UPDATE student SET dept=? WHERE roll_no=?")
        );
        ps->setString(1, dept); ps->setInt(2, roll); ps->execute();
    }
    cout << "Student updated.\n";
}

void adminDeleteStudent(sql::Connection* con){
    int roll = askInt("Roll No to delete: ");
    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("DELETE FROM student WHERE roll_no=?")
    );
    ps->setInt(1, roll);
    ps->execute();
    cout << "Deleted (if existed). Related rows cascade removed.\n";
}

void adminAddTeacher(sql::Connection* con){
    int id = askInt("Teacher ID: ");
    string name = askStr("Name: ");
    string subject = askStr("Subject: ");
    string dept = askStr("Dept: ");
    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("INSERT INTO teacher(id,name,subject,dept) VALUES(?,?,?,?)")
    );
    ps->setInt(1,id); ps->setString(2,name); ps->setString(3,subject); ps->setString(4,dept);
    ps->execute();
    cout << "Teacher added.\n";
}

void adminUpdateTeacher(sql::Connection* con){
    int id = askInt("Teacher ID to update: ");
    string name = askStr("New name (blank skip): ");
    string subject = askStr("New subject (blank skip): ");
    string dept = askStr("New dept (blank skip): ");

    if(!name.empty()){
        auto ps = std::unique_ptr<sql::PreparedStatement>(
            con->prepareStatement("UPDATE teacher SET name=? WHERE id=?")
        ); ps->setString(1,name); ps->setInt(2,id); ps->execute();
    }
    if(!subject.empty()){
        auto ps = std::unique_ptr<sql::PreparedStatement>(
            con->prepareStatement("UPDATE teacher SET subject=? WHERE id=?")
        ); ps->setString(1,subject); ps->setInt(2,id); ps->execute();
    }
    if(!dept.empty()){
        auto ps = std::unique_ptr<sql::PreparedStatement>(
            con->prepareStatement("UPDATE teacher SET dept=? WHERE id=?")
        ); ps->setString(1,dept); ps->setInt(2,id); ps->execute();
    }
    cout << "Teacher updated.\n";
}

void adminDeleteTeacher(sql::Connection* con){
    int id = askInt("Teacher ID to delete: ");
    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("DELETE FROM teacher WHERE id=?")
    ); ps->setInt(1,id); ps->execute();
    cout << "Deleted (if existed).\n";
}

void adminUpdateCGPA(sql::Connection* con){
    int roll = askInt("Roll No: ");
    double cg = stod(askStr("New C-GPA (e.g. 3.75): "));
    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("UPDATE c_gpa SET c_gpa=? WHERE roll_no=?")
    ); ps->setDouble(1,cg); ps->setInt(2,roll); ps->execute();
    cout << "C-GPA updated.\n";
}

void adminPanel(sql::Connection* con){
    while(true){
        printRowLine();
        cout << "ADMIN PANEL\n"
             << "1) Add Student\n2) Update Student\n3) Delete Student\n"
             << "4) Add Teacher\n5) Update Teacher\n6) Delete Teacher\n"
             << "7) Update C-GPA\n0) Back\n";
        int ch = askInt("Choose: ");
        if(ch==0) break;
        try{
            if(ch==1) adminAddStudent(con);
            else if(ch==2) adminUpdateStudent(con);
            else if(ch==3) adminDeleteStudent(con);
            else if(ch==4) adminAddTeacher(con);
            else if(ch==5) adminUpdateTeacher(con);
            else if(ch==6) adminDeleteTeacher(con);
            else if(ch==7) adminUpdateCGPA(con);
        } catch(sql::SQLException &e){
            cerr << "SQL Error: " << e.what() << "\n";
        }
        pauseLine();
    }
}

// ------- TEACHER PANEL -------
string teacherSubjectById(sql::Connection* con, int tid){
    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("SELECT subject FROM teacher WHERE id=?")
    ); ps->setInt(1, tid);
    auto rs = std::unique_ptr<sql::ResultSet>(ps->executeQuery());
    if(rs->next()) return rs->getString(1);
    return "";
}

void teacherUpdateAttendance(sql::Connection* con, int tid){
    string subj = teacherSubjectById(con, tid);
    if(subj.empty()){ cout << "Teacher not found.\n"; return; }
    cout << "You can update for subject: " << subj << "\n";

    int roll = askInt("Student Roll No: ");
    int att  = askInt("Attendance points: ");

    // Upsert pattern: try update; if 0 rows, insert using student info
    auto upd = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("UPDATE attendance SET attendance=?, name=(SELECT name FROM student WHERE roll_no=?), reg_no=(SELECT reg_no FROM student WHERE roll_no=?) WHERE roll_no=? AND subject=?")
    );
    upd->setInt(1, att); upd->setInt(2, roll); upd->setInt(3, roll);
    upd->setInt(4, roll); upd->setString(5, subj);
    int affected = upd->executeUpdate();

    if(affected==0){
        auto ins = std::unique_ptr<sql::PreparedStatement>(
            con->prepareStatement(
                "INSERT INTO attendance(roll_no, reg_no, name, subject, attendance) "
                "SELECT s.roll_no, s.reg_no, s.name, ?, ? FROM student s WHERE s.roll_no=?"
            )
        );
        ins->setString(1, subj); ins->setInt(2, att); ins->setInt(3, roll);
        ins->execute();
    }
    cout << "Attendance updated.\n";
}

void teacherUpdateMid(sql::Connection* con, int tid){
    string subj = teacherSubjectById(con, tid);
    if(subj.empty()){ cout << "Teacher not found.\n"; return; }
    cout << "You can update for subject: " << subj << "\n";

    int roll = askInt("Student Roll No: ");
    int which = askInt("Which mid? (1/2/3): ");
    if(which<1 || which>3){ cout << "Invalid mid.\n"; return; }
    int mark = askInt("Marks: ");

    string col = (which==1?"mid1":which==2?"mid2":"mid3");

    // Update then insert if needed
    {
        string q = "UPDATE mid_mark SET "+col+"=?, name=(SELECT name FROM student WHERE roll_no=?), reg_no=(SELECT reg_no FROM student WHERE roll_no=?) WHERE roll_no=? AND subject=?";
        auto upd = std::unique_ptr<sql::PreparedStatement>(con->prepareStatement(q));
        upd->setInt(1, mark); upd->setInt(2, roll); upd->setInt(3, roll);
        upd->setInt(4, roll); upd->setString(5, subj);
        int n = upd->executeUpdate();
        if(n==0){
            auto ins = std::unique_ptr<sql::PreparedStatement>(
                con->prepareStatement(
                    "INSERT INTO mid_mark(roll_no, reg_no, name, subject, mid1, mid2, mid3) "
                    "SELECT s.roll_no, s.reg_no, s.name, ?, 0, 0, 0 FROM student s WHERE s.roll_no=?"
                )
            );
            ins->setString(1, subj); ins->setInt(2, roll);
            ins->execute();
            // set the chosen mid after insert
            auto upd2 = std::unique_ptr<sql::PreparedStatement>(
                con->prepareStatement(("UPDATE mid_mark SET "+col+"=? WHERE roll_no=? AND subject=?").c_str())
            );
            upd2->setInt(1, mark); upd2->setInt(2, roll); upd2->setString(3, subj);
            upd2->execute();
        }
    }
    cout << "Mid-" << which << " updated.\n";
}

void teacherPanel(sql::Connection* con){
    int tid = askInt("Enter Teacher ID: ");
    while(true){
        printRowLine();
        cout << "TEACHER PANEL (ID="<<tid<<")\n"
             << "1) Update Attendance\n2) Update Mid (1/2/3)\n0) Back\n";
        int ch = askInt("Choose: "); if(ch==0) break;
        try{
            if(ch==1) teacherUpdateAttendance(con, tid);
            else if(ch==2) teacherUpdateMid(con, tid);
        } catch(sql::SQLException &e){ cerr << "SQL Error: " << e.what() << "\n"; }
        pauseLine();
    }
}

// ------- STUDENT PANEL -------
void studentPanel(sql::Connection* con){
    int roll = askInt("Enter your Roll No: ");
    printRowLine();
    cout << "STUDENT INFO\n";

    // Attendance (all subjects)
    cout << "\nAttendance:\n";
    auto psA = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("SELECT subject, attendance FROM attendance WHERE roll_no=? ORDER BY subject")
    ); psA->setInt(1, roll);
    auto rsA = std::unique_ptr<sql::ResultSet>(psA->executeQuery());
    while(rsA->next()){
        cout << "  " << rsA->getString(1) << " : " << rsA->getInt(2) << "\n";
    }

    // Mid marks (all subjects)
    cout << "\nMid Marks:\n";
    auto psM = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("SELECT subject, mid1, mid2, mid3 FROM mid_mark WHERE roll_no=? ORDER BY subject")
    ); psM->setInt(1, roll);
    auto rsM = std::unique_ptr<sql::ResultSet>(psM->executeQuery());
    while(rsM->next()){
        cout << "  " << rsM->getString(1) << " : mid1="<<rsM->getInt(2)
             << ", mid2="<<rsM->getInt(3) << ", mid3="<<rsM->getInt(4) << "\n";
    }

    // C-GPA
    cout << "\nC-GPA:\n";
    auto psC = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement("SELECT c_gpa FROM c_gpa WHERE roll_no=?")
    ); psC->setInt(1, roll);
    auto rsC = std::unique_ptr<sql::ResultSet>(psC->executeQuery());
    if(rsC->next()) cout << "  " << rsC->getDouble(1) << "\n";
    else cout << "  Not set.\n";
    cout << "\n";
    pauseLine();
}

// ------- ATTENDANCE SHEET PANEL -------
void attendanceSheetPanel(sql::Connection* con){
    string subj = askStr("Subject: ");
    printRowLine();
    cout << "ATTENDANCE SHEET for " << subj << "\n";
    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement(
            "SELECT a.roll_no, a.reg_no, a.name, a.attendance "
            "FROM attendance a WHERE a.subject=? ORDER BY a.roll_no"
        )
    ); ps->setString(1, subj);
    auto rs = std::unique_ptr<sql::ResultSet>(ps->executeQuery());
    cout << left << setw(10) << "Roll" << setw(16) << "Reg" << setw(24) << "Name" << "Attendance\n";
    while(rs->next()){
        cout << left << setw(10) << rs->getInt(1)
             << setw(16) << rs->getString(2)
             << setw(24) << rs->getString(3)
             << rs->getInt(4) << "\n";
    }
    pauseLine();
}

// ------- TOTAL INTERNAL PANEL -------
void totalInternalPanel(sql::Connection* con){
    string subj = askStr("Subject: ");
    printRowLine();
    cout << "TOTAL INTERNAL for " << subj << " (attendance + mid1 + mid2 + mid3)\n";

    auto ps = std::unique_ptr<sql::PreparedStatement>(
        con->prepareStatement(
            "SELECT s.roll_no, s.reg_no, s.name, "
            "COALESCE(a.attendance,0) AS att, "
            "COALESCE(m.mid1,0) AS m1, COALESCE(m.mid2,0) AS m2, COALESCE(m.mid3,0) AS m3, "
            "(COALESCE(a.attendance,0)+COALESCE(m.mid1,0)+COALESCE(m.mid2,0)+COALESCE(m.mid3,0)) AS total "
            "FROM student s "
            "LEFT JOIN attendance a ON a.roll_no=s.roll_no AND a.subject=? "
            "LEFT JOIN mid_mark  m ON m.roll_no=s.roll_no AND m.subject=? "
            "ORDER BY s.roll_no"
        )
    );
    ps->setString(1, subj);
    ps->setString(2, subj);
    auto rs = std::unique_ptr<sql::ResultSet>(ps->executeQuery());

    cout << left << setw(8) << "Roll" << setw(14) << "Reg" << setw(22) << "Name"
         << setw(6) << "Att" << setw(6) << "M1" << setw(6) << "M2" << setw(6) << "M3" << "Total\n";
    while(rs->next()){
        cout << left << setw(8)  << rs->getInt("roll_no")
             << setw(14) << rs->getString("reg_no")
             << setw(22) << rs->getString("name")
             << setw(6)  << rs->getInt("att")
             << setw(6)  << rs->getInt("m1")
             << setw(6)  << rs->getInt("m2")
             << setw(6)  << rs->getInt("m3")
             << rs->getInt("total") << "\n";
    }
    pauseLine();
}

// ------- MAIN MENU -------
int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    try{
        auto con = connectDB();
        while(true){
            printRowLine();
            cout << "MAIN MENU\n"
                 << "1) Admin Panel\n"
                 << "2) Teacher Panel\n"
                 << "3) Student Panel\n"
                 << "4) Attendance Sheet Panel\n"
                 << "5) Total Internal Panel\n"
                 << "0) Exit\n";
            int ch = askInt("Choose: ");
            if(ch==0) break;
            if(ch==1) adminPanel(con.get());
            else if(ch==2) teacherPanel(con.get());
            else if(ch==3) studentPanel(con.get());
            else if(ch==4) attendanceSheetPanel(con.get());
            else if(ch==5) totalInternalPanel(con.get());
        }
    } catch(sql::SQLException &e){
        cerr << "FATAL SQL Error: " << e.what() << "\n";
    } catch(std::exception &e){
        cerr << "Error: " << e.what() << "\n";
    }
    return 0;
}
