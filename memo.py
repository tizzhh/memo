from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QPlainTextEdit,
    QDateTimeEdit,
    QPushButton,
    QMessageBox,
    QLineEdit,
)
from PyQt5.QtCore import QDateTime
from PyQt5 import uic, QtCore, QtGui
import sys
import time
import threading
import re
import argparse
import csv
import os


class UI(QMainWindow):
    test_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(UI, self).__init__()

        self.filename = args().strip()
        self.filename = filecreate(self.filename)

        self.setWindowIcon(QtGui.QIcon("logo.svg"))

        self.memos = []

        self.memos2 = {}

        uic.loadUi("layout5.ui", self)

        self.label = self.findChild(QLabel, "label")
        self.label.hide()
        self.date = self.findChild(QDateTimeEdit, "dateTimeEdit_2")
        self.textedit = self.findChild(QPlainTextEdit, "plainTextEdit")
        self.textedit2 = self.findChild(QPlainTextEdit, "plainTextEdit_2")
        self.button = self.findChild(QPushButton, "pushButton")
        self.line = self.findChild(QLineEdit, "lineEdit")
        self.memodelete = self.findChild(QPushButton, "pushButton_2")
        self.date.setMinimumDateTime(QDateTime.currentDateTime())

        self.button.clicked.connect(self.click)
        self.memodelete.clicked.connect(self.memo_delete)

        self.show()

        self.waiting = threading.Thread(target=self.wait, daemon=True)
        self.waiting.start()

        self.test_signal.connect(self.label.setText)
        self.test_signal.connect(self.memoo)


        if not os.stat(self.filename).st_size == 0:
            self.memos = csv_read(self.filename)
            self.prev_memos()
            self.update_memos2(self.memos)


    def update_memos2(self, memos):
        for item in memos:
            date = item["date"]
            self.memos2[date] = item["memo"]

    def memo_delete(self):
        if not re.search(
            r"^([0][1-9]|[1-2][0-9]|[3][0-1])\.([0][1-9]|[1][0-2])\.[2][0-1][0-9][0-9] ([0][0-9]|[1][0-9]|[2][0-4]):([0][0-9]|[1-5][0-9])$",
            self.line.text(),
        ):
            self.error3()
            return
        for i in range(len(self.memos)):
            check = False
            if self.line.text() in self.memos[i]["date"]:
                self.memos.pop(i)
                check = True
                break
        if check == False:
            self.error2()
            return
        self.line.clear()
        self.prev_memos()
        update_csv(self.memos, self.filename)
        self.update_memos2(self.memos)

    def click(self):
        memo = self.textedit.toPlainText()
        date = self.date.dateTime().toString("dd.MM.yyyy hh:mm")
        self.save_memo(memo, date)
        self.textedit.clear()

    def save_memo(self, memo, date):
        if self.textedit.toPlainText() == "":
            self.error()
            return
        if date in self.memos:
            self.error1()
            return
        self.memos.append({"date": date, "memo": memo})
        update_csv(self.memos, self.filename)
        self.prev_memos()
        self.update_memos2(self.memos)

    def prev_memos(self):
        self.textedit2.setPlainText("")
        for memo in self.memos:
            self.textedit2.insertPlainText(f"{memo['date']}: {memo['memo']}\n")

    def wait(self):
        while True:
            if QDateTime.currentDateTime().toString("dd.MM.yyyy hh:mm") in self.memos2:
                self.test_signal.emit(
                    f"{self.memos2[QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm')]}"
                )
            time.sleep(60)

    def memoo(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(self.label.text())
        msg.setWindowTitle("Memo")
        msg.exec_()

    def error(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("Please make a memo")
        error.setWindowTitle("Error")
        error.exec_()

    def error1(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("A memo for this date already exists")
        error.setWindowTitle("Error")
        error.exec_()

    def error2(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("A memo doesn't exist")
        error.setWindowTitle("Error")
        error.exec_()

    def error3(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("Wrong date format")
        error.setInformativeText("Date format: dd.MM.yyyy hh:mm")
        error.setWindowTitle("Error")
        error.exec_()


def main():
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec_()

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="The name of file with memos, if it doesn't exist this app will create it. The file must be a .csv type", default="memos.csv")
    args = parser.parse_args()
    return args.f

def filecreate(filename):
    if not ".csv" in filename:
        sys.exit("Wrong file")
    try:
        with open(filename, "a") as file:
            pass
    except FileNotFoundError:
        sys.exit("File doesn't exist")

    return filename

def update_csv(memos, filename):
    with open(filename, "w", newline="") as file:
        fieldnames = ["date", "memo"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in memos:
            if QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm') <= row["date"]:
                writer.writerow(row)
    return True

def csv_read(filename):
    memos = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm') <= row["date"]:   
                memos.append(row)

    return memos

if __name__ == "__main__":
    main()
