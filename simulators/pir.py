import time
import random

def generate_pir_values():
    # Simulacija detekcije pokreta
    motion_state = False  # Početni status (nema pokreta)
    while True:
        # Nasumično generisanje stanja (pokret ili ne)
        motion_state = random.choice([True, False])
        yield motion_state  # Vraća True ako je pokret detektovan, inače False
        time.sleep(0.5)  # Delay između čitanja (može da se prilagodi)

def run_pir_simulator(delay, callback, stop_event, publish_event, settings, motion_detected_event):
    for motion_detected in generate_pir_values():
        time.sleep(delay) 

        #if motion_detected:
        if motion_detected_event:
            motion_detected_event.set()

        # Pozovi PIR callback uvek sa trenutnim stanjem
        callback(motion_detected, publish_event, settings,True)

        if stop_event.is_set():
            break 
