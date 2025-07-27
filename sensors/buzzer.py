import RPi.GPIO as GPIO
import time

#Sa vezbi copy
class Buzzer(object):

    def __init__(self,name, pin):
        self.name = name
        self.pin = pin
        
    
    def buzz(self,pitch, duration):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        period = 1.0 / pitch
        delay = period / 2
        cycles = int(duration * pitch)
        for i in range(cycles):
            GPIO.output(self.pin, True)
            time.sleep(delay)
            GPIO.output(self.pin, False)
            time.sleep(delay)

def run_buzzer_loop(buzzer, pitch, duration, stop_event, event_on,publish_event):
    """
    Upravljanje stvarnim buzzer-om pomoću klase Buzzer.
    :param buzzer: Instanca klase Buzzer.
    :param pitch: Frekvencija zvuka.
    :param duration: Trajanje zvuka.
    :param stop_event: Event za zaustavljanje rada.
    :param event_on: Event koji aktivira zvuk.
    """
    try:
        while not stop_event.is_set():
            if event_on.wait(timeout=0.1):  # Čekaj na signal
                print(f"{buzzer.name} Buzzer: Aktiviran")
                buzzer.buzz(pitch, duration)
                event_on.clear()
    finally:
        GPIO.cleanup(buzzer.pin)  # Očisti GPIO resurse
        print(f"{buzzer.name} Buzzer: Zaustavljen")
