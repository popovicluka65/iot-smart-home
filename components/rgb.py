import threading
import time
from simulators.rgb import run_rgb_simulator
from locks import print_lock
import paho.mqtt.publish as publish
import json
import paho.mqtt.client as mqtt

rgb_batch = []
publish_data_counter = 0
publish_data_limit = 2
counter_lock = threading.Lock()

def publisher_task(event, rgb_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_rgb_batch = rgb_batch.copy()
            publish_data_counter = 0
            rgb_batch.clear()
        try:
            publish.multiple(local_rgb_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} rgb')
        except:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, rgb_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def rgb_callback(status, publish_event, settings, verbose=False):
    global publish_data_counter, publish_data_limit

    t = time.localtime()
    if verbose:
        with print_lock:
            print("="*10)
            print(settings['name'], end=" ")
            print("="*10)
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"Status: {status}\n")

    rgb_payload = {
        "measurement": "rgb_changed",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": status,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "front": True,
        "datetime": time.strftime('%d.%m.%Y. %H:%M:%S', t)
    }

    with counter_lock:
        rgb_batch.append(('topic/rgb', json.dumps(rgb_payload), 0,True))
        #rgb_batch.append(('topic/rgb', json.dumps(rgb_payload), 0, False))
        publish_data_counter += 1

        if publish_data_counter >= publish_data_limit:
            publish_event.set()

def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)
    client.subscribe("topic/rgb/color")

def on_message(client, userdata, msg):
    print("UDJE U ON MESSAGE")
    data_queue, color_event = userdata
    print(data_queue)
    print(color_event)
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        color = data.get("color")
        if color:
            data_queue.put(color.lower())
            color_event.set()
            print(f"[MQTT] Color command received: {color.lower()}")
        else:
            print(f"[MQTT] Invalid color payload: {data}")
    except Exception as e:
        print(f"[MQTT] Error: {e}")

def run_rgb(settings, threads, stop_event, input_queue,bir_rgb_event):
    sensor_name = settings["name"]

    mqtt_client = mqtt.Client(userdata=(input_queue, bir_rgb_event))
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()

    if settings['simulated']:
        print("UDJE U SIMULATED")
        with print_lock:
            print(f"Starting {sensor_name} simulator")
        rgb_thread = threading.Thread(target = run_rgb_simulator, args=(input_queue, 2, rgb_callback, stop_event, publish_event, settings,bir_rgb_event))
        rgb_thread.start()
        threads.append(rgb_thread)
        with print_lock:
            print(f"{sensor_name} simulator started")
    else:
        from sensors.rgb import run_rgb_loop, RGB
        print("UDJE U NOT SIMULATED")

        with print_lock:
            print(f"Starting {sensor_name} loop")
        dl = RGB(RED = settings['red_pin'], GREEN = settings['green_pin'], BLUE = settings['blue_pin'])
        rgb_thread = threading.Thread(target=run_rgb_loop, args=(input_queue, dl, 2, rgb_callback, stop_event, publish_event, settings))
        rgb_thread.start()
        threads.append(rgb_thread)
        with print_lock:
            print(f"{sensor_name} loop started")