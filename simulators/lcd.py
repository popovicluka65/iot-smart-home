import time
import random
from queue import Empty

def generate_lcd_values():
    """Simulate random temperature and humidity values."""
    while True:
        temperature = random.uniform(15.0, 30.0)  # Simulate temperature in Celsius
        humidity = random.uniform(30.0, 70.0)  # Simulate humidity in percentage
        yield temperature, humidity


#MORA DA BUDE SINHRONIZOVANO SA GDHT


#def run_lcd_simulator(delay, callback, stop_event, settings):
    # """Run a simulated LCD loop that generates random values."""
    # for temperature, humidity in generate_lcd_values():
    #     time.sleep(delay)  # Delay between updates

    #     # Call the callback function with simulated values
    #     callback(settings, humidity, temperature)

    #     # Stop the simulator if stop_event is set
    #     if stop_event.is_set():
    #         break

def run_lcd_simulator(delay, callback, stop_event, settings, events,lcd_commands):

    if events is not None and lcd_commands is not None:
        while not stop_event.is_set():
            try:
                events.wait()
                temperature, humidity = lcd_commands.get(timeout=1)
                events.clear()
                callback(settings, humidity, temperature,True)
            except Empty:
                pass
            time.sleep(delay)
    else:
        for temperature, humidity in generate_lcd_values():
            time.sleep(delay)  # Delay between updates

            callback(settings, humidity, temperature,True)

            if stop_event.is_set():
                break
