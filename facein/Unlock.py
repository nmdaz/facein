#import RPi.GPIO as GPIO
import time
from threading import Timer

class Unlock:
    
    def __init__(self):
        self.relay = 3 #pin GPIO
        self.isLocked = True
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setwarnings(False)
        # GPIO.setup(self.relay, GPIO.OUT)
        
    def unlock(self):
        print("[INFO] unlock")
        if(self.isLocked):
            #GPIO.output(self.relay, GPIO.LOW)
            self.isLocked = False

    def lock(self):
        print("[INFO] lock")
        if(self.isLocked == False):
            #GPIO.output(self.relay, GPIO.HIGH)
            self.isLocked = True
