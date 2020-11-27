import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import sys
import start
import MySQLdb
import adduser
import hashlib


#Show Main Menu

class MainMenu():

    def __init__(self):

        print("[INFO] MainMenu")

        self.db = MySQLdb.connect(
            host="localhost",
            user="monty",
            password="some_pass",
            database="facerecoghome"
        )

        print("[INFO] Connected to Database")

        w = tk.Tk()
        w.geometry("630x360")
        w.title("FaceIn - Welcome")
        self.w = w

        frame_left = tk.Frame(master=w, bg="#333333", width=150, height=360)
        frame_left.grid(row=0, column=0)
        self.frame_left = frame_left

        frame_right = tk.Frame(master=w, bg="#666666", width=480, height=360)
        frame_right.grid(row=0, column=1)
        self.frame_right = frame_right

        self.widgets = []
        self.to_destroy_widgets = []

        # Main widgets
        self.setting_button = tk.Button(frame_left, text="Admin", width=14, font=("Courier", 8), bg="#666666",
                                   command=self.login)
        self.widgets.append(self.setting_button)

        self.start_button = tk.Button(frame_left, text="Start", width=14, font=("Courier", 8), bg="#666666",
                                 command=self.start)
        self.widgets.append(self.start_button)

        # Login widgets
        self.login_return_button = tk.Button(frame_left, text="Return", width=14, font=("Courier", 8), bg="#666666",
                                        command=self.return_from_login)
        self.widgets.append(self.login_return_button)

        self.login_username_label = tk.Label(self.frame_right, text="Username", fg="white", bg="#333333", font=("Courier", 8))
        self.widgets.append(self.login_username_label)

        self.login_username_entry = tk.Entry(self.frame_right)
        self.widgets.append(self.login_username_entry)

        self.login_password_label = tk.Label(self.frame_right, text="Password", fg="white", bg="#333333", font=("Courier", 8))
        self.widgets.append(self.login_password_label)

        self.login_password_entry = tk.Entry(self.frame_right, show="*")
        self.widgets.append(self.login_password_entry)

        self.login_button = tk.Button(self.frame_right, text="Login", width=14,
                                 command=self.try_login, font=("Courier", 8), bg="#666666")
        self.widgets.append(self.login_button)

        # Admin widgets
        self.add_user_button = tk.Button(frame_left, text="Add User", width=14, font=("Courier", 8), bg="#666666",
                                   command=self.add_user)
        self.widgets.append(self.add_user_button)

        self.view_user_button = tk.Button(frame_left, text="View Users", width=14, font=("Courier", 8), bg="#666666",
                                 command=self.view_user)
        self.widgets.append(self.view_user_button)

        self.admin_return_button = tk.Button(frame_left, text="Return", width=14, font=("Courier", 8), bg="#666666",
                                             command=self.return_from_admin)
        self.widgets.append(self.admin_return_button)


        self.main()
        self.w.mainloop()

    # Start FaceRecognition
    def start(self):
        self.w.destroy()
        start.Recog(lambda :MainMenu())

    def main(self):
        self.w.title("FaceIn - Main")
        self.hide()
        self.setting_button.place(relx=.07, rely=.01, relwidth=.85, relheight=.1)
        self.start_button.place(relx=.07, rely=.12, relwidth=.85, relheight=.1)

    def login(self):
        self.w.title("FaceIn - Login")
        self.hide()
        self.login_return_button.place(relx=.07, rely=.01, relwidth=.85, relheight=.1)
        self.login_username_label.place(relx=.32, rely=.3)
        self.login_username_entry.place(relx=.32, rely=.34, relwidth=.30)
        self.login_password_label.place(relx=.32, rely=.42)
        self.login_password_entry.place(relx=.32, rely=.46, relwidth=.30)
        self.login_button.place(relx=.32, rely=.55, relwidth=.15, relheight=.08)

    # When login button is Click
    def try_login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()
        password_encode = password.encode()
        md5_object = hashlib.md5()
        md5_object.update(password.encode())
        password_md5 = md5_object.hexdigest()

        sql = "SELECT * FROM `users` WHERE `username` = '{}' AND `password` = '{}'".format(username,password_md5)

        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()

        if row is not None:
            id = row[0]
            dbusername = row[1]
            dbpassword = row[2]

            email = row[3]
            role = row[4]

            isAdmin = False

            if role == "admin" and dbusername == username and dbpassword == password_md5:
                isAdmin = True
            else:
                isAdmin = False

            if isAdmin:
                print("[INFO] Login Success")
                self.admin()
        else:
            print("[INFO] Wrong username or password")

    def admin(self):
        self.w.title("FaceIn - Admin")
        self.hide()
        self.add_user_button.place(relx=.07, rely=.01, relwidth=.85, relheight=.1)
        self.view_user_button.place(relx=.07, rely=.12, relwidth=.85, relheight=.1)
        self.admin_return_button.place(relx=.07, rely=.23, relwidth=.85, relheight=.1)

    def add_user(self):
        self.w.destroy()
        adduser.Adduser(MainMenu)

    def view_user(self):

        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM `users` WHERE `role` = 'user'")
        rows = cursor.fetchall()

        row_h = .05
        margin = .01
        row_y = margin
        num_x = margin
        num_w = .1
        username_x = num_x + num_w + margin
        username_w = .28
        email_x = username_x + username_w + margin
        email_w = .28
        role_x = email_x + email_w + margin
        role_w = .28

        num_label = tk.Label(self.frame_right, text="#", fg="white", bg="#333333", font=("Courier", 10))
        num_label.place(relx=num_x, rely=row_y, relwidth=num_w, relheight=row_h)
        self.to_destroy_widgets.append(num_label)

        username_label = tk.Label(self.frame_right, text="Username", fg="white", bg="#333333", font=("Courier", 10))
        username_label.place(relx=username_x, rely=row_y, relwidth=username_w, relheight=row_h)
        self.to_destroy_widgets.append(username_label)

        email_label = tk.Label(self.frame_right, text="Email", fg="white", bg="#333333", font=("Courier", 10))
        email_label.place(relx=email_x, rely=row_y, relwidth=email_w, relheight=row_h)
        self.to_destroy_widgets.append(email_label)

        role_label = tk.Label(self.frame_right, text="Role", fg="white", bg="#333333", font=("Courier", 10))
        role_label.place(relx=role_x, rely=row_y, relwidth=role_w, relheight=row_h)
        self.to_destroy_widgets.append(role_label)

        counter = 1
        row_y = row_h + .02

        for row in rows:
            id = row[0]
            username = row[1]
            email = row[3]
            role = row[4]

            num = tk.Label(self.frame_right, text=str(counter), fg="white", bg="#333333", font=("Courier", 8))
            num.place(relx=num_x, rely=row_y, relwidth=num_w, relheight=row_h)
            self.to_destroy_widgets.append(num)
            username = tk.Label(self.frame_right, text=username, fg="white", bg="#333333", font=("Courier", 8))
            username.place(relx=username_x, rely=row_y, relwidth=username_w, relheight=row_h)
            self.to_destroy_widgets.append(username)
            email = tk.Label(self.frame_right, text=email, fg="white", bg="#333333", font=("Courier", 8))
            email.place(relx=email_x, rely=row_y, relwidth=email_w, relheight=row_h)
            self.to_destroy_widgets.append(email)
            role = tk.Label(self.frame_right, text=role, fg="white", bg="#333333", font=("Courier", 8))
            role.place(relx=role_x, rely=row_y, relwidth=role_w, relheight=row_h)
            self.to_destroy_widgets.append(role)

            counter += 1
            row_y += row_h + margin


    def return_from_admin(self):
        self.main()

    # Hide all widgets inside the window
    def hide(self):
        for a in self.widgets:
            a.pack_forget()
            a.place_forget()

        for b in self.to_destroy_widgets:
            b.destroy()

    def return_from_login(self):
        self.hide()
        self.setting_button.place(relx=.07, rely=.01, relwidth=.85, relheight=.1)
        self.start_button.place(relx=.07, rely=.12, relwidth=.85, relheight=.1)


if __name__ == "__main__":
    MainMenu()






