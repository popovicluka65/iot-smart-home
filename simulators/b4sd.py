import time

def generate_value():
    n = time.ctime()[11:13] + time.ctime()[14:16]
    return "{}:{}".format(n[0:2], n[2:])


# def run_b4sd_simulator(delay, callback, stop_event, publish_event, settings):
#     while True:
#         time_value = generate_value()
#         callback(time_value, publish_event, settings)
#         if stop_event.is_set():
#             break
#         #time.sleep(delay)
#         time.sleep(2)



 
def run_b4sd_simulator(delay,callback, stop_event, settings, b4sd_queue, alarm_on_event, alarm_off_event,publish_event):
    current_alarm = None
    while True:
        if alarm_off_event.is_set() and current_alarm:
            current_alarm = None
            alarm_on_event.clear()
        try: 
            alarm = b4sd_queue.get(timeout=1)
            current_alarm = alarm
        except: 
            pass

        current_time = time.ctime()[11:13]+time.ctime()[14:16]
        current_time_s = str(current_time[:2])+":"+str(current_time[2:])
        
        if current_alarm and is_after_current_time(current_alarm['date'], current_alarm['time']):
        # if current_alarm:
            print('tu')
            if not alarm_on_event.is_set():
                alarm_on_event.set()
            for _ in range(2):
                callback(current_time_s,publish_event,settings,True)
                time.sleep(0.5)
                callback("",publish_event,settings,True)
                time.sleep(0.5)
        else:
            callback(current_time_s,publish_event,settings,True)
            time.sleep(delay)
        if stop_event.is_set():
            break


#kao i u buzzeru

def is_after_current_time(date_str, time_str):
    from datetime import datetime
    target_datetime = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
    current_datetime = datetime.now().replace(second=0, microsecond=0)
    return current_datetime >= target_datetime