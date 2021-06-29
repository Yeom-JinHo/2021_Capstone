import Adafruit_DHT
import time
import datetime
import serial
import numpy
import struct

sensor = Adafruit_DHT.DHT11  # DHT11
pin = '4'  # GPIO number
ser = serial.Serial('/dev/ttyUSB0', 115200)  # baud rate


def PrintLoRaInfo():
    # Request SX1276 info (device type/MAC address)
    ser.write(b'\x02\xa1\x00\x00\x03')
    a = 1
    t = bytes()
    Dt = ''
    Mad = ''
    while a:
        x = ser.read()
        # t.append(x)
        t = t+x
        if x == b'\x03':
            print("Device type: " + t[4:10].decode())

            a = 0


def CheckDataSend():
    tt = bytes()
    aa = 1
    while aa:  # index out of range fail preven
        xx = ser.read()
        # tt.append(xx)
        tt = tt+xx

        # print(len(tt))
        if xx == b'\x03' and len(tt) == 7:
            aa = 0

    if tt[4] == 1:
        print("Data successfully sent")
        return 1
    elif tt[5] == 1:
        print("Data empty")
    elif tt[5] == 2:
        print("Data longer than 32 bytes")
    elif tt[5] == 3:
        print("Communication module busy")
    elif tt[5] == 4:
        print("Transmission failure")
    elif tt[5] == 5:
        print("Authentication failure")
    return 0


# Print device type and MAC address
PrintLoRaInfo()
# \x02\xa2\x00 : LoRa data transmission request
# + data length in byte + byte
# \x03 : End
cnt = 0
while 1:
    time.sleep(1)  # seconds
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print()
        print('Count Number='+str(cnt))
        print(
            'Temperature={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature, humidity))
        datalen = len(str(temperature))+len(str(humidity))+len(str(cnt))+1
        ser.write(b'\x02\xa2\x00'+struct.pack("B", datalen)+str(temperature).encode() +
                  b'\x20'+str(humidity).encode()+str(cnt).encode()+b'\x03')
        cnt += 1
        if(cnt == 10):
            cnt = 0
        # Print transmission log

        sent = CheckDataSend()
        f = open("test2.txt", "a")
        f.write(time.strftime('%c', time.localtime(time.time())))
        f.write(' Temperature {0:0.1f} Humidity {1:0.1f} '.format(
            temperature, humidity))
        f.close()
    else:
        print('Failed to get reading. Try again!')
