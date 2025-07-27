from simulators.pir import run_pir_simulator
import threading
import time
from locks import print_lock
import paho.mqtt.publish as publish
import json

pir_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()

def publisher_task(event, pir_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_pir_batch = pir_batch.copy()
            publish_data_counter = 0
            pir_batch.clear()
        try:
            publish.multiple(local_pir_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} pir values')
        except:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, pir_batch,))
publisher_thread.daemon = True
publisher_thread.start()


def pir_callback(is_motion_detected, publish_event, settings,verbose = True):
    global publish_data_counter, publish_data_limit
    t = time.localtime()
    value = ""
    with print_lock:
        print("=" * 20)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        if is_motion_detected:
            value = "move"
            print("Senzor je detektovao pokret.")
        else:
            value = "not move"
            print("Senzor ne detektuje pokret.")
        print(f"Sensor name: {settings['name']}")
    
    move_payload = {
        "measurement": "move",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": value,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "front":False
    }

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            move_payload["front"] = True
        pir_batch.append(('topic/move', json.dumps(move_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()



# def run_pir(settings, threads, stop_event):
def run_pir(settings, threads, stop_event, motion_detected_event = None):
    print("UDJE OVDE ",settings["name"])
    if settings['simulated']:
        with print_lock:
            print(f"Starting PIR simulator with name: {settings['name']}")
        #11 sekundi samo za proveru
        pir_thread = threading.Thread(target=run_pir_simulator, args=(11, pir_callback, stop_event, publish_event, settings, motion_detected_event))
        pir_thread.start()
        threads.append(pir_thread)
        with print_lock:
            print(f"PIR simulator started with name: {settings['name']}")
    else:
        # PIR senzor nije simuliran, već pravi senzor
        from sensors.pir import run_pir_loop, PIR  # Pretpostavka da imate PIR klasu
        with print_lock:
            print(f"Starting PIR loop with name: {settings['name']}")
        pir_sensor = PIR(settings["name"], settings["pin"])
        pir_thread = threading.Thread(target=run_pir_loop, args=(pir_sensor, 11, pir_callback, stop_event, publish_event, settings))
        pir_thread.start()
        threads.append(pir_thread)
        with print_lock:
            print(f"PIR loop started with name: {settings['name']}")