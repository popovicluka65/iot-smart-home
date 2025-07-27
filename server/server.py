from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import json
from flask_cors import CORS
from flask_socketio import SocketIO
import threading
import time


time_press_ds1 = 0
time_press_ds2 = 0
ds_alarm = False
ds_lock = threading.Lock()
people_count = 0
people_count_lock = threading.Lock()

#sve za dms
ALARM_PIN = "0001"
dms_alarm_is_active = False
dms_alarm_lock = threading.Lock()
dms_pin_arrived_event = [threading.Event(), threading.Event()]
start_countdown_event = [threading.Event(), threading.Event()]
#ako se jeda
dms_alarm_ring = [False, False]

app = Flask(__name__)

#GPT DODAO
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:4200"], logger=True, engineio_logger=True)

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('custom_event')
def handle_custom_event(data):
    print(f"Received data: {data}")
    # Emitovanje događaja nazad klijentu
    socketio.emit('response_event', {"status": "success"})

#LUKA POPOVIC
#token = "faG2QzteThertmKVTMH3SYPtlLvz_IPbtTtn2XpG1VI2MyQOHwKju9R65t9HJ6N79aCLTPE9eiWOzOXeKsHVuA=="
token = "Mxf2IYnaHrCDxWPPRa9O8rLIl9M0_mTWRD5ZPs3mmMIb6PM0H4HulA8BAf7_sjIABk0ZrMyyq4SF4X5X22rprQ=="

org = "IOT-grupa1-tim4"
url = "http://localhost:8086"
bucket = "example_db"
influxdb_client = InfluxDBClient(url=url, token=token, org=org)


# MQTT Configuration
mqtt_client = mqtt.Client()
#mqtt_client.connect("localhost", 1883, 60)
#mqtt_client.loop_start()


#OVDE DODAVATI STA TREBA
def on_connect(client, userdata, flags, rc):
    client.subscribe("topic/temperature")
    client.subscribe("topic/humidity")
    client.subscribe("topic/button")
    client.subscribe("topic/buzzer")
    client.subscribe("topic/distance")
    client.subscribe("topic/move")
    client.subscribe("topic/keypad")
    client.subscribe("topic/dl")
    client.subscribe("topic/gyro/angle")
    client.subscribe("topic/b4sd")
    client.subscribe("topic/infrared")
    client.subscribe("topic/rgb")
    client.subscribe("topic/lcd/temperature")
    client.subscribe("topic/lcd/humidity")
    
    

#PRE
# mqtt_client.on_connect = on_connect
# mqtt_client.on_message = lambda client, userdata, msg: save_to_db(json.loads(msg.payload.decode('utf-8')))
#mqtt_client.on_message = lambda client, userdata, msg: on_message_callback(client, userdata, msg)
#mqtt_client.loop_start()

#GPT

mqtt_client.on_connect = on_connect
mqtt_client.on_message = lambda client, userdata, msg: on_message_callback(client, userdata, msg)

# 2. Poveži se
mqtt_client.connect("localhost", 1883, 60)

# 3. Pokreni loop
mqtt_client.loop_start()

def save_to_db(data):
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

    
    print("Primljeni podaci: ", data) 
    if data['name']=="Buzzer" or data['name']=="Buzzer2":
        value = data["value"]
        if isinstance(value, str):
            if value.upper() == "ON":
                value = 1
            elif value.upper() == "OFF":
                value = 0
            elif isinstance(value, bool):
                value = 1 if value else 0
        print("DATA BUZZER",data)
        print("value",value)
        point = Point("buzzer123") \
        .field("value",value) \
        .field("front", False) \
        .tag("simulated",  data["simulated"]) \
        .tag("runs_on",  data["runs_on"]) \
        .tag("name", data["name"]) \
        
    else:
        point = (
            Point(data["measurement"])
            .tag("simulated", data["simulated"])
            .tag("runs_on", data["runs_on"])
            .tag("name", data["name"])
            .field("measurement", data["value"])
        )

   
    write_api.write(bucket=bucket, org=org, record=point)
    if data.get("front"):
        print("USAO U UPDATE FRONT")
        update_frontend(data)

