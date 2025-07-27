from simulators.gyro import run_gyro_simulator
import threading
import time
from locks import print_lock
import json
import paho.mqtt.publish as publish

publish_event = threading.Event()
gyro_batch = []
publish_data_counter = 0
publish_data_limit = 2
counter_lock = threading.Lock()

def publisher_task(event, gyro_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_gyro_batch = gyro_batch.copy()
            publish_data_counter = 0
            gyro_batch.clear()
        try:
            publish.multiple(local_gyro_batch, hostname="localhost", port=1883)
            print(f'Publish {publish_data_limit} gyroscopes')
        except Exception as e:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, gyro_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def gyro_callback(angle, publish_event, gyro_settings,verbose = True):
    global publish_data_counter, publish_data_limit
    t = time.localtime()
    if verbose:
        with print_lock:
            print("="*10, end=" ")
            print(gyro_settings['name'], end=" ")
            print("="*10)
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"Rotation x: {angle['gyro_rot_x']}")
            print(f"Rotation y: {angle['gyro_rot_y']}")
            print(f"Rotation z: {angle['gyro_rot_z']}")

    #dodati sta ako treba
    angle_payload_x = {
        "measurement": "angle",
        "simulated": gyro_settings['simulated'],
        "runs_on": gyro_settings["runs_on"],
        "name": gyro_settings["name"],
        "value": angle["gyro_rot_x"],
        "field": gyro_settings["influxdb_field"],
        "bucket": gyro_settings["influxdb_bucket"],
        "front": False,
        "axis": "x" 
    }

    angle_payload_y = {
        "measurement": "angle",
        "simulated": gyro_settings['simulated'],
        "runs_on": gyro_settings["runs_on"],
        "name": gyro_settings["name"],
        "value": angle["gyro_rot_y"],
        "field": gyro_settings["influxdb_field"],
        "bucket": gyro_settings["influxdb_bucket"],
        "front": False,
        "axis": "y" 
    }

    angle_payload_z = {
        "measurement": "angle",
        "simulated": gyro_settings['simulated'],
        "runs_on": gyro_settings["runs_on"],
        "name": gyro_settings["name"],
        "value": angle["gyro_rot_z"],
        "field": gyro_settings["influxdb_field"],
        "bucket": gyro_settings["influxdb_bucket"],
        "front": False,
        "axis": "z" 
    }

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            angle_payload_x["front"] = True
            angle_payload_y["front"] = True
            angle_payload_z["front"] = True
        gyro_batch.append(('topic/gyro/angle', json.dumps(angle_payload_x), 0, True))
        gyro_batch.append(('topic/gyro/angle', json.dumps(angle_payload_y), 0, True))
        gyro_batch.append(('topic/gyro/angle', json.dumps(angle_payload_z), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_gyro(settings, threads, stop_event):
    sensor_name = settings["name"]
    if settings['simulated']:
        with print_lock:    
            print(f"Starting {sensor_name} simulator")
        gyro_thread = threading.Thread(target = run_gyro_simulator, args=(6, gyro_callback, stop_event, publish_event, settings))
        gyro_thread.start()
        threads.append(gyro_thread)
        with print_lock: 
            print(f"{sensor_name} simulator started")
    else:
        from sensors.gyro.gyro import run_gyro_loop, Gyroscope
        with print_lock:    
            print(f"Starting {sensor_name} loop")
        gyro = Gyroscope()
        gyro_thread = threading.Thread(target=run_gyro_loop, args=(gyro, 2, gyro_callback, stop_event, publish_event, settings))
        gyro_thread.start()
        threads.append(gyro_thread)
        with print_lock: 
            print(f"{sensor_name} loop start")