import time
from threading import Timer

class Led:

    green_blink_start_time = 0
    green_blink_duration = .5

    red_blink_start_time = 0
    red_blink_duration = .5

    is_red_light_on = False
    is_green_light_on = False

    red_timer = None
    green_timer = None

    def __init__(self):
        print("Led object is created")

    def red_light_on(self):
        print("[INFO] Red light On")
        if self.is_red_light_on == False:
            self.is_red_light_on = True
            # Code to turn ON red light here ---->


    def red_light_off(self):
        print("[INFO] Red light Off")
        if self.is_red_light_on:
            self.is_red_light_on = False
            # Code to turn OFF red light here ---->


    def green_light_on(self):
        print("[INFO] Green light On")
        if self.is_green_light_on == False:
            self.is_green_light_on = True
            # Code to turn ON red light here ---->

    def green_light_off(self):
        print("[INFO] Green light Off")
        if self.is_green_light_on:
            self.is_green_light_on = False
            # Code to turn OFF red light here ---->

    def green_light_toggle(self):
        if self.is_green_light_on:
            self.green_light_off()
        else:
            self.green_light_on()

    def red_light_toggle(self):
        if self.is_red_light_on:
            self.red_light_off()
        else:
            self.red_light_on()


    def standby_green(self):

        if self.green_timer is not None:
            self.green_timer.cancel()
            self.green_timer = None

        self.green_light_on()

    def turn_off_green(self):

        if self.green_timer is not None:
            self.green_timer.cancel()
            self.green_timer = None

        self.green_light_off()

    def standby_red(self):

        if self.red_timer is not None:
            self.red_timer.cancel()
            self.red_timer = None

        self.red_light_on()

    def turn_off_red(self):

        if self.red_timer is not None:
            self.red_timer.cancel()
            self.red_timer = None

        self.red_light_off()


    def blinking_green_light(self):

        if self.green_timer is not None:
            self.green_timer.cancel()
            self.green_timer = None

        def blink():
            self.green_light_toggle()
            self.green_timer = Timer(self.green_blink_duration, blink)
            self.green_timer.start()

        self.green_light_toggle()
        self.green_timer = Timer(self.green_blink_duration, blink)
        self.green_timer.start()

    def blinking_red_light(self):

        if self.red_timer is not None:
            self.red_timer.cancel()
            self.red_timer = None

        def blink():
            self.red_light_toggle()
            self.red_timer = Timer(self.red_blink_duration, blink)
            self.red_timer.start()

        self.red_light_toggle()
        self.red_timer = Timer(self.red_blink_duration, blink)
        self.red_timer.start()