def on_message_callback(client, userdata, msg):
    #3 tacka u alarmima
    if msg.topic == "topic/button":
        data = json.loads(msg.payload.decode('utf-8'))
        global ds_lock, time_press_ds1, time_press_ds2
        if data["name"] == "BUTTON1":
            with  ds_lock:
                #print("UDJE U DS LOCK")
                if data["value"] == "pressed":
                    time_press_ds1 = time.time() 
                    print("time u petlji", time_press_ds1)
                else:
                    time_press_ds1 = 0
                    if dms_alarm_is_active:
                        start_countdown_event[0].set()
        if data["name"] == "BUTTON2":
            with ds_lock:
                if data["value"] == "pressed":
                    time_press_ds2 = time.time() 
                else:
                    time_press_ds2 = 0
                    if dms_alarm_is_active:
                        start_countdown_event[1].set()
        save_to_db(data)
    #6 tacka u alarmima
    elif msg.topic == "topic/gyro/angle":
        print("udje u ziroskop cek")
        check_gyro_alarms(json.loads(msg.payload.decode('utf-8')))
        save_to_db(json.loads(msg.payload.decode('utf-8')))
    #tacka 8
    elif msg.topic == "topic/b4sd":
        print("Stigla B4SD poruka")
        payload = json.loads(msg.payload.decode('utf-8'))
        print(payload)
        save_to_db(payload)
        # Emituj kroz SocketIO
        socketio.emit("B4SD", payload)
    #7 tacka
    elif msg.topic == "topic/lcd/temperature" or msg.topic == "topic/lcd/humidity":
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"LCD poruka na topic {msg.topic}: {payload}")
        save_to_db(payload)
        socketio.emit("lcd_data", payload)
    #5 tacka i 2 tacka
    elif msg.topic == "topic/move":
        print("AKTIVIRAO SE PIR")
        payload = json.loads(msg.payload.decode('utf-8'))
        print(payload)
        #5 tacka
        if "RPIR" in payload["name"]:
            with people_count_lock:
                if people_count == 0:
                    print("USAO U ALARM ZA RPIR")
                    raise_alarm(payload, message=f"DETECTED MOVE ON RPIR {payload['name']} BUT THERE ARE NO PEOPLE")     
        if "DPIR" in payload["name"]:
            print("UDJE U CECK")
            check_uds_distance(payload["name"], payload["runs_on"])
        save_to_db(payload)
        
    #4 tacka
    if msg.topic == "topic/ms/code":
        try:
            message = json.loads(msg.payload.decode('utf-8'))
            code = message["code"]
        except Exception as e:
            print(str(e))
            return
        save_to_db(data) 
        process_dms_code_received(code)
    elif msg.topic == "topic/rgb/color":
        payload = json.loads(msg.payload.decode('utf-8'))
        color = payload.get('color')
        if color:
            print(f"RGB COLOR COMMAND RECEIVED FROM MQTT: {color}")
    elif msg.topic == "topic/distance":
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"Distance data received: {payload}")  # da vidiš da stiže
        save_to_db(payload)
    #da se oglasava alarm
    elif msg.topic == "topic/buzzer":
        print(f"UDJE U ALARM TOPIC")
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"Distance data received: {payload}")  # da vidiš da stiže
        socketio.emit("buzzer",payload)
        save_to_db(payload)
        
    elif msg.topic == "topic/keypad":

        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"DMS: {payload}")  # da vidiš da stiže
        #save_to_db(payload)
    #da bi se sacuvalo u bazi za gdht
    elif msg.topic == "topic/temperature" or msg.topic == "topic/humidity":
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"DHT {msg.topic}: {payload}")
        save_to_db(payload)
    elif msg.topic == "topic/dl":
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"DL {msg.topic}: {payload}")
        save_to_db(payload)

