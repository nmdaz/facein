# import the necessary packages
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import cv2
import Unlock
import MySQLdb
import pyzbar.pyzbar as pyzbar
import led
import os
import time
from threading import Timer


#Start FaceRecognition

class Recog:

    SCAN_QR_TIME_LIMIT = 25
    UNLOCK_DURATION = 10
    # Inner state machine.
    # Each state has an init and update function.
    # stateInit() function will be called one time to change
    # and setup the current_state.
    # stateUpdate() function will called continously
    # inside a while loop
    STATE_RECOGNIZING_FACE = 1
    STATE_RECONGNIZING_QR = 2
    STATE_UNLOCKING_DOOR = 3

    # the database has 10 sample image per user
    # a PERFECT_VALUE of 10 means a user facing the camera
    # should match all 10 sample images in the database
    # to unlock
    PERFECT_VALUE = 10
    

    def __init__(self, exit_callback = None, is_show_video = True):
        self.exit_callback = exit_callback
        self.is_show_video = is_show_video
        print("[INFO] Recog Started | " "exit_callback: " + str(exit_callback) + " | Show Video: " + str(is_show_video))
        print("[INFO] Loading encodings.pickle")
        self.data = pickle.loads(open(os.getcwd()+"/encodings.pickle", "rb").read())
        print("[INFO] Loading Cascade Classifier")
        self.detector = cv2.CascadeClassifier(os.getcwd()+"/haarcascade_frontalface_default.xml")
        
        self.unlock = Unlock.Unlock()
        self.current_state = 0
        self.needed_password = ""
        self.perfect_face_counter = 0
        self.frame_label = ""
        self.led = led.Led()

        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        vs = cv2.VideoCapture(0)
        self.vs = vs
        time.sleep(2.0)

        self.recognizeFaceInit()

        # start the FPS counter
        fps = FPS().start()

        # loop over frames from the video file stream
        while True:

            # grab the frame from the threaded video stream and resize it
            # to 500px (to speedup processing)
            ret, frame = vs.read()
            frame = imutils.resize(frame, width=500)
            self.frame = frame

            if self.current_state == self.STATE_RECOGNIZING_FACE:
                self.recognizeFaceUpdate()
            elif self.current_state == self.STATE_RECONGNIZING_QR:
                self.recognizeQRUpdate()
            elif self.current_state == self.STATE_UNLOCKING_DOOR:
                self.unlockDoorUpdate()
                
            if(self.is_show_video):
                
                cv2.putText(frame, self.frame_label, (12, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.6, (0, 255, 0), 1)

                # display the image to our screen
                cv2.imshow("Frame", self.frame)
            key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                cv2.destroyAllWindows()
                vs.release()
                if self.exit_callback is not None:
                    self.exit_callback()
                break
            elif key & 0xFF == 27:
                break

            # update the FPS counter
            fps.update()

        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.release()


    def recognizeQRInit(self, recognized_face_id):
        print("[INFO] change state to: STATE_RECOGNIZING_QR")
        self.current_state = self.STATE_RECONGNIZING_QR
        self.recognized_face_id = recognized_face_id
        self.frame_label = "Scanning QR Code..."
        
        print("[INFO] Connecting to database")
        
        db = MySQLdb.connect(
            host="localhost",
            user="monty",
            password="some_pass",
            database="facerecoghome"
        )
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE `id` = " + recognized_face_id)
        result = cursor.fetchall()
        for row in result:
            self.needed_password = row[2]
        cursor.close()
        self.start_time = time.perf_counter()
        
        print("[INFO] Connected to database")
        self.led.standby_red()
        self.led.blinking_green_light()

    
        
    def recognizeFaceInit(self):
        print("[INFO] change state to: STATE_RECOGNIZING_FACE")
        self.current_state = self.STATE_RECOGNIZING_FACE
        self.perfect_face_counter = 0
        self.frame_label = "Recognizing Face..."
        self.led.standby_red()
        self.led.turn_off_green()

    def recognizeFaceUpdate(self):

        detector = self.detector
        data = self.data
        frame = self.frame

        # convert the input frame from (1) BGR to grayscale (for face
        # detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                          minNeighbors=5, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        name_of_best = ""

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings.pickle"],
                                                     encoding, .52)
            name = "Unknown"
            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)
                highestValue = counts.get(name)
                if highestValue >= self.PERFECT_VALUE:
                    self.perfect_face_counter += 1
                    # update the list of names
                    names.append(name)
                    if self.perfect_face_counter >= 2:
                        name_of_best = name
                else:
                    self.perfect_face_counter = 0
                    print("[INFO] unknown face detected")
                    self.led.blinking_red_light()
                    def red_light():
                        self.led.standby_red()
                    t = Timer(1, red_light)

        if name_of_best != "":
            print("[INFO] user is detected: " + name_of_best)
            id = name_of_best.split("@")[1]
            self.recognizeQRInit(id)
            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                if name == name_of_best:
                    # draw the predicted face name on the image
                    cv2.rectangle(frame, (left, top), (right, bottom),
                                  (0, 0, 255), 2)


    def recognizeQRUpdate(self):
        self.led.blinking_green_light()
        elapse_time = time.perf_counter() - self.start_time
        remaining_time = self.SCAN_QR_TIME_LIMIT - elapse_time
        print("[INFO] ScanQR Remaining Time: " + str(remaining_time) )
        if remaining_time <= 0:
            self.recognizeFaceInit()
            return

        decodedObjects = pyzbar.decode(self.frame)

        for obj in decodedObjects:
            if obj.type == "QRCODE":
                qr = obj
                qr_data = obj.data.decode("utf-8")
                (x, y, w, h) = qr.rect
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                if self.needed_password == qr_data:
                    print("[INFO] Correct QR Code")
                    self.unlockDoorInit()
                else:
                    print("[INFO] Incorrect QR Code")
                    self.led.blinking_red_light()
                    def red_light():
                        self.led.standby_red()
                    t = Timer(1, red_light)


    def unlockDoorInit(self):
        print("[INFO] change state to: STATE_UNLOCK_DOOR")
        self.current_state = self.STATE_UNLOCKING_DOOR
        self.frame_label = "Door is unclocked"
        self.unlock.unlock()
        self.start_time = time.perf_counter()
        self.led.standby_red()
        self.led.standby_green()
        
    def unlockDoorUpdate(self):
        elapse_time = time.perf_counter() - self.start_time
        remaining_time = self.UNLOCK_DURATION - elapse_time
        print("[INFO] Lock in: " + str(remaining_time) )
        if remaining_time <= 0:
            self.unlock.lock()
            self.recognizeFaceInit()
            return

    def exit(self):
        self.exit_callback()
        self.cv2.destroyAllWindows()
        self.vs.release()
        

