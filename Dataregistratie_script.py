import serial
import time
import datetime
import json
import redis
import requests
import math

# defining the api-endpoint
baseUrl = 'https://qioskdotnetapi.azurewebsites.net/api/'

#kioskenlijst voorbereiding
response= requests.get(baseUrl+"kiosks")
kioksList=response.json()
kiosks=[]
for k in kioksList:
    k_coor=[]
    k_coor.append(int(k['coordinate'][0]))
    k_coor.append(int(k['coordinate'][2]))
    k_coor.append(int(k['coordinate'][4]))
    k_coor.append(int(k['kioskID']))
    kiosks.append(k_coor)

#variables
posx = 0
posy = 0
wasInKiosk =[ False, 0 ]
inKiosk = [False, 0 ]
begin = " "
end = " "
prevKiosk = 0

def location():
  counter = 0
  r = redis.Redis(host='localhost', port=6379, db=0)
  DWM = serial.Serial(port="/dev/ttyACM0", baudrate=115200)
  print("Connected to " + DWM.name)
  DWM.write("\r\r".encode())
  print("Encode")
  time.sleep(1)
  DWM.write("lec\r".encode())
  print("Encode")
  time.sleep(1)
  try:
        while counter < 10:
          counter = counter + 1
          data = DWM.readline()
          if(data):
            print(data)
            if (b"DIST" in data and b"AN0" in data and b"AN1" in data and b"AN2" in data):
              data = data.replace(b"\r\n",b"")
              data = data.decode().split(",")
        DWM.write("\r".encode())
        DWM.close()
        return data
  except KeyboardInterrupt:
    print("Stopped by keyboard")
    return data

def inCircle(kiosks,x,y):
    toReturn=[False,0]
    for k in kiosks:
        dist = math.sqrt((k[0] - x) ** 2 + (k[1] - y) ** 2)
        print("x1="+str(k[0])+",,,,y1"+str(k[1]))
        print(x,y)
        print('dis=====',dist)
        print(k[2])
        if dist <= k[2]:
            print("kiosk "+str(k[3])+" mid point:", k[0],k[1])
            print("radius:", k[2])
            return [True,k[3]] 
        else:
            toReturn = [False,0]
    return toReturn

if __name__ == '__main__':


  try:
        while True:

          dataArr  = location()
          if(dataArr[-5]=="POS"):
              posx = float(dataArr[-4])    
              posy = float(dataArr[-3])   
          else:
              posx = -10    
              posy = -10
          print(posx, posy)
          inKiosk = inCircle(kiosks,posx,posy)
          print("==================================================")
          print(inKiosk)
          print("==================================================")
          if (inKiosk[0] == True) and ((wasInKiosk[0] == False)or wasInKiosk[1]!=inKiosk[1]):
              begin = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
              prevKiosk = inKiosk[1]
              wasInKiosk = [True,inKiosk[1]]
          elif (inKiosk[0] == False) and (wasInKiosk[0] == True):
              end = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
              a = requests.post(baseUrl+"userkiosks", json={"userID": 3, "kioskID": prevKiosk, "begin": begin,"end": end})
              print(a.text)
              wasInKiosk = [False,0]
  except KeyboardInterrupt:
    print("Stop")
