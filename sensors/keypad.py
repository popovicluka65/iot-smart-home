import RPi.GPIO as GPIO
import time

class Keyboard(object):
    def __init__(self, settings):
        """
        Inicijalizacija tastature sa postavkama.
        :param settings: Dictionary sa pinovima i nazivom uređaja.
        """
        self.name = settings["name"]
        self.R1 = settings["R1"]
        self.R2 = settings["R2"]
        self.R3 = settings["R3"]
        self.R4 = settings["R4"]
        self.C1 = settings["C1"]
        self.C2 = settings["C2"]
        self.C3 = settings["C3"]
        self.C4 = settings["C4"]

        # Inicijalizacija GPIO pinova
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.R1, GPIO.OUT)
        GPIO.setup(self.R2, GPIO.OUT)
        GPIO.setup(self.R3, GPIO.OUT)
        GPIO.setup(self.R4, GPIO.OUT)

        GPIO.setup(self.C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read_line(self, line, characters):
        """
        Funkcija koja šalje impuls na zadatu liniju i proverava kolone
        kako bi detektovala koji je taster pritisnut.
        :param line: GPIO pin reda koji se proverava
        :param characters: Lista karaktera koji se nalaze na tom redu
        """
        GPIO.output(line, GPIO.HIGH)
        if GPIO.input(self.C1) == 1:
            print(f"Detected: {characters[0]}")
        if GPIO.input(self.C2) == 1:
            print(f"Detected: {characters[1]}")
        if GPIO.input(self.C3) == 1:
            print(f"Detected: {characters[2]}")
        if GPIO.input(self.C4) == 1:
            print(f"Detected: {characters[3]}")
        GPIO.output(line, GPIO.LOW)

    def start(self):
        """
        Funkcija koja pokreće petlju za detekciju tastera.
        """
        try:
            while True:
                # Pozivanje read_line funkcije za svaki red tastature
                self.read_line(self.R1, ["1", "2", "3", "A"])
                self.read_line(self.R2, ["4", "5", "6", "B"])
                self.read_line(self.R3, ["7", "8", "9", "C"])
                self.read_line(self.R4, ["*", "0", "#", "D"])
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\nApplication stopped!")
        finally:
            GPIO.cleanup()  # Očisti GPIO kada aplikacija prestane sa radom

def run_keyboard_loop(keyboard, delay, callback, stop_event, settings, publish_event):
    while True:
        for i, row in enumerate(keyboard.rows):
            key = keyboard.read_line(row, keyboard.keys[i])
            if key:
                callback(key, settings, publish_event)
        if stop_event.is_set():
            break
        time.sleep(delay)

    