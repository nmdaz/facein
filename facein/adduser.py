import tkinter as tk
from PIL import ImageTk
from tkinter import *
from tkinter.ttk import *
import numpy as np
import cv2
import MySQLdb
import database_to_system
from PIL import Image
import io
import time
import imutils
import main
import hashlib

class Adduser:

    def __init__(self, exit_callback):
        self.exit_callback = exit_callback
        self.detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.neededImage = 10
        self.imageCount = 0
        self.btnSave = None
        self.is_exited = False
        self.show()

    def show(self):
        db = MySQLdb.connect(
            host="localhost",
            user="monty",
            password="some_pass",
            database="facerecoghome"
        )

        self.db = db

        w = tk.Tk()
        w.geometry("630x360")
        w.title("Enroll User")
        w.protocol("WM_DELETE_WINDOW", self.exit)
        w.bind("<Escape>", self.exit)
        self.w = w

        frameLeft = tk.Frame(master=w,bg="#333333",width=150,height=360)
        frameLeft.grid(row=0,column=0)
        frameRight = tk.Frame(master=w,bg="#666666",width=480,height=360)
        frameRight.grid(row=0,column=1)

        canvas = tk.Label(frameRight, width=480, height=360, background="white")
        canvas.place(relx=.5,rely=.5, relwidth=.9, relheight=.9, anchor=tk.CENTER)
        self.canvas = canvas

        usernameLabel = tk.Label(frameLeft, text="Username", fg="white", bg="#333333", font=("Courier", 8))
        usernameLabel.place(relx=.05, rely=.05)

        usernameEntry = tk.Entry(frameLeft, width=50)
        usernameEntry.place(relx=.07, rely=.1, relwidth=.85)
        usernameEntry.bind("<FocusOut>", self.check)
        usernameEntry.bind("<KeyRelease>", self.check)
        self.usernameEntry = usernameEntry

        passwordLabel = tk.Label(frameLeft, text="Password", fg="white", bg="#333333", font=("Courier", 8))
        passwordLabel.place(relx=.05, rely=.17)

        passwordEntry = tk.Entry(frameLeft, width=50, show="*")
        passwordEntry.place(relx=.07, rely=.22, relwidth=.85)
        passwordEntry.bind("<FocusOut>", self.check)
        passwordEntry.bind("<KeyRelease>", self.check)
        self.passwordEntry = passwordEntry

        cpasswordLabel = tk.Label(frameLeft, text="Confirm Password", fg="white", bg="#333333", font=("Courier", 8))
        cpasswordLabel.place(relx=.05, rely=.29)

        cpasswordEntry = tk.Entry(frameLeft, width=50, show="*")
        cpasswordEntry.place(relx=.07, rely=.34, relwidth=.85)
        cpasswordEntry.bind("<FocusOut>", self.check)
        cpasswordEntry.bind("<KeyRelease>", self.check)
        self.cpasswordEntry = cpasswordEntry

        capture_button = tk.Button(frameLeft, text="Capture Image 0/" + str(self.neededImage), width=14,
                                   command=self.cap,  font=("Courier", 8), bg="#666666")
        capture_button.place(relx=.07, rely=.45, relwidth=.85, relheight=.1)
        self.capture_button = capture_button

        reset_button = tk.Button(frameLeft, text="Reset", width=14, font=("Courier", 8), bg="#666666")
        reset_button.place(relx=.07, rely=.58, relwidth=.85, relheight=.1)
        self.reset_button = reset_button

        save_button = tk.Button(frameLeft, text="Save", width=14, state=DISABLED,
                                 command=self.save, font=("Courier", 8), bg="#666666")
        save_button.place(relx=.07, rely=.71, relwidth=.85, relheight=.1)
        self.save_button = save_button

        note = tk.Message(frameLeft, text="Note: ", fg="white", bg="#333333", font=("Courier", 6), justify=LEFT, width = 100)
        note.place(relx=.07, rely=.82, anchor=NW)
        self.note = note

        self.check()

        cap = cv2.VideoCapture(0)
        time.sleep(2)

        self.cap = cap
        self.update()
        self.w.mainloop()


    def update(self):

        if self.is_exited:
            return

        ret, frame = self.cap.read()

        if frame is None:
            return

        frame = imutils.resize(frame, 500)
        self.frame = frame


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100),
                                               flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        if(len(boxes) == 0 or self.imageCount >= self.neededImage):
            self.capture_button.configure(state=DISABLED)
        else:
            self.capture_button.configure(state=NORMAL)

        # loop over the recognized faces
        for top, right, bottom, left in boxes:
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            y = top - 15 if top - 15 > 15 else top + 15

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.canvas.configure(image=image)
        self.canvas.image = image
        self.w.after(15, self.update)


    def check(self, event = None):

        showSaveButton = True

        noteS = "Note"

        if self.imageCount < self.neededImage:
            showSaveButton = False
            noteS += ": {} more needed image".format(self.neededImage - self.imageCount)

        if len(self.usernameEntry.get()) < 4:
            showSaveButton = False
            noteS += ": Username must be atleast 4 characters long"
        else:
            db = self.db
            cursor = db.cursor()
            sql = "SELECT * FROM `users` WHERE `username` = '{}'".format(self.usernameEntry.get())
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            if result is not None:
                showSaveButton = False
                noteS += ": Username already in database"


        if len(self.passwordEntry.get()) < 4:
            showSaveButton = False
            noteS += ": Password should be atlease 4 chars long"

        if self.passwordEntry.get() != self.cpasswordEntry.get():
            showSaveButton = False
            noteS += ": Password and CPassword dont match"

        if showSaveButton:
            self.save_button.configure(state=NORMAL)
        else:
            self.save_button.configure(state=DISABLED)

        self.note.configure(text=noteS)




    def cap(self):

        if self.imageCount >= self.neededImage:
            return

        self.imageCount += 1

        self.capture_button.configure(text="Capture Image" + str(self.imageCount) + "/" + str(self.neededImage))

        if self.imageCount == 1:
            self.image1 = self.frame
        elif self.imageCount == 2:
            self.image2 = self.frame
        elif self.imageCount == 3:
            self.image3 = self.frame
        elif self.imageCount == 4:
            self.image4 = self.frame
        elif self.imageCount == 5:
            self.image5 = self.frame
        elif self.imageCount == 6:
            self.image6 = self.frame
        elif self.imageCount == 7:
            self.image7 = self.frame
        elif self.imageCount == 8:
            self.image8 = self.frame
        elif self.imageCount == 9:
            self.image9 = self.frame
        elif self.imageCount == 10:
            self.image10 = self.frame

        self.check()

    def save(self):

        password = self.passwordEntry.get()
        password_encode = password.encode()
        md5_object = hashlib.md5()
        md5_object.update(password.encode())
        password_md5 = md5_object.hexdigest()

        self.cap.release()

        db = self.db
        cursor = db.cursor()

        sql = "INSERT INTO users (username, password, email, role, image1, image2, image3, image4, image5, image6" \
              ", image7, image8, image9, image10) " \
              "VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (self.usernameEntry.get(), password_md5, "nmdazgames@gmail.com", "user",
               cv2.imencode('.jpg', self.image1)[1].tostring(),
               cv2.imencode('.jpg', self.image2)[1].tostring(),
               cv2.imencode('.jpg', self.image3)[1].tostring(),
               cv2.imencode('.jpg', self.image4)[1].tostring(),
               cv2.imencode('.jpg', self.image5)[1].tostring(),
               cv2.imencode('.jpg', self.image6)[1].tostring(),
               cv2.imencode('.jpg', self.image7)[1].tostring(),
               cv2.imencode('.jpg', self.image8)[1].tostring(),
               cv2.imencode('.jpg', self.image9)[1].tostring(),
               cv2.imencode('.jpg', self.image10)[1].tostring())
        cursor.execute(sql, val)
        db.commit()
        database_to_system.start()
        self.exit()

    def exit(self):
        self.w.destroy()
        if self.exit_callback is not None:
            self.exit_callback()