#tacka 3
def ds_update():
    global ds_lock, time_press_ds1, time_press_ds2, ds_alarm
    while True:
        time.sleep(1)
        #print("vreme", time_press_ds1)
        with ds_lock:
            if not time_press_ds1 and ds_alarm:
                turn_ds_alarm_off(data)
                
            if time_press_ds1 and (time.time() - time_press_ds1 > 5):
                data = {"name": "Door Sensor 1"}
                #print("UDJE DA AKTIVIRA ALARM")
                if not ds_alarm:
                    raise_alarm(data, message=f"Door 1 has been opened for more than 5 seconds")
                ds_alarm = True
        with ds_lock:
            if not time_press_ds2 and ds_alarm:
                turn_ds_alarm_off(data)
            if time_press_ds2 and time.time() - time_press_ds2 > 5:
                data = {"name": "Door Sensor 2"}
                if not ds_alarm:
                    raise_alarm(data, message=f"Door 2 has been opened for more than 5 seconds")
                ds_alarm = True

def raise_alarm(data, message="", verbose=True):
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    try:
        point = (
                Point("alarm")
                .tag("name sensor", data["name"])
                .tag("message", message)
                .field("status", "ON")
            ) 
        
        write_api.write(bucket=bucket, org=org, record=point)
        alarm_data = {
            "caused_by": data["name"],
            "message": message,
            "status": "ON",
            "timestamp": time.strftime('%d.%m.%Y. %H:%M:%S', time.localtime())
        }
        if verbose:
            print("Sound the alarm")
            print("mes", message)
        
        alarm_frontend(alarm_data)
        #potencijalno obrisati ovo
        #mqtt_client.publish("topic/alarm/buzzer/on", json.dumps(alarm_data))

    
    except Exception as e:
        print(str(e))
        pass

def turn_ds_alarm_off(settings):
    with app.app_context():
        sensor_name = settings["name"]
        #print("gasenje alarma")
        global  ds_alarm
        ds_alarm = False
        write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
        try:
            point = (
                    Point("alarm")
                    .tag("caused_by", sensor_name)
                    .tag("message", "Alarms turned off by closing door")
                    .field("status", "OFF")
                ) 
            alarm_data = {
                "caused_by": sensor_name,
                "message": "Alarms turned off by closing door",
                "status": "OFF"
            }
            alarm_frontend(({"status": "OFF"}))

            write_api.write(bucket=bucket, org=org, record=point)
            mqtt_client.publish("topic/alarm/buzzer/off", json.dumps(alarm_data))

        except Exception as e:
            print(str(e))

def check_gyro_alarms(data):
    #posto je vrednost gyroskopa od -5 do 5 ako je po apsolutnoj vrednosti veci od 4 prijavljujemo problem
    if abs(data["value"]) > 4:
        print("UDJE U CHECK GYRO",data)
        raise_alarm(data, message=f"significant change detected via {data['axis']} axis")

#KUPLJENJE SA FRONTA KEYPAD
@app.route('/dms/code', methods=['PUT'])
def update_dms_code():
    #global dms_alarm_activation_code, dms_alarm_is_active, dms_pin_arrived_event, dms_alarm_ringing
    try:
        data = request.get_json()
        code = data.get('code', None)

        if code is not None:
            print(f"Received code1: {code}")
            process_dms_code_received(code)

            return jsonify({'message': 'Code updated successfully'}), 200
        else:
            return jsonify({'error': 'Code not provided'}), 400

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

#za 4 tacku 

