import threading
from settings import load_settings
from components.dht import run_dht
from components.uds import run_uds
from components.button import run_button
from components.dl import run_dl
from components.buzzer import run_buzzer
from components.pir import run_pir
from components.keypad import run_keyboard
from components.lcd import run_lcd
from components.gyro import run_gyro
import time
from threading import Event
from queue import Queue

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(7, GPIO.OUT)  # set up pin 7
except:
    pass


if __name__ == "__main__":
    print('Starting app')
    settings = load_settings('settings2.json')
    threads = []
    stop_event = threading.Event()
    event_on = threading.Event()
    event_off = threading.Event()
    events = {"dht-lcd" : Event()}
    lcd_commands = Queue()
    event_on.set()
    try:
        #1
        ds2_settings = settings['DS2']
        #2
        dus2_settings = settings['UDS2']
        #3
        dpir2_settings = settings['DPIR2']
        #4
        gdht_settings = settings['GDHT']
        #5
        lcd_settings = settings['GLCD']
        #6
        gyro_settings = settings['GSG']
        #7
        rpir3_settings = settings['RPIR3']
        #8
        dht3_settings = settings['DHT3']
        

        #1
        run_button(ds2_settings,threads,stop_event)
        #2
        #run_uds(dus2_settings,threads,stop_event)
        #3
        #run_pir(dpir2_settings, threads, stop_event)
        #4
        #run_dht(gdht_settings, threads, stop_event,events["dht-lcd"],lcd_commands)
        #5 ima
        #run_lcd(lcd_settings, threads, stop_event,events["dht-lcd"],lcd_commands)
        #6 ima
        #run_gyro(gyro_settings, threads, stop_event)
        #7
        #run_pir(rpir3_settings, threads, stop_event)
        #8
        #run_dht(dht3_settings, threads, stop_event)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping app')
        for t in threads:
            stop_event.set()
