import requests
import json
import FaBo9Axis_MPU9250
import time
import sys
import timeit
import blescan
import bluetooth._bluetooth as bluez
import threading
import RPi.GPIO as GPIO
sys.path.append('/home/pi/mpu/cosmic/Sensors/MPU 9250')
from mfrc522 import SimpleMFRC522

dev_id = 0

############################
id_value = str(0)
reader = SimpleMFRC522()

def RFID_work():
    global id_value
    while(1):
        print('Hold a tag near the reader')
        count_exit = int(0)
        try:
             id, text = reader.read()
             print('id is : ', id)
             id_value = id
             if(id == 0):
                 if(count_exit == 10):
                     print('count + 1 ')
                 else:
                     count_exit = count_exit + 1
                     print('id is not 0')
                     
        finally:
            GPIO.cleanup()


####################################################
def main():
    global id_value
    th = threading.Thread(target=RFID_work, name="[Daemon]", args=())
    th.setDaemon(True)
    th.start()

    try:
        sock = bluez.hci_open_dev(dev_id)
        print "ble thread started"
    except:
        print "error accessing bluetooth device..."
        sys.exit(1)
    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)

    mpu9250 = FaBo9Axis_MPU9250.MPU9250()

    #url = 'http://10.5.15.83:80'
    url = 'http://192.168.43.182:80'
    headers = {'Content-type': 'application/json', 'Accept':'text-plain'}
    cnt = int()
    sum_ax = int()
    sum_ay = int()
    sum_az = int()
    sum_gx = int()
    sum_gy = int()
    sum_gz = int()
    sum_mx = int()
    sum_my = int()
    sum_mz = int()
    max_ax = int(0)
    max_ay = int(0)
    max_az = int(0)
    max_gx = int(0)
    max_gy = int(0)
    max_gz = int(0)
    check_cnt = int(0)
    txPower = int()
    rssi = float()
    beacon_dist = float(0)

    def calculateDistance(txPower, rssi):
        if(rssi == 0):
            return -1.0
        
        ratio = float(rssi*1.0/txPower)
        if(ratio < 1.0):
            print('ratio < 1.0 case ', pow(ratio, 10))
            return pow(ratio, 10)
        else:
            accuracy = float((0.89976)*pow(ratio, 7.7095) + 0.111)
            #print('ratio > 1.0 case ', accuracy)
            return accuracy
        #distance = pow(10, (txPower-rssi)/(20))
        #print('distance : ', distance)
        #return distance

    try:

        while cnt < 100:
           
            # read 9-axis sensor value #

            accel = mpu9250.readAccel()

            #print (" ax = " ,  accel['x'] )
            #print (" ay = " , ( accel['y'] ))
            #print (" az = " , ( accel['z'] ))
            
            if(accel['x'] > max_ax):
                max_ax = accel['x']
            if(accel['y'] > max_ay):
                max_ay = accel['y']
            if(accel['z'] > max_az):
                max_az = accel['z']
            sum_ax += accel['x']
            sum_ay += accel['y']
            sum_az += accel['z']

            gyro = mpu9250.readGyro()

            #print (" gx = " , ( gyro['x'] ))
            #print (" gy = " , ( gyro['y'] ))
            #print (" gz = " , ( gyro['z'] ))

            if(gyro['x'] > max_gx):
                max_gx = gyro['x']
            if(gyro['y'] > max_gy):
                max_gy = gyro['y']
            if(gyro['z'] > max_gz):
                max_gz = gyro['z']

            sum_gx += gyro['x']
            sum_gy += gyro['y']
            sum_gz += gyro['z']

            mag = mpu9250.readMagnet()

            #print (' mx = ' , mag['x'])
            #print (' my = ' , mag['y'])
            #print (' mz = ' , mag['z'])
            
            sum_mx += mag['x']
            sum_my += mag['y']
            sum_mz += mag['z']

            start_1 = timeit.timeit()


            ##########################################################################
            # reading blescan value, calculate #
            
            returnedList = blescan.parse_events(sock, 30)
            #print "---------------"
            myname = threading.currentThread().getName()
            active_cnt = threading.activeCount()
            #print('active thread is : ', active_cnt)
            #print('myname thread is : ', myname)
            #print('returnedList is : ', returnedList)
            #print('enumerate is :' , threading.enumerate())
            for beacon in returnedList:
                check_cnt = check_cnt + 1
                #print('chk cnt is : ' , check_cnt)
                ret_List = beacon.split(',')
                
                #print(ret_List[1])
                if(ret_List[1] == 'e2c56db5dffb48d2b060d0f5a71096e0'):
                    print('beacon is done!')
                    #print(ret_List[1] , "RSSI : ", ret_List[5], "TXp : " , ret_List[4])
                    #print('===========================================')
                    print('')
                    rssi = float(ret_List[5])
                    txPower = int(ret_List[4])

                    beacon_dist = calculateDistance(txPower, rssi)
                    beacon_dist = round(beacon_dist, 4)
                    #print('type is' , type(rssi), type(txPower))
                    print('distance from beacon is : ', beacon_dist)
                    data = {'ax': accel['x'], 'ay': accel['y'], 'az': accel['z'],
                    'gx': gyro['x'], 'gy': gyro['y'], 'gz': gyro['z'],
                    'dist': beacon_dist, 'id' : id_value}
                    end_1 = timeit.timeit()
                    #print('data generate time is : ', end_1 - start_1);
                    print('data is : ', data)
                    start_2 = timeit.timeit()
                    #if(data['id'] != 0):
                    print('id value is : ', id_value)
                    r = requests.post(url, data=json.dumps(data), headers=headers)
                    id = 0
                    id_value = 0
                    time.sleep(1)
                    print('=====================================================')
                    break

                else:
                    beacon_dist = 0
                    #print('beacon_dist is[2] : ', beacon_dist)
                    
            
            #data = {'ax': accel['x'], 'ay': accel['y'], 'az': accel['z'],
            #        'gx': gyro['x'], 'gy': gyro['y'], 'gz': gyro['z'],
            #        'dist': beacon_dist}
            #end_1 = timeit.timeit()
            #print('data generate time is : ', end_1 - start_1);
            #print('data is : ', data)
            
            #start_2 = timeit.timeit()
            #r = requests.post(url, data=json.dumps(data), headers=headers)
            #end_2 = timeit.timeit()
            #print('requests time is ' , end_2 - start_2)
            
            #print('data, posing is done!')
            #time.sleep(1)
            #cnt = cnt+1

            #avg_ax = sum_ax / 10
            #avg_ay = sum_ay / 10
            #avg_az = sum_az / 10
            #avg_gx = sum_gx / 10
            #avg_gy = sum_gy / 10
            #avg_gz = sum_gz / 10
            #avg_mx = sum_mx / 10
            #avg_my = sum_my / 10
            #avg_mz = sum_mz / 10

            #print('avg ax, ay, az : ', avg_ax, avg_ay, avg_az)
            #print('avg gx, gy, gz : ', avg_gx, avg_gy, avg_gz)
            #print('avg mx, my, mz : ', avg_mx, avg_my, avg_mz)
            #print('#########################')
            #print('max ax, ay, az is : ', max_ax, max_ay, max_az)
            #print('max gx, gy, gz is : ', max_gx, max_gy, max_gz)
            #print('########################')
    except KeyboardInterrupt:
        sys.exit()
if __name__ == "__main__":
    main()
