import RPi.GPIO as GPIO
import time

#GPIO.setmode(GPIO.BCM)

#Create class with atributtes trig_pin and echo_pin
#TRIG_PIN = 23
#ECHO_PIN = 24

#GPIO.setup(TRIG_PIN, GPIO.OUT)
#GPIO.setup(ECHO_PIN, GPIO.IN)

#KOPIRANO SA VEZBI, SAMO UBACENO U KLASU

class UDS(object):
    def __init__(self,name, trig_pin, echo_pin):
        self.name = name
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        

    def get_distance(self):
        GPIO.output(self.trig_pin, False)
        time.sleep(0.2)
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)
        pulse_start_time = time.time()
        pulse_end_time = time.time()

        max_iter = 100

        iter = 0
        while GPIO.input(self.echo_pin) == 0:
            if iter > max_iter:
                return None
            pulse_start_time = time.time()
            iter += 1

        iter = 0
        while GPIO.input(self.echo_pin) == 1:
            if iter > max_iter:
                return None
            pulse_end_time = time.time()
            iter += 1

        pulse_duration = pulse_end_time - pulse_start_time
        distance = (pulse_duration * 34300)/2
        return distance

# if __name__ == '__main__':
#     try:
#         while True:
#             distance = get_distance()
#             if distance is not None:
#                 print(f'Distance: {distance} cm')
#             else:
#                 print('Measurement timed out')
#             time.sleep(1)
#     except KeyboardInterrupt:
#         GPIO.cleanup()
#         print('Measurement stopped by user')
#     except Exception as e:
#         print(f'Error: {str(e)}')


#KOPIRANO SA VEZBI3, OD DHT I PRIMENJENO NA UDS
def run_dht_loop(uds, delay, callback, stop_event,publish_event, settings):
        while True:
            distance = uds.get_distance()
            callback(distance,publish_event, settings)
            if stop_event.is_set():
                    break
            time.sleep(delay)  # Delay between readings