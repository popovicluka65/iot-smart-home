import threading
from settings import load_settings
from components.dht import run_dht
from components.uds import run_uds
from components.button import run_button
from components.dl import run_dl
from components.buzzer import run_buzzer
from components.pir import run_pir
from components.keypad import run_keyboard
import time
from threading import Event
from shared_events import alarm_on_event

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(7, GPIO.OUT)  # set up pin 7
except:
    pass


if __name__ == "__main__":
    print('Starting app')
    settings = load_settings('settings1.json')
    threads = []
    stop_event = threading.Event()
    event_on = threading.Event()
    event_off = threading.Event()
    event_on.set()
    events = {"dpir-dl" : Event()}
    try:
        #ports 1 and 17, 3.3V
        dht1_settings = settings['DHT1']
        dht2_settings = settings['DHT2']
        uds1_settings = settings['UDS1']
        ds1_settings = settings['DS1']
        
        #KONFIGURACIJA ZA BUZZER, prepraviti posle da bude kako treba
        db_settings = settings['DB']
        dl_settings = settings['DL']

        rpir1_settings = settings['RPIR1']
        rpir2_settings = settings['RPIR2']
        dpir1_settings = settings['DPIR1']
        kb_settings = settings['DMS']

        #1 ima
        run_button(ds1_settings,threads,stop_event)
        #2 ima

        #run_dl(dl_settings,threads,stop_event, events["dpir-dl"])
        
        #3 ima
        #run_uds(uds1_settings,threads,stop_event)
        #4 ima
        #run_buzzer(db_settings, threads, stop_event,alarm_on_event)

        #5
        #run_pir(dpir1_settings, threads, stop_event, events["dpir-dl"])

        #6 ima
        run_keyboard(kb_settings, threads, stop_event)
        #7,8 rpir1 ima al ne radi
        #run_pir(rpir1_settings, threads, stop_event)
        #run_pir(rpir2_settings, threads, stop_event)
        #9,10 oba ima na grafani
        #run_dht(dht1_settings, threads, stop_event)
        #run_dht(dht2_settings, threads, stop_event)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping app')
        for t in threads:
            stop_event.set()
