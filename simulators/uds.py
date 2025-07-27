import time
import random

#GPT GENERISAO SIMULACIJU
def generate_values():
    distance = random.randint(5, 100)  # Početna udaljenost
    sign = 1  # Smer promene vrednosti (+ ili -)
    while True:
        delta = random.randint(1, 10)
        distance += delta * sign
        if random.random() < 0.1:  # 10% šansa za grešku
            yield None  # Greška u očitavanju
            continue

        # Provera da li je udaljenost izašla van opsega
        if distance > 120 or distance < 3:
            sign *= -1  # Promena smera kretanja
            distance = max(3, min(distance, 120))  # Ograničavanje na dozvoljeni opseg

        yield distance
        time.sleep(0.5) 


def run_uds_simulator(delay, callback, stop_event,  publish_event, settings):
    for d in generate_values():
        time.sleep(delay)  # Delay between readings (adjust as needed)
        callback(d,  publish_event, settings,True)
        if stop_event.is_set():
            break