def process_dms_code_received(code: str):
    global dms_alarm_is_active,ALARM_PIN, dms_pin_arrived_event, dms_alarm_ring
    #srediti ovo
    if code == ALARM_PIN and not dms_alarm_is_active:
        with dms_alarm_lock:
            print("DMS ALARM ACTIVATED **************")
            dms_alarm_is_active = True
    elif code == ALARM_PIN and dms_alarm_is_active:
        with dms_alarm_lock:
            dms_alarm_is_active = False

            print("DMS ALARM DEACTIVATED **************")
        if dms_alarm_ring[0] or dms_alarm_ring[1]:
            #TODO: na front posalji da prestane alarm
            print("DMS ALARM OFF **************")
            with dms_alarm_lock:
                dms_alarm_ring[0] = False
                dms_alarm_ring[1] = False
            turn_dms_alarm_off()
        else:
            dms_pin_arrived_event[0].set()
            dms_pin_arrived_event[1].set()

        
#za 10 tacku
@app.route('/rgb/color', methods=['PUT'])
def update_rgb_color():
    try:
        data = request.get_json()
        color = data.get('color', None)
        if color is not None:
            print(f"Received color: {color}")

            #CHAT GPT
            mqtt_message = {"color": color}
            mqtt_client.publish("topic/rgb/color", payload=json.dumps(mqtt_message))

            return jsonify({'message': 'Color updated successfully'}), 200
        else:
            return jsonify({'error': 'Color not provided'}), 400

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

#za 9 podesavanje budilnika
@app.route('/clock-alarm', methods=['POST'])
def post_clock_alarm():
    data = request.get_json()  # Get JSON data from the request body
    date = data.get('params').get('date')
    time = data.get('params').get('time')
    print("BUDILNIK" , data)

    mqtt_client.publish("topic/clock-alarm-gadget/on", json.dumps(data.get('params')))
    return jsonify({'message': f'Data received successfully. Date: {date}, Time: {time}'})

@app.route('/clock-alarm/off', methods=['PUT'])
def clock_alarm_off():
    data = request.get_json() 
    print("clock alarm off")
    mqtt_client.publish("topic/clock-alarm-gadget/off", json.dumps({"action": "off"}))
    return jsonify({'message': f'Turn clock alarm off'})

#za 2 tacku upisivanje ljudi u bazu, da se ima u svakom trenutku

def write_people(count):
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    try:
        point = (
                Point("people")
                .field("count", count)
            ) 
        
        write_api.write(bucket=bucket, org=org, record=point)
        socketio.emit("people_update", {"count": count})
    except Exception as e:
        print(str(e))
        pass

#provera uds pomeraja,2 tacka
def check_uds_distance(name, runs_on):
    print("USAO JE DA SE PROVERI UDS")
    print(name,runs_on)

    #prepraviti u najgorem slucaju
    #query = f'from(bucket: "example_db") |> range(start: -10s) |> filter(fn: (r) => r.runs_on == "{runs_on}")'
    if runs_on == "PI1":
        query = f'''
    from(bucket: "example_db")
    |> range(start: -3s)
    |> filter(fn: (r) => r["name"] == "DUS1")
    '''
    else:
         query = f'''
    from(bucket: "example_db")
    |> range(start: -3s)
    |> filter(fn: (r) => r["name"] == "DUS2")
    '''

    result = influxdb_client.query_api().query(org=org, query=query)
    records = []

    for table in result:
        for record in table.records:
            records.append((record.get_time(), record.get_value()))
    
    if len(records) < 2:
        return
    
    sorted_records = sorted(records, key=lambda record: record[0], reverse=True)
    sorted_records = sorted_records if len(sorted_records) < 3 else sorted_records[:3]

    for i in range(len(sorted_records) - 1):
        print(f"Compare: {sorted_records[i][1]} and {sorted_records[i + 1][1]}")
    entering_order = all(sorted_records[i][1] <= sorted_records[i + 1][1] for i in range(len(sorted_records) - 1))
    exiting_order = all(sorted_records[i][1] >= sorted_records[i + 1][1] for i in range(len(sorted_records) - 1))
    
    print("ENTERING ORDER", entering_order)
    print("EXITING ORDER",exiting_order)
   
    global people_count
    with people_count_lock:
        if entering_order:
            people_count += 1
            write_people(people_count)
            print(f"Someone entered the house. People count: {people_count}")
        elif exiting_order:
            if people_count == 0:
                return
            people_count -= 1
            write_people(people_count)
            print(f"Someone left the house. People count: {people_count}")

    pass

