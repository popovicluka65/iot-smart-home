#!/usr/bin/env python3

from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD

from time import sleep, strftime
from datetime import datetime
from queue import Empty

# def get_cpu_temp():     # get CPU temperature and store it into file "/sys/class/thermal/thermal_zone0/temp"
#     tmp = open('/sys/class/thermal/thermal_zone0/temp')
#     cpu = tmp.read()
#     tmp.close()
#     return '{:.2f}'.format( float(cpu)/1000 ) + ' C'
 
# def get_time_now():     # get system time
#     return datetime.now().strftime('    %H:%M:%S')
    
# def loop():
#     mcp.output(3,1)     # turn on LCD backlight
#     lcd.begin(16,2)     # set number of LCD lines and columns
#     while(True):         
#         #lcd.clear()
#         lcd.setCursor(0,0)  # set cursor position
#         lcd.message( 'CPU: ' + get_cpu_temp()+'\n' )# display CPU temperature
#         lcd.message( get_time_now() )   # display the time
#         sleep(1)
        
# def destroy():
#     lcd.clear()
    
# PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
# PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# # Create PCF8574 GPIO adapter.
# try:
# 	mcp = PCF8574_GPIO(PCF8574_address)
# except:
# 	try:
# 		mcp = PCF8574_GPIO(PCF8574A_address)
# 	except:
# 		print ('I2C Address Error !')
# 		exit(1)
# # Create LCD, passing in MCP GPIO adapter.
# lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

#GPT
class LCD:
    def __init__(self, **kwargs):
        self.PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
        self.PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.

        try:
            self.mcp = PCF8574_GPIO(self.PCF8574_address)
        except:
            try:
                self.mcp = PCF8574_GPIO(self.PCF8574A_address)
            except:
                print('I2C Address Error!')
                exit(1)

        pin_rs = kwargs.get('pin_rs')
        pin_e = kwargs.get('pin_e')
        pins_db = kwargs.get('pins_db')

        print("PIN RS", pin_rs)
        print("PIN E", pin_e)
        print("PINS DB", pins_db)
        #self.lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=self.mcp)
        self.lcd = Adafruit_CharLCD(pin_rs=pin_rs, pin_e=pin_e, pins_db=pins_db, GPIO=self.mcp)

    @staticmethod
    def get_cpu_temp():
        """Get CPU temperature from the system."""
        with open('/sys/class/thermal/thermal_zone0/temp') as temp_file:
            cpu_temp = temp_file.read()
        return '{:.2f} C'.format(float(cpu_temp) / 1000)

    @staticmethod
    def get_time_now():
        """Get the current system time."""
        return datetime.now().strftime('%H:%M:%S')

    def show_text(self, temperature, humidity):
        """Display temperature and humidity on the LCD."""
        self.mcp.output(3, 1)  # Turn on LCD backlight
        self.lcd.begin(16, 2)  # Set number of LCD lines and columns

        self.lcd.setCursor(0, 0)  # Set cursor position
        self.lcd.message('TEMP: {:.2f}\n'.format(temperature))
        self.lcd.message('HUM: {:.2f}'.format(humidity))

    def destroy(self):
        """Clear the LCD display."""
        self.lcd.clear()


def run_lcd_loop(lcd, delay, callback, stop_event, settings, display_values_event, data_queue):
    """Run the LCD update loop."""
    while not stop_event.is_set():
        try:
            display_values_event.wait()  # Wait for signal to display new values
            temperature, humidity = data_queue.get(timeout=1)  # Get values from queue
            lcd.show_text(temperature, humidity)  # Display values on LCD
            display_values_event.clear()  # Clear the event
            #callback(temperature, humidity, settings)  # Execute callback with current values
            callback(settings, humidity, temperature) 
            
        except Empty:
            pass

        sleep(delay)  # Delay between updates

    lcd.destroy()  # Clean up LCD when loop stops