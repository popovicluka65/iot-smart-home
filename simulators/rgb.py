from queue import Empty
import time
import random 

#GPT IZGENERISAO
class RGB(object):
     def __init__(self) -> None:
         self.status = "off"

         self.supported_commands = ['off', 'red', 'blue', 'purple', 'white', 'yellow', 'light blue', 'green']

     def resolve_command(self, command):
            if command in self.supported_commands:
                if command != self.status:
                    self.status = command
                    return True
            else:
                print(f"Invalid RGB diode command: {command}")

            return False

#OVO JE INACE ALI SAD DOK NE NAMESTIM UNOS SA TASTATURE NEK BUDE ONO ISPOD 

# def run_rgb_simulator(input_queue, delay, callback, stop_event, publish_event, settings):
#     rgb = RGB()
#     while not stop_event.is_set():
#         try:
#             action = input_queue.get(timeout=1)
#             status_changed = rgb.resolve_command(action)

#             if status_changed:
#                 print("BRGB lights are " + action)
#                 callback(rgb.status, publish_event, settings, True)
#         except Empty:
#             pass
#         time.sleep(delay)

def run_rgb_simulator(input_queue, delay, callback, stop_event, publish_event, settings,bir_rgb_event):
    rgb = RGB()
    
    while not stop_event.is_set():
        try:
            bir_rgb_event.wait()
            action = input_queue.get(timeout=1)
            status_changed = rgb.resolve_command(action)
            
            bir_rgb_event.clear()
            if status_changed:
                print("BRGB lights are " + action)
                callback(rgb.status, publish_event, settings, True)
        except Empty:
            pass
        time.sleep(delay)

