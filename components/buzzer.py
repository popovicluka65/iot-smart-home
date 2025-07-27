from simulators.buzzer import run_buzzer_simulator
import threading
import time
#import pygame
#print(pygame.__file__)
from locks import print_lock
import paho.mqtt.publish as publish
import json
import paho.mqtt.client as mqtt
import pygame
print(pygame.__file__)
#from server.server import socketio

buzzer_batch = []
publish_data_counter = 0
publish_data_limit = 1
counter_lock = threading.Lock()

def publisher_task(event, buzzer_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_buzzer_batch = buzzer_batch.copy()
            publish_data_counter = 0
            buzzer_batch.clear()
        try:
            publish.multiple(local_buzzer_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} buzzer values')
        except:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, buzzer_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def buzzer_callback(status, settings,publish_event,verbose = True):
    global publish_data_counter, publish_data_limit
    t = time.localtime()
    print("UDJE OVDE u callback")
    if verbose:
        with print_lock:
            #play_sound()
            print("="*10)
            print(settings['name'], end=" ")
            print("="*10)
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"{settings['name']} Buzzer: {status}")
    

    # buzzer_payload = {
    #     "measurement": "buzzerbool",
    #     "simulated": settings['simulated'],
    #     "runs_on": settings["runs_on"],
    #     "name": settings["name"],
    #     #"value": status,
    #     "value": status,
    #     #"field": settings["influxdb_field"],
    #     #"bucket": settings["influxdb_bucket"],
    #     "front": False,
    #     "datetime": time.strftime('%d.%m.%Y. %H:%M:%S', t)
    # }

    buzzer_payload = {
        "measurement": "buzzer123",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": status,
        "front": False,
        "datetime": time.strftime('%d.%m.%Y. %H:%M:%S', t)
    }
    

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            buzzer_payload["front"] = True
        print("KOMPONENTA BUZZER")
        buzzer_batch.append(('topic/buzzer', json.dumps(buzzer_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def play_sound():
    pygame.mixer.init()  # Inicijalizuj mixer
    sound = pygame.mixer.Sound("C:\\Users\\NITRO\\Desktop\\incorrect-buzzer-sound-147336.mp3")  # Učitaj zvučni fajl
    sound.play()  # Pusti zvu

#GPT 

def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)
    #iz servera
    client.subscribe("topic/alarm/buzzer/on")
    client.subscribe("topic/alarm/buzzer/off")

def on_message(msg, alarm_on_event):
    if msg.topic == "topic/alarm/buzzer/on":
        alarm_on_event.set()
    elif msg.topic == "topic/alarm/buzzer/off":
        alarm_on_event.clear()


def run_buzzer(settings, threads, stop_event,alarm_on_event, bb_queue = None,  alarm_clock_on_event = None, alarm_clock_off_event= None):
   

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = lambda client, userdata, msg: on_message(msg, alarm_on_event)
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()
    

    if settings['simulated']:
        with print_lock:
            print(f"Starting buzzer simulator: {settings['name']}")
        buzzer_thread = threading.Thread(
            target=run_buzzer_simulator,
            args=(buzzer_callback, stop_event,  settings,alarm_on_event,publish_event,bb_queue,alarm_clock_on_event, alarm_clock_off_event)
        )
    else:
        from sensors.buzzer import run_buzzer_loop, Buzzer
        buzzer = Buzzer(settings['name'], settings['pin'])
        with print_lock:
            print(f"Starting buzzer: {settings['name']}")
        buzzer_thread = threading.Thread(
            target=run_buzzer_loop,
            #args=(buzzer, pitch, duration, stop_event, event_on, publish_event)
        )
    
    buzzer_thread.start()
    threads.append(buzzer_thread)
    with print_lock:
        print(f"Buzzer started: {settings['name']}")