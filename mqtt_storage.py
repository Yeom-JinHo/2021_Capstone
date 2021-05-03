import paho.mqtt.client as mqtt
import datetime
import os
import signal
import argparse
import configure_storage

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

  def on_message(self, client, userdata, msg):
    print ("Topic: " + msg.topic + '\nMessage: ' + str(msg.payload))
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

if __name__ == '__main__':
#  parser = argparse.ArgumentParser()
#  parser.addargument("--log", help="log filename", default=None)
#  args = parser.parse_args()
  storage = MqttStorage()
  storage.main()

