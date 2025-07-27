from simulators.button import run_button_simulator
import threading
import time
from locks import print_lock
from paho.mqtt import publish
import json

#DODATO
button_batch = []
publish_data_counter = 0
publish_data_limit = 2
counter_lock = threading.Lock()

def publisher_task(event, button_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_button_batch = button_batch.copy()
            publish_data_counter = 0
            button_batch.clear()
        try:
            publish.multiple(local_button_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} button values')
        except:
            print("greska")
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, button_batch,))
publisher_thread.daemon = True
publisher_thread.start()

#Nisam siguran je l ovo dobro
def button_callback(pressed, publish_event, settings):
    global publish_data_counter, publish_data_limit
    
    t = time.localtime()
    formatted_time = time.strftime('%d.%m.%Y. %H:%M:%S', t)

    with print_lock:
        print("="*20)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print("SETINGS ", settings)
        if pressed:
            print("Button is pressed - ",settings["name"])
        else:
            print("Button is not pressed - ",settings["name"])



    press_payload = {
        "measurement": "button_press",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
         "value": "pressed" if pressed else "closed",
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "datetime": formatted_time,
        "front":False
    }

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            press_payload["front"] = True
        button_batch.append(('topic/button', json.dumps(press_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()    


def run_button(settings, threads, stop_event):
        if settings['simulated']:
            with print_lock:
                print("Starting button sumilator which name is:" + settings["name"])
            button_thread = threading.Thread(target = run_button_simulator, args=(1, button_callback, stop_event, publish_event, settings))
            button_thread.start()
            threads.append(button_thread)
            with print_lock:
                print("button sumilator started which name is:" + settings["name"])
        else:
            from sensors.button import run_button_loop, Button
            with print_lock:
                print("Starting button loop which name is "+ settings["name"])
            button = Button(settings['name'],settings['port'])
            button_thread = threading.Thread(target=run_button_loop, args=(button, 2, button_callback, stop_event, publish_event, settings))
            button_thread.start()
            threads.append(button_thread)
            with print_lock:
                print("button loop started which name is "+ settings["name"])