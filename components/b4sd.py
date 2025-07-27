import threading
from locks import print_lock
import time
import threading
from locks import print_lock
import paho.mqtt.publish as publish
import json
from simulators.b4sd import run_b4sd_simulator
import paho.mqtt.client as mqtt

b4sd_batch = []
publish_data_counter = 0
publish_data_limit = 3
counter_lock = threading.Lock()


def publisher_task(event, b4sd_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_rgb_batch = b4sd_batch.copy()
            publish_data_counter = 0
            b4sd_batch.clear()
        publish.multiple(local_rgb_batch,  hostname="localhost", port=1883)
        print(f'Showed {publish_data_limit}= values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, b4sd_batch,))
publisher_thread.daemon = True
publisher_thread.start()


def b4sd_callback(time_value, publish_event,settings,verbose=True):
    global publish_data_counter, publish_data_limit
    t = time.localtime()
    if verbose:
        with print_lock:
    
            print("=" * 10)
            print(settings["name"])
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"Time: {time_value}")

    payload = {
        "measurement": "b4sd",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": time_value,
        "front": False
    }

    with counter_lock:
        if publish_data_counter + 1 >= publish_data_limit:
            payload["front"] = True
        b4sd_batch.append(('topic/b4sd', json.dumps(payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def on_connect(client: mqtt.Client, userdata: any, flags, result_code):
    print("Connected with result code "+str(result_code))
    client.subscribe("topic/clock-alarm-gadget/on")
    client.subscribe("topic/clock-alarm-gadget/off")

def on_message(msg, b4sd_queue, bb_queue, alarm_off_event):
    print(msg.topic)
    if msg.topic == "topic/clock-alarm-gadget/off":
        alarm_off_event.set()
    else:
        data = json.loads(msg.payload.decode('utf-8'))
        alarm_off_event.clear()
        b4sd_queue.put(data)
        bb_queue.put(data)

def run_b4sd(settings, threads, stop_event, b4sd_queue, bb_queue, alarm_on_event, alarm_off_event):

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = lambda client, userdata, msg: on_message(msg, b4sd_queue, bb_queue, alarm_off_event)
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()
    

    if settings['simulated']:
        print("Starting {} simulator".format(settings["name"]))
        b4sd_thread = threading.Thread(target=run_b4sd_simulator, args=(3, b4sd_callback, stop_event, settings, b4sd_queue, alarm_on_event, alarm_off_event,publish_event))
        b4sd_thread.start()
        threads.append(b4sd_thread)
        print("{0} simulator started".format(settings["name"]))
    else:
        from sensors.b4sd import run_b4sd_loop, B4SD
        print("Starting {} loop".format(settings["name"]))
        b4sd = B4SD(settings)
        b4sd_thread = threading.Thread(target=run_b4sd_loop, args=(b4sd, 2, b4sd_callback, stop_event, publish_event, settings))
        b4sd_thread.start()
        threads.append(b4sd_thread)
        print("{} loop started".format(settings["name"]))