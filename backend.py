# Code starts here...
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QCompleter
import sys
from PyQt5.QtCore import Qt
from frontend import Ui_MainWindow
import pymysql
from PyQt5 import QtCore, QtWidgets


class FinalProjectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.userid = None  # Initialize the userid attribute
        self.ui.tabWidget.setCurrentIndex(0)  # login page is at index 0 s0 it will show a login page initially
        self.ui.tabWidget.tabBar().setVisible(False)  # all the menu buttons are invisible before successfully login

        # connecting functions on clicking different buttons and menu buttons
        self.ui.login.clicked.connect(self.home)
        self.ui.menu5.aboutToShow.connect(self.cancel)
        self.ui.menu4b.triggered.connect(self.show_exit)
        self.ui.menu4a.triggered.connect(self.logout)
        self.ui.menu1a.triggered.connect(self.hostelreg)
        self.ui.menu1b.triggered.connect(self.roomreg)
        self.ui.menu2a.triggered.connect(self.sreg)
        self.ui.menu2b.triggered.connect(self.ssel)
        self.ui.menu2c.triggered.connect(self.salloc)
        self.hide_menu_options()  # to hide all menu buttons except exit
        self.ui.Savebtn.clicked.connect(self.hreg)
        self.ui.Submit.clicked.connect(self.roomdetails)
        self.ui.submitbtn.clicked.connect(self.studentreg)

        # Create a completer for student name search
        completer = QCompleter()
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.ui.lineEdit_15.setCompleter(completer)
        # to display the hostel list
        conn = pymysql.connect(host='localhost', user='root', password='', db='hostel_management')
        cur = conn.cursor()
        cur.execute("SELECT Hostel_Id, Hostel_Name FROM hostel_mst")
        hostels = cur.fetchall()
        for hostel_id, hostel_name in hostels:
            self.ui.Hostelidinp.addItem(hostel_name)
            self.ui.lineEdit_16.addItem(hostel_name)
        query = "SELECT DISTINCT sr.S_Name,sr.Student_Id FROM student_registration sr WHERE sr.Status = 'S'"
        cur.execute(query)
        student_names = cur.fetchall()
        student_names = [name[0] for name in student_names]
        completer.setModel(QtCore.QStringListModel(student_names, ))
        cur.close()
        conn.close()
        # when currentindex changed it connect to the update function if there is no such year in currentindex then only you have to enter refresh
        # button for retrieve desired rows
        self.ui.comboBox.currentIndexChanged.connect(self.selection)
        self.ui.refresh_btn.clicked.connect(self.submit)

    # function of login button
    def home(self):
        userid = self.ui.lineEdit.text()  # when a user enter anything in userid section it will goes to variable userid
        password = self.ui.lineEdit_2.text()  # when a user enter anything in userid section it will goes to variable password
        conn = pymysql.connect(host="localhost", user="root", password="",
                               db="hostel_management")  # create a object to connect database
        cur = conn.cursor()
        query = "select * from user_mst where User_Id=%s and Password=%s"
        data = cur.execute(query, (userid, password))  # execution of query
        if (len(cur.fetchall()) > 0):  # comparing userid and password that is stored in database
            cur.execute("UPDATE user_mst SET Login_Date=NOW(), Status='A' WHERE User_Id=%s AND Password=%s",
                        (userid, password))
            conn.commit()
            self.userid = userid
            self.ui.tabWidget.setCurrentIndex(1)
            self.show_menu_options()
            conn.close()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Alert ! ")
            msg.setText("Invalid Admin Login Details, Try Again ")
            msg.exec_()

     # function of hostel registration menu button
    def hreg(self):
        hid = self.ui.Hostelidinp_2.text()
        hname = self.ui.Hostelnameinp.text()
        # Check if any field is empty
        if not all([hid, hname]):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Please fill in all fields.  ")
            msg_box.setWindowTitle("Error ! ")
            msg_box.exec_()
            return
        conn = pymysql.connect(host="localhost", user="root", password="", db="hostel_management")
        cur = conn.cursor()
        query1 = "SELECT hostel_id FROM hostel_mst WHERE hostel_id = %s"
        cur.execute(query1, (hid,))
        result = cur.fetchone()
        if result:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("This hostel is already registered")
            msg_box.setWindowTitle("Warning ! ")
            msg_box.exec_()
            return
        query = "INSERT INTO hostel_mst (Hostel_Id, Hostel_Name, Reg_By) VALUES (%s, %s, %s )"
        values = (hid, hname, (self.userid))
        cur.execute(query, values)
        self.ui.Hostelidinp.addItem(hname)  # this will add new added hostel in hostel list in room details
        self.ui.lineEdit_16.addItem(hname)
        conn.commit()
        cur.close()
        conn.close()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Hostel registered successfully!")
        msg_box.setWindowTitle("Success")
        msg_box.exec_()

    # function of Room Details menu button
    def roomdetails(self):
        hname = self.ui.Hostelidinp.currentText()
        fno = self.ui.Floorinp.text()
        rno = self.ui.Roominp.text()
        bno = self.ui.Bedinp.text()
        if not all([hname, fno, rno, bno]):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Error ! ")
            msg_box.setText("Please fill in all fields ")
            msg_box.exec_()
            return
        conn = pymysql.connect(host='localhost', user='root', password='', db='hostel_management')
        cur = conn.cursor()
        query1 = "SELECT Hostel_Id FROM hostel_mst WHERE Hostel_Name = %s"
        cur.execute(query1, (hname,))
        result = cur.fetchone()
        hid = result[0]
        query = "SELECT hostel_id FROM room_mst WHERE hostel_id = %s"
        cur.execute(query, (hid,))
        result = cur.fetchone()
        if result:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Room details of this hostel is already registered")
            msg_box.setWindowTitle("Warning ! ")
            msg_box.exec_()
            return
        query = "INSERT INTO room_mst (hostel_id, Floor_No, Room_No,Total_Bed_No, Reg_By) VALUES (%s, %s, %s, %s, %s)"
        value = (hid, fno, rno, bno, (self.userid))
        cur.execute(query, value)
        conn.commit()
        cur.close()
        conn.close()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Success")
        msg_box.setText("Room Registered Successfully ")
        msg_box.exec_()
        return

    # function of Student registration menu button
    def studentreg(self):
        sid1 = self.ui.lineEdit_3.text()
        sname = self.ui.lineEdit_4.text()
        fname = self.ui.lineEdit_5.text()
        gender = self.ui.Gender.currentText()
        email = self.ui.lineEdit_6.text()
        mobile = self.ui.lineEdit_7.text()
        address = self.ui.lineEdit_8.text()
        percentage = self.ui.lineEdit_9.text()
        year = self.ui.dateEdit.text()
        sid = "%s%s" % (year, sid1)
        # Check if any field is empty
        if not all([sid1, sname, fname, gender, email, mobile, address, percentage, year]):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Please fill in all fields.  ")
            msg_box.setWindowTitle("Error ! ")
            msg_box.exec_()
            return
        conn = pymysql.connect(host="localhost", user="root", password="", db="hostel_management")
        cur = conn.cursor()
        cur.execute("SELECT MAX(Reg_No) FROM student_registration")
        reg_no = cur.fetchone()[0]
        if reg_no is not None:
            reg_no = int(reg_no) + 1
            reg = "%s" % (reg_no)
        else:
            reg_no = 0
            reg = "%s%04d" % (year, reg_no)
        cur.execute("SELECT * FROM student_registration WHERE Student_Id = %s", (sid,))
        result = cur.fetchone()
        if result:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("This student is already registered")
            msg_box.setWindowTitle("Warning")
            msg_box.exec_()
            cur.close()
            conn.close()
            return
        query = "INSERT INTO student_registration (Reg_NO, Student_Id, S_Name, F_Name, Gender, S_Email, S_MobileNo, LastYear_Percentage, Address, Year) VALUES (%s, %s, %s, %s, %s, %s,'+91 ' %s, %s, %s, %s)"
        values = (reg, sid, sname, fname, gender, email, mobile, percentage, address, year)
        cur.execute(query, values)
        conn.commit()
        cur.close()
        conn.close()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Student registered successfully!")
        msg_box.setWindowTitle("Success!")
        msg_box.exec_()

    # function of Student selection menu button
    def selection(self):
        conn = pymysql.connect(host="localhost", user="root", password="", db="hostel_management")
        cur = conn.cursor()
        year = self.ui.comboBox.currentText()
        cur.execute(
            "SELECT `Reg_No`, `Student_Id`, `S_Name`, `F_Name`,`Year`, `Status` FROM `student_registration` WHERE `Year`=%s AND Status='R' ",
            (year,))
        rows = cur.fetchall()
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)
        for row in rows:
            self.ui.tableWidget.insertRow(0)
            for i in range(len(row)):
                # To display data in table widget
                self.ui.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(row[i])))
                if i == 5:  # Check column
                    checkbox = QtWidgets.QCheckBox()
                    checkbox.stateChanged.connect(self.checked)  # Connect to the checked method
                    self.ui.tableWidget.setCellWidget(0, 5, checkbox)  # Set the checkbox in the cell

    def checked(self, state):
        # Handle checkbox state change because we connect checked function when state changed
        pass

    def submit(self):
        selected_rows = []
        for row in range(self.ui.tableWidget.rowCount()):
            checkbox = self.ui.tableWidget.cellWidget(row, 5)
            if checkbox.isChecked():
                selected_rows.append(row)

        if len(selected_rows) > 0:
            # Show confirmation message box
            confirm_box = QMessageBox()
            confirm_box.setIcon(QMessageBox.Question)
            confirm_box.setText("Are you sure to select these students?")
            confirm_box.setWindowTitle("Confirmation")
            confirm_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm_box.setDefaultButton(QMessageBox.No)
            confirm_result = confirm_box.exec_()

            if confirm_result == QMessageBox.Yes:
                conn = pymysql.connect(host='localhost', user='root', password='', db='hostel_management')
                cur = conn.cursor()

                for row in selected_rows:
                    reg_no = self.ui.tableWidget.item(row, 0).text()
                    cur.execute("UPDATE student_registration SET Status = 'S' WHERE Reg_No = %s", (reg_no,))
                    # cur.execute("select Student_Id, S_Name from student_registration where Status='S'")
                    # selectt = cur.fetchall()
                    # for Sname, Sid in selectt:
                    #     self.completer.setModel(QtCore.QStringListModel((sname),sid))

                conn.commit()
                conn.close()

                # Show success message box
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setText("Students selected for hostel")
                msg_box.setWindowTitle("Congratulations")
                msg_box.exec_()

                # Update the table changes
                self.selection()

    # Homepage
    def show_exit(self):
        reply = QtWidgets.QMessageBox.question(None, 'Confirmation', 'Are you sure you want to exit?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            QApplication.quit()

    def cancel(self):
        self.ui.tabWidget.setCurrentIndex(1)

    def logout(self):
        reply1 = QtWidgets.QMessageBox.question(None, 'Confirmation', 'Are you sure you want to Logout?',
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply1 == QtWidgets.QMessageBox.Yes:
            self.ui.tabWidget.setCurrentIndex(0)
            self.hide_menu_options()

    def hostelreg(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def roomreg(self):
        self.ui.tabWidget.setCurrentIndex(3)

    def sreg(self):
        self.ui.tabWidget.setCurrentIndex(4)

    def ssel(self):
        self.ui.tabWidget.setCurrentIndex(5)

    def salloc(self):
        self.ui.tabWidget.setCurrentIndex(6)

    def hide_menu_options(self):
        # Hide all menu options except "Exit"
        for action in self.ui.menu.actions():
            action.setVisible(action.text() == "Exit")

     # function to populate menu buttons dynamically
    def show_menu_options(self):
        conn = pymysql.connect(host='localhost', user='root', password='', db='hostel_management')
        cur = conn.cursor()

        query1 = "SELECT Menu_Dtl_Id FROM user_privileges WHERE  User_Id = %s"
        cur.execute(query1, (self.userid,))

        result = cur.fetchall()

        if not result:
            # Handle the case where no results were found for the given userid
            # You can choose to display an error message or take some other action
            print("No privileges found for this user.")
            conn.close()
            return

        menu_dtl_ids = [row[0] for row in result]

        query = "SELECT Type FROM module_dtl WHERE Menu_Dtl_Id IN %s"
        cur.execute(query, (menu_dtl_ids,))

        available_abbreviated_names = [menu[0] for menu in cur.fetchall()]

        # Mapping of abbreviated forms to full names
        menu_name_mapping = {
            'M': 'Master',
            'T': 'Transaction',
            'R': 'Report'
        }

        available_full_names = [menu_name_mapping.get(abbreviated_name, abbreviated_name) for abbreviated_name in
                                available_abbreviated_names]

        # Always show Menu4 and Menu5
        # Hide all menu options except "Exit" and "Cancel"
        for action in self.ui.menu.actions():
            if action.text() == "Exit" or action.text() == "Cancel":
                action.setVisible(True)
            elif action.text() in available_full_names:
                action.setVisible(True)
            else:
                action.setVisible(False)

        # Close the database connection
        conn.close()
        self.ui.menu1.aboutToShow.connect(self.menudtl)

        self.ui.menu2.aboutToShow.connect(self.menudtl1)
        self.ui.menu3.aboutToShow.connect(self.menudtl2)

    def menudtl(self):
        # Fetch and populate the submenu for the "Master" menu
        self.populate_submenu(self.ui.menu1, 'M')

    def menudtl1(self):
        # Fetch and populate the submenu for the "Transaction" menu
        self.populate_submenu(self.ui.menu2, 'T')

    def menudtl2(self):
        # Fetch and populate the submenu for the "Report" menu
        self.populate_submenu(self.ui.menu3, 'R')

    def populate_submenu(self, menu, menu_type):
        conn = pymysql.connect(host='localhost', user='root', password='', db='hostel_management')
        cur = conn.cursor()

        query1 = "SELECT Menu_Dtl_Id FROM user_privileges WHERE User_Id = %s"
        cur.execute(query1, (self.userid,))
        result = cur.fetchall()

        if not result:
            # Handle the case where no results were found for the given userid
            # You can choose to display an error message or take some other action
            print("No privileges found for this user.")
            conn.close()
            return

        menu_dtl_ids = [row[0] for row in result]

        # Fetch the available submenus for the specified menu_type
        query = "SELECT Menu_Name FROM module_dtl WHERE Menu_Dtl_Id IN %s AND Type=%s"
        cur.execute(query, (menu_dtl_ids, menu_type))
        available_submenus = [menu[0] for menu in cur.fetchall()]

        # Clear existing submenus
        menu.clear()

        # Populate the submenu with the fetched submenus
        for submenu_name in available_submenus:
            submenu_action = menu.addAction(submenu_name)
            # Convert submenu name to lowercase for case-insensitive comparison
            submenu_name_lower = submenu_name.lower()

            # Connect the submenu action to the corresponding function based on name
            if "hostel registration" in submenu_name_lower:
                submenu_action.triggered.connect(self.hostelreg)
            elif "room details" in submenu_name_lower:
                submenu_action.triggered.connect(self.roomreg)
            elif "student registration" in submenu_name_lower:
                submenu_action.triggered.connect(self.sreg)
            elif "student selection" in submenu_name_lower:
                submenu_action.triggered.connect(self.ssel)
            elif "student allocation" in submenu_name_lower:
                submenu_action.triggered.connect(self.salloc)

        # Close the database connection
        conn.close()


def main():
    app = QApplication(sys.argv)
    window = FinalProjectWindow()
    window.setWindowFlag(Qt.FramelessWindowHint)  # it doesnot show frame means Mainwindow and exit sign
    window.showMaximized()  # maximize the window
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
