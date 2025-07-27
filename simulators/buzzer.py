import time
import random
from queue import Empty

import pygame
print(pygame.__file__)

pygame.mixer.init()  # Inicijalizuj mixer
alarm_sound = pygame.mixer.Sound("C:\\Users\\NITRO\\Desktop\\incorrect-buzzer-sound-147336.mp3") 

# def run_buzzer_simulator(callback, stop_event, event_on, settings, pitch, duration,publish_event):
#     """
#     Simulacija buzzer-a.
#     :param callback: Callback funkcija za status.
#     :param stop_event: Event za zaustavljanje rada.
#     :param event_on: Event koji aktivira zvuk.
#     :param name: Ime buzzer-a.
#     :param pitch: Frekvencija zvuka.
#     :param duration: Trajanje zvuka.
#     """
#     """
#     Simulacija buzzer-a.
#     :param callback: Callback funkcija za status.
#     :param stop_event: Event za zaustavljanje rada.
#     :param event_on: Event koji aktivira zvuk.
#     :param name: Ime buzzer-a.
#     :param pitch: Frekvencija zvuka.
#     :param duration: Trajanje zvuka.
#     """
#     print("UDJE U SIMULATOR")
#     print(stop_event.is_set())
#     while not stop_event.is_set():
#         # Čekaj na signal za uključivanje zvuka
#         if event_on.wait(timeout=0.1):
#             print(f"{settings['name']} Buzzer Simulator: Aktiviran")
#             callback(True, settings, pitch, duration,publish_event)
            
#             # Simuliraj zvuk
#             print(f"Zvuk se pušta za {duration} sekundi.")
#             time.sleep(duration)
            
#             # Resetuj event i pozovi callback za isključivanje
#             event_on.clear()
#             callback(False, settings, pitch, duration,publish_event)
        
#         # Kratka pauza da izbegnemo preterano opterećenje CPU-a
#         time.sleep(0.1)

def run_buzzer_simulator(callback, stop_event,  settings,alarm_on_event,publish_event,bb_queue,alarm_clock_on_event, alarm_clock_off_event):
    delay = 1 
    pitch = 440
    duration = 0.5
    print("UDJE U SIMULATOR")
    current_clock_alarm = None
    called_callback = False
    while True:
        if stop_event.is_set():
            return
        if alarm_clock_on_event:
            while not alarm_clock_off_event.is_set():
                if alarm_on_event.is_set():

                    #play_alarm()
                    #status = "ON"
                    status = True
                    callback(status, settings, publish_event,True)
                    while alarm_on_event.is_set():
                        time.sleep(1)
                    stop_alarm()
                    #status = "OFF"
                    status = False
                    callback(status, settings, publish_event,True)
            
                try:
                    current_clock_alarm = bb_queue.get(timeout=1)
                except Empty:
                    pass
                if current_clock_alarm and is_after_current_time(current_clock_alarm['date'], current_clock_alarm['time']):
                    if not alarm_clock_on_event.is_set():
                        alarm_clock_on_event.set()
                    if not called_callback:
                        #status = "ON"
                        status = True
                        play_alarm()
                        callback(status, settings, publish_event,True)
                        called_callback = True
                    delay = 1.0 / (pitch*2)
                    time.sleep(delay)
                
            if alarm_on_event.is_set():
                print("UDJE OVDE U CALL3")
                #play_alarm()
                #status = "ON"
                status = True
                callback(status, settings, publish_event,True)
                while alarm_on_event.is_set():
                    time.sleep(1)
                #status = "OFF"
                status = False
                stop_alarm()
                callback(status, settings, publish_event,True)
            else:
                if current_clock_alarm:
                    called_callback = False
                    #status = "OFF"
                    status = False
                    stop_alarm()
                    callback(status, settings, publish_event,True)
                current_clock_alarm = None
        else:
            if alarm_on_event.is_set():
                #play_alarm()
                #status = "ON"
                status = True
                callback(status, settings, publish_event,True)
                while alarm_on_event.is_set():
                    time.sleep(1)
                stop_alarm()
                #status = "OFF"
                status = False
                callback(status, settings, publish_event,True)
            

def is_after_current_time(date_str, time_str):
    from datetime import datetime
    target_datetime = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
    current_datetime = datetime.now().replace(second=0, microsecond=0)
    return current_datetime >= target_datetime


def play_alarm():
    alarm_sound.play(-1)  # Loop beskonačno

def stop_alarm():
    alarm_sound.stop()
