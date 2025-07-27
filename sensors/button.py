import RPi.GPIO as GPIO
import time
from locks import print_lock

#PORT_BUTTON = 17
#KOPIRANO SA PDF NA VEZBAMA
class Button(object):
 
    def __init__(self,name, port):
         self.name = name
         self.port = port

    def button_callback(self, event):
        with print_lock:
            print("Button is clicked!")

    def button_pressed(self):
        #print("BUTTON PRESS DETECTED")
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.port, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback = self.button_callback, bouncetime = 100)
        #input("Press any key to exit...")

def run_button_loop(button, stop_event):
    button.detect_button_press()
    while True:
        if stop_event.is_set():
            GPIO.remove_event_detect(button.port)
            break