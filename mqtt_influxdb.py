import paho.mqtt.client as mqtt
import datetime
import os
import signal
import argparse
import configure_storage
from influxdb import InfluxDBClient
from typing import NamedTuple
INFLUXDB_ADDRESS = '192.168.0.129'
INFLUXDB_USER = 'exP01'
INFLUXDB_PASSWORD = 'password'
INFLUXDB_DATABASE = 'ex01'
MAC_ADDRESS = ["kyungbaekkim@jnu.ac.kr/3534353157376704",
               "kyungbaekkim@jnu.ac.kr/353435315A376904",
               "kyungbaekkim@jnu.ac.kr/3534353173375F02"]
REAL_ADDRESS = ["1-1","1-2","1-3"]
#MQTT_ADDRESS = '192.168.0.8'
#MQTT_USER = 'exP01'
#MQTT_PASSWORD = 'password'
#MQTT_TOPIC = 'home/+/+'
#MQTT_REGEX = 'home/([^/]+)/([^/]+)'
#MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
class SensorData(NamedTuple):
    location : str
    measurement : str
    value : float

class MqttStorage:
  def __init__(self):
    self.client = mqtt.Client(configure_storage.client_id)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.on_log = self.on_log
    self.client.username_pw_set(configure_storage.user_id, configure_storage.user_pw)
    self.client.connect(configure_storage.host, 1883, 60)
    
    self.__stop = False
    signal.signal(signal.SIGINT, self.stop)
    signal.signal(signal.SIGTERM, self.stop)

  def main(self):
#    self.client.loop_start()
    self.client.loop_forever()

  def stop(self, signum, frame):
    self.__stop = True
    print ("I'll be back")
    self.client.loop_stop()

  def on_connect(self, client, userdata, flags, rc):
    print ("Connected with result code " + str(rc))
    client.subscribe(configure_storage.topic)
  def _send_sensor_data_to_influxdb(self, sensor_data):
    json_body = [
        {
            'measurement': sensor_data.measurement,
            'tags': {
                'location': sensor_data.location
            },
            'fields': {
                'value': sensor_data.value
            }
        }
    ]
    influxdb_client.write_points(json_body)

  def tranTopic(self,topic):
      index=MAC_ADDRESS.index(topic)
      return index
    
  def on_message(self, client, userdata, msg):
    print ("Topic: " + msg.topic + '\nMessage: ' + str(msg.payload))
    sensor_data = str(msg.payload)
    tmp_sensor=sensor_data[2:6]
    hum_sensor=sensor_data[7:11]
    index =self.tranTopic(msg.topic)
    tran_topic=REAL_ADDRESS[index]
    tmp_data = SensorData(tran_topic,'tmp',float(tmp_sensor))
    hum_data = SensorData(tran_topic,'hum',float(hum_sensor))
    if hum_data is not None:
      self._send_sensor_data_to_influxdb(hum_data)
    if tmp_data is not None:
      self._send_sensor_data_to_influxdb(tmp_data)  
    self.store(configure_storage.storage_path + msg.topic, msg.payload) 
  

  def on_log(self, client, userdata, level, buf):
    print("log: ",buf)

  def store(self, path, data):
    #path = path.replace('@', '').replace('.', '')
    if not os.path.exists(path):
      os.makedirs(path)
    dt = datetime.datetime.now()
    filename = dt.strftime("%Y%m%d")
#   with open(path+filename, 'ab') as f:
#     f.write(data)
    with open(path+'/'+filename, 'at') as f:
      f.write(dt.strftime("%Y%m%d-%H:%M:%S " + str(data) + '\n'))
def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)
if __name__ == '__main__':
#  parser = argparse.ArgumentParser()
#  parser.addargument("--log", help="log filename", default=None)
#  args = parser.parse_args()
  _init_influxdb_database()
  storage = MqttStorage()
  storage.main()
