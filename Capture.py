from darkflow.net.build import TFNet
import cv2
import time
import pyautogui
import requests
import serial
import numpy
import struct

ser = serial.Serial('/dev/ttyUSB0', 115200)  # baud rate


def capturing():  # 캡쳐구간 설정
    print("Current Mouse Position:", pyautogui.position())  # 커서위치확인
    # region= 커서위치x,y& x,y길이
    pyautogui.screenshot('./test.png', region=(30, 50, 1000, 500))


def testing():
    options = {"model": "cfg/yolo.cfg",
               "load": "bin/yolov2.weights", "threshold": 0.1}
    tfnet = TFNet(options)
    imgcv = cv2.imread("./test.png")
    result = tfnet.return_predict(imgcv)
    return result


def parsing(results):
    personN = 0
    fireN = 0
    personC = 0.0
    fireC = 0.0
    for i in range(len(results)):
        print(i)
        print(results[i]['label'])
        if results[i]['label'] == 'person':
            print("person detected")
            personC = personC+results[i]['confidence']
            personN = personN+1
        if results[i]['label'] == 'fire':
            print("fire detected")
            fireC = fireC+results[i]['confidence']
    if fireN == 0:
        print("no fire detected")
    print("**********************************************")
    if personN != 0:
        personC = personC/personN
    if fireN != 0:
        fireC = fireC/fireN
    SendSever(personN, personC)
    print("sending detection complete")


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
        tt = tt+xx
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


def SendSever(personN, fireC):
    cnt = 0
    print()
    print('Count Number='+str(cnt))
    print('Person={0:0.0f} Fire={1:0.1f}%'.format(personN, fireC*100))
    datalen = len(str(personN))+len(str(fireC))+len(str(cnt))+1
    ser.write(b'\x02\xa2\x00'+struct.pack("B", datalen)+str(personN).encode() +
              b'\x20'+str(fireC).encode()+str(cnt).encode()+b'\x03')
    sent = CheckDataSend()
    cnt = cnt+1
    if cnt == 10:
        cnt = 0


while True:
    print("========================start===============================")
    PrintLoRaInfo()
    capturing()
    result = testing()
    print("========================result==============================")
    print(result)
    parsing(result)
    print("=========================end================================")
    time.sleep(5)  # 지연시간
