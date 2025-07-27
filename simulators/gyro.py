import time
import random

def generate_values():
    while True:
        gyro_rot_x = random.randint(-50, 50) / 10.0
        gyro_rot_y = random.randint(-50, 50) / 10.0
        gyro_rot_z = random.randint(-50, 50) / 10.0
       
        yield {
            "gyro_rot_x": gyro_rot_x,
            "gyro_rot_y": gyro_rot_y,
            "gyro_rot_z": gyro_rot_z
        }

        time.sleep(0.1)

def run_gyro_simulator(delay, callback, stop_event, publish_event, settings):
        for a in generate_values():
            time.sleep(delay)  # Delay between readings (adjust as needed)
            callback(a, publish_event, settings,True)
            if stop_event.is_set():
                  break