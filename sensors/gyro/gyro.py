#!/usr/bin/env python3
import MPU6050 
import time
import os

#Morao sam klasu napraviti zbog komponente
class Gyroscope(object):
    def __init__(self) :
        self.mpu = MPU6050.MPU6050()     #instantiate a MPU6050 class object
        self.accel = [0]*3               #store accelerometer data
        self.gyro = [0]*3                #store gyroscope data
        def setup(self):
            self.mpu.dmp_initialize()    #initialize MPU6050

#izmenio sam naziv i u komponenti
def run_gyro_loop(gyro, delay, callback, stop_event, publish_event, settings):
    while(True):
        accel = gyro.mpu.get_acceleration()      #get accelerometer data
        gyro_rot = gyro.mpu.get_rotation()           #get gyroscope data
        os.system('clear')
        # print("a/g:%d\t%d\t%d\t%d\t%d\t%d "%(accel[0],accel[1],accel[2],gyro[0],gyro[1],gyro[2]))
        # print("a/g:%.2f g\t%.2f g\t%.2f g\t%.2f d/s\t%.2f d/s\t%.2f d/s"%(accel[0]/16384.0,accel[1]/16384.0,
        #     accel[2]/16384.0,gyro[0]/131.0,gyro[1]/131.0,gyro[2]/131.0))

        angle = {
            "gyro_rot_x": round(gyro_rot[0] / 131.0, 2),
            "gyro_rot_y": round(gyro_rot[1] / 131.0, 2),
            "gyro_rot_z": round(gyro_rot[2] / 131.0, 2)
        }

        callback(angle, publish_event, settings)

        if stop_event.is_set():
            break

        time.sleep(delay)   