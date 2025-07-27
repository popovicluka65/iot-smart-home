from simulators.dht import run_dht_simulator
import threading
import time
from locks import print_lock
from paho.mqtt import publish
import json

dht_batch = []
publish_data_counter = 0
publish_data_limit = 3
counter_lock = threading.Lock()
def publisher_task(event, dht_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_dht_batch = dht_batch.copy()
            publish_data_counter = 0
            dht_batch.clear()
        try:
            publish.multiple(local_dht_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} dht values')
        except:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dht_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def dht_callback(humidity, temperature, code,publish_event,settings,verbose = True):
    print("UDJE U DHT CALLBACK")
    global publish_data_counter, publish_data_limit
    t = time.localtime()
    if verbose:
        with print_lock:
            print("="*20)
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"Code: {code}")
            print(f"Humidity: {humidity}%")
            print(f"Temperature: {temperature}°C")
            print(f"Name: {settings['name']}")
    
    #DODATO
    temperature_payload = {
        "measurement": "Temperature",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": temperature,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "datetime":time.strftime('%d.%m.%Y. %H:%M:%S', time.localtime()),
        "front": False,
    }

    humidity_payload = {
        "measurement": "Humidity",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": humidity,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "datetime":time.strftime('%d.%m.%Y. %H:%M:%S', time.localtime()),
        "front": False,
        
    }

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            temperature_payload["front"] = True
            humidity_payload["front"] = True
        dht_batch.append(('topic/temperature', json.dumps(temperature_payload), 0, True))
        dht_batch.append(('topic/humidity', json.dumps(humidity_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_dht(settings, threads, stop_event,events = None, lcd_commands = None):
        if settings['simulated']:
            with print_lock:
                print("Starting dht1 sumilator which name is:" + settings["name"])
            dht1_thread = threading.Thread(target = run_dht_simulator, args=(2, dht_callback, stop_event, publish_event,settings,events,lcd_commands))
            dht1_thread.start()
            threads.append(dht1_thread)
            with print_lock:
                print("Dht1 sumilator started which name is:" + settings["name"])
        else:
            from sensors.dht import run_dht_loop, DHT
            with print_lock:
                print("Starting dht1 loop which name is "+ settings["name"])
            dht = DHT(settings['pin'])
            dht1_thread = threading.Thread(target=run_dht_loop, args=(dht, 2, dht_callback, stop_event, publish_event,settings,events))
            dht1_thread.start()
            threads.append(dht1_thread)
            with print_lock:
                print("Dht1 loop started which name is "+ settings["name"])
