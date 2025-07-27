from simulators.lcd import run_lcd_simulator
import threading
import time
from locks import print_lock
from paho.mqtt import publish
import json

lcd_batch = []
publish_data_counter = 0
publish_data_limit = 1
counter_lock = threading.Lock()
def publisher_task(event, lcd_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_lcd_batch = lcd_batch.copy()
            publish_data_counter = 0
            lcd_batch.clear()
        try:
            publish.multiple(local_lcd_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} dht values')
        except:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, lcd_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def lcd_callback(settings,humidity, temperature,verbose = False):
    global publish_data_counter, publish_data_limit
    print(settings)
    if verbose:
        t = time.localtime()
        with print_lock:
            print("="*20)
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"Name: {settings['name']} ")
            print(f"Humidity: {humidity}")
            print(f"Temperature: {temperature}")

    #prekopirano od GDHT

    t_payload = {
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

    h_payload = {
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
            t_payload["front"] = True
            h_payload["front"] = True
        lcd_batch.append(('topic/lcd/temperature', json.dumps(t_payload), 0, True))
        lcd_batch.append(('topic/lcd/humidity', json.dumps(h_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_lcd(settings, threads, stop_event,events = None, lcd_commands = None):
        if settings['simulated']:
            with print_lock:
                print("Starting lcd sumilator which name is:" + settings["name"])
            lcd_thread = threading.Thread(target = run_lcd_simulator, args=(2, lcd_callback, stop_event,settings,events,lcd_commands))
            lcd_thread.start()
            threads.append(lcd_thread)
            with print_lock:
                print("lcd sumilator started which name is:" + settings["name"])
        else:
            #IZMENITI OVDE STA TREBA
            from sensors.lcd.LCD1602 import run_lcd_loop, LCD
            with print_lock:
                print("Starting lcd loop which name is "+ settings["name"])
            #lcd = LCD(settings['name'],settings['port'])
            lcd = LCD(pin_rs=settings['pin_rs'], pin_e=settings['pin_e'], pins_db=settings['pins_db'])
            lcd_thread = threading.Thread(target=run_lcd_loop, args=(lcd, 2, lcd_callback, stop_event,settings))
            lcd_thread.start()
            threads.append(lcd_thread)
            with print_lock:
                print("lcd loop started which name is "+ settings["name"])