import RPi.GPIO as GPIO
import time

class PIR(object):
    def __init__(self,name, pin):
        self.name = name
        self.pin = pin

    def motion_detected_callback(self, channel):
        """Funkcija koja se poziva kada je detektovan pokret."""
        print("Pokret je detektovan.")
        self.motion_detected = True

    def no_motion_callback(self, channel):
        """Funkcija koja se poziva kada pokret prestane."""
        print("Pokret je prestao.")
        self.motion_detected = False

def run_pir_loop(pir, delay, callback):
        """Petlja koja stalno čita stanje PIR senzora."""
        while not pir.stop_event.is_set():
            if pir.motion_detected:
                callback(True)
            else:
                callback(False)
            time.sleep(delay)

def stop(pir):
        """Zaustavlja PIR petlju."""
        pir.stop_event.set()
    


        