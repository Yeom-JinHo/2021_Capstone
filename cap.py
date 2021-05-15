from darkflow.net.build import TFNet
import cv2
import time
import pyautogui
import requests
import serial
import numpy
import struct

#ser = serial.Serial('/dev/ttyUSB0', 115200) # baud rate

def capturing(): #캡쳐구간 설정
    print("Current Mouse Position:",pyautogui.position()) #커서위치확인
    pyautogui.screenshot('./test.png',region=(30,180,500,300)) #region= 커서위치x,y& x,y길이

def testing():
    options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1,"gpu":1.0}
    tfnet = TFNet(options)
    imgcv = cv2.imread("./test.png")
    result = tfnet.return_predict(imgcv)
    return result
    
def sendingToServer(results):
    #datas = {"results":"animal detected!!", "location":"[경부고속도로]부지", "Time":time.strftime('%y-%m-%d %H:%M:%S'),"longitude": "35.8046466536","latitude":"129.1867718281"}
    datas = {"results":"animal detected!!", "location":"가덕영업소", "Time":time.strftime('%y-%m-%d %H:%M:%S'),"longitude": "35.1881","latitude":"126.862893"}
    url="http://ec2-3-34-151-216.ap-northeast-2.compute.amazonaws.com:3000/update"
    requests.post(url, data=datas)

def parsing(results):
    a=0
    for i in range(len(results)):
        if results[i]=={'animal'}:
            print("animal detected")
            sendingToServer(results)
            print("sending detection complete")
            a=a+1
            break
    if a==0:
        print("no animal detected")
        
def PrintLoRaInfo():
    # Request SX1276 info (device type/MAC address)
    ser.write(b'\x02\xa1\x00\x00\x03') 
    a=1
    t=bytes()
    Dt=''
    Mad=''
    while a:
        x=ser.read()
        #t.append(x)
        t=t+x
        if x==b'\x03':
            print ("Device type: "+ t[4:10].decode())
            
            a=0
         
def CheckDataSend():
    tt=bytes()
    aa=1
    while aa: # index out of range fail preven
        xx=ser.read()
        #tt.append(xx)
        tt=tt+xx
       
        #print(len(tt))
        if xx==b'\x03' and len(tt)==7:
            aa=0

    if tt[4]==1:
        print ("Data successfully sent")
        return 1
    elif tt[5]==1:
        print ("Data empty")
    elif tt[5]==2:
        print ("Data longer than 32 bytes")
    elif tt[5]==3:
        print ("Communication module busy")
    elif tt[5]==4:
        print ("Transmission failure")
    elif tt[5]==5:
        print ("Authentication failure")
    return 0

def SendSever():
    print ()
    print ('Count Number='+str(cnt))
    print ('Temperature={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature, humidity))
    datalen = len(str(temperature))+len(str(humidity))+len(str(cnt))+1
    ser.write(b'\x02\xa2\x00'+struct.pack("B",datalen)+str(temperature).encode()+b'\x20'+str(humidity).encode()+str(cnt).encode()+b'\x03')
    sent = CheckDataSend()
    
        


while True:
    print("========================start===============================")
    capturing()
    result=testing()
    print(result)
    parsing(result)
    print("=========================end================================")
    time.sleep(5)  #지연시간
