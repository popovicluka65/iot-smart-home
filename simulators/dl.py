import time

# def run_dl_simulator(callback, stop_event, event_on, event_off, settings, publish_event):
#     #radi kada fiksno stavim na svake 2 sekunde
#     while True:
#         time.sleep(2)
#         #print("Simulacija ON event-a")
#         callback(True, settings, publish_event)
#         event_on.set()  # Simuliraj uključivanje
#         time.sleep(2)
#         #print("Simulacija OFF event-a")
#         callback(False, settings, publish_event)
#         event_off.set()

def run_dl_simulator(callback, stop_event, publish_event, settings, motion_detected_event):
    while not stop_event.is_set():
        # Čekaj da PIR detektuje pokret
        motion_detected_event.wait()

        # Uključi LED
        callback(True, settings,publish_event,  True)

        # Drži LED upaljen 10 sekundi
        time.sleep(10)

        # Isključi LED
        callback(False,settings,publish_event,  True)

        # Očisti event da bi se čekalo na sledeći pokret
        motion_detected_event.clear()