#za 4 tacku

def dms_event(indx: int):
    global dms_alarm_ring, dms_pin_arrived_event, start_countdown_event
    print(indx)
    while True:
        start_countdown_event[indx].wait()

        #ceka se 10 sekundi
        if not dms_pin_arrived_event[indx].wait(timeout=10):
            print("DMS ALARM ON ****************")
            with dms_alarm_lock:
                dms_alarm_ring[indx] = True
            raise_alarm({"name": "server"}, f"DMS PIN NIJE UNET A JE DETEKTOVAO DS{indx+1}.", True)
        else:
            print("DMS CODE ARRIVED ON TIME ****************")
            dms_pin_arrived_event[indx].clear()

        start_countdown_event[indx].clear()

def turn_dms_alarm_off():
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    try:
        point = (
                Point("alarm")
                .tag("caused_by", "dms")
                .tag("message", "Alarms turned of by dms pin input")
                .field("status", "OFF")
            ) 
        alarm_data = {
            "caused_by": "dms",
            "message": "Alarms turned of dms pin input",
            "status": "OFF"
        }

        socketio.emit('alarm', json.dumps({"status": "OFF"}))
        write_api.write(bucket=bucket, org=org, record=point)
        #mqtt_client.publish("topic/alarm/buzzer/off", json.dumps(alarm_data))
        

    except Exception as e:
        print(str(e))

def update_frontend(data):
    print("UDJE U UPDATE FRONT1")
    try:
        print("UDJE U UPDATE FRONT2")
        socketio.emit('update/' + data['runs_on'], json.dumps(data))
    except Exception as e:
        print(str(e))

def alarm_frontend(data):
    print("UDJE U SEND ALARM FRONTEND")
    try:
        print("UDJE U SEND ALARM FRONTEND")
        socketio.emit('alarm', json.dumps(data))
    except Exception as e:
        print(str(e))

#ISKLJUCIVANJE ALARMA NA DUGME
@app.route('/alarm-off', methods=['PUT'])
def alarm_off():
    global dms_alarm_ring, dms_alarm_is_active, ds_lock, time_press_ds1, time_press_ds2

    with ds_lock:
        time_press_ds1= 0
        time_press_ds2 = 0
    
    #data = request.get_json() 
    print("alarm off")
    
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    try:
        point = (
                Point("alarm")
                .tag("caused_by", "web")
                .tag("message", "Alarms turned of by web app")
                .field("status", "OFF")
            ) 
        alarm_data = {
            "caused_by": "web",
            "message": "Alarms turned of by web app",
            "status": "OFF"
        }

        write_api.write(bucket=bucket, org=org, record=point)
        mqtt_client.publish("topic/alarm/buzzer/off", json.dumps(alarm_data))

        if dms_alarm_ring:
            dms_alarm_ring[0] = False
            dms_alarm_ring[1] = False
            dms_alarm_is_active = False
            print("DMS ALARM DEACTIVATED **************")
            print("DMS ALARM OFF **************")

        return jsonify({'message': f'SUCCESS'}), 200
    
    except Exception as e:
        print(str(e))
        pass
    
    return jsonify({'message': "ERROR"}), 400

if __name__ == '__main__':

    ds_sensor = threading.Thread(target=ds_update)
    ds_sensor.daemon = True
    ds_sensor.start()

    #prijavljuje gresku ako ne stavim ,
    dms_ds1 = threading.Thread(target=dms_event, args=(0,))
    dms_ds1.daemon = True
    dms_ds1.start()
        #prijavljuje gresku ako ne stavim ,
    dms_ds2 = threading.Thread(target=dms_event, args=(1,))
    dms_ds2.daemon = True
    dms_ds2.start()

    app.run(debug=True)
