import time
import random

#TEMPERATURE AND HUMIDITY SENSOR
#3.3V , PORTS ON Raspberry Pi are 1 and 17
def generate_values(initial_temp=25, initial_humidity=20):
    temperature = initial_temp
    humidity = initial_humidity
    while True:
        temperature = temperature + random.randint(-1, 1)
        humidity = humidity + random.randint(-1, 1)
        if humidity < 0:
            humidity = 0
        if humidity > 100:
            humidity = 100
        yield humidity, temperature


def run_dht_simulator(delay, callback, stop_event,  publish_event, settings,events,lcd_commands):
    for h, t in generate_values():
        time.sleep(delay)  # Delay between readings (adjust as needed)
        if lcd_commands:
            lcd_commands.put([t,h])
        if events:
            events.set()
        callback(h, t, "DHTLIB_OK",  publish_event, settings,False)
        if stop_event.is_set():
            break
              