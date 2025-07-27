import threading
from settings import load_settings
from components.dht import run_dht
from components.uds import run_uds
from components.button import run_button
from components.dl import run_dl
from components.buzzer import run_buzzer
from components.pir import run_pir
from components.keypad import run_keyboard
from components.b4sd import run_b4sd
from components.infrared import run_infrared
from components.rgb import run_rgb

import time
from queue import Queue
from threading import Event
from shared_events import alarm_on_event

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(7, GPIO.OUT)  # set up pin 7
except:
    pass

def run_user_input_thread(queue, stop_event, threads):
    input_thread = threading.Thread(target=user_input_thread, args=(queue, stop_event))
    input_thread.start()
    threads.append(input_thread)

def user_input_thread(queue, stop_event):
    while True:
        try:
            user_action = input()
            if user_action.upper() == "R":
                queue.put("red")
            elif user_action.upper() == "G":
                queue.put("green")
            elif user_action.upper() == "B":
                queue.put("blue")
            elif user_action.upper() == "P":
                queue.put("purple")
            elif user_action.upper() == "W":
                queue.put("white")
            elif user_action.upper() == "Y":
                queue.put("yellow")
            elif user_action.upper() == "L":
                queue.put("light blue")
            elif user_action.upper() == "O":
                queue.put("off")
        except:
            time.sleep(0.001)
            if stop_event.is_set():
                break

if __name__ == "__main__":
    print('Starting app')
    settings = load_settings('settings3.json')
    threads = []
    stop_event = threading.Event()
    event_on = threading.Event()
    event_off = threading.Event()
    bir_rgb_event = Event()
    bir_rgb_mappings = {"0": "off",
                        "1": "red",
                        "2": "blue",
                        "3": "purple",
                        "4": "white",
                        "5": "yellow",
                        "6": "light blue",
                        "7": "green"
                        }
    
    #10 tacka
    rgb_queue = Queue()
    b4sd_queue = Queue()
    bb_queue = Queue()
    alarm_clock_on_event = Event()
    alarm_clock_off_event = Event()

    #uvek moraju buzeri da piste kada se aktivira alarm
    #alarm_on_event = Event()
    
    event_on.set()
    try:
        rpir4_settings = settings['RPIR4']
        dht4_settings = settings['DHT4']
        bb_settings = settings['BB']
        b4sd_settings = settings['B4SD']
        infrared_settings = settings['BIR']
        rgb_settings = settings['BRGB']

        #1 ima al ne radi
        #run_pir(rpir4_settings, threads, stop_event)
        #2 ima al ne radi
        #run_dht(dht4_settings, threads, stop_event)
        #3 ima      
        

        #4 ima
        #run_b4sd(b4sd_settings, threads, stop_event, b4sd_queue, bb_queue, alarm_clock_on_event, alarm_clock_off_event)

        #run_buzzer(bb_settings, threads, stop_event,alarm_on_event, bb_queue,  alarm_clock_on_event, alarm_clock_off_event)
        #5
        #run_infrared(infrared_settings, threads, stop_event,bir_rgb_event,bir_rgb_mappings,rgb_queue)
        #6 prepraviti posle
        run_rgb(rgb_settings, threads, stop_event, rgb_queue,bir_rgb_event)
    
        run_user_input_thread(rgb_queue, stop_event, threads)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping app')
        for t in threads:
            stop_event.set()
