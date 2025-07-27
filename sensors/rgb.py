import RPi.GPIO as GPIO
from time import sleep
from queue import Empty

class RGB(object):
    def __init__(self, **kwargs) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.RED_PIN = kwargs["RED"]
        self.GREEN_PIN = kwargs["GREEN"]
        self.BLUE_PIN = kwargs["BLUE"]

        self.status = "off"

        self.command_mappings = {
            "off": self.turnOff,
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "purple": self.purple,
            "white": self.white,
            "yellow": self.yellow,
            "light blue": self.lightBlue
        }

        #set pins as outputs
        GPIO.setup(self.RED_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_PIN, GPIO.OUT)
        GPIO.setup(self.BLUE_PIN, GPIO.OUT)

    def turnOff(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
    
    def white(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)
        
    def red(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)

    def green(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        
    def blue(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)
        
    def yellow(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        
    def purple(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)
        
    def lightBlue(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)

    def resolve_command(self, command):
        if command in self.command_mappings:
            if command != self.status:
                self.command_mappings[command]()
                self.status = command

                return True
        else:
            print(f"Invalid RGB diode command: {command}")

        return False

def run_rgb_loop(input_queue, rgb: RGB, delay, callback, stop_event, publish_event, settings):
    while True:
        try:
            action = input_queue.get(timeout=1)
            status_changed = rgb.resolve_command(action)

            if status_changed:
                callback(rgb.status, publish_event, settings)
        except Empty:
            pass

        if stop_event.is_set():
            GPIO.cleanup()
            break

        sleep(delay)