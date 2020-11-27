#import MySQLdb
import os
import shutil
import encode_faces
import MySQLdb
import cv2
import numpy as np
import PIL.Image
import io


def start():

    # delete dataset folder and create a new one
    if os.path.isdir(os.getcwd() + "/dataset"):
        shutil.rmtree(os.getcwd() + "/dataset")
    os.mkdir(os.getcwd() + "/dataset")

    # delete qr folder and create a new one
    if os.path.isdir(os.getcwd() + "/qr"):
        shutil.rmtree(os.getcwd() + "/qr")
    os.mkdir(os.getcwd() + "/qr")

    db = MySQLdb.connect(
            host="localhost",
            user="monty",
            password="some_pass",
            database="facerecoghome"
        )

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()

    counter = 0
    for row in result:
        counter += 1
        id = row[0]
        username = row[1]
        password = row[2]
        email = row[3]
        role = row[4]
        images = [row[5],  row[6], row[7], row[8], row[9],
                  row[10], row[11], row[12], row[13], row[14]]

        user_folder = role + "@" + str(id)

        os.mkdir(os.getcwd() + "/dataset/" + user_folder)

        max = len(images)
        i = 0

        while i < max:

            with open(os.getcwd() + "/dataset/" + user_folder + "/" + str(i+1) + ".jpeg", "wb") as img:
                if img is not None:
                    img.write(images[i])
            i += 1

    encode_faces.encode()
