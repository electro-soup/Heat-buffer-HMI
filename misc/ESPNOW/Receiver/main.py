import network
import espnow
from machine import Pin
import time


def wifi_reset():   # Reset wifi to AP_IF off, STA_IF on and disconnected
  sta = network.WLAN(network.STA_IF); sta.active(False)
  ap = network.WLAN(network.AP_IF); ap.active(False)
  sta.active(True)
  while not sta.active():
      time.sleep(0.1)
  sta.disconnect()   # For ESP8266
  while sta.isconnected():
      time.sleep(0.1)
  return sta, ap

sta, ap = wifi_reset()


led = Pin(8, Pin.OUT)
# A WLAN interface must be active to send()/recv()

sta.config(channel = 9)
sta.config(pm=sta.PM_NONE)
print(sta.config("channel"))
sta.active(True)

print(sta.config("channel"))
sta.config(reconnects =0)

e = espnow.ESPNow()
e.active(True)
state = 0
channel = 0
print(sta.config('mac').hex())
while True:
    print(sta.config("channel"))
    
    host, msg = e.recv(10000)
    if msg:             # msg == None if timeout in recv()
        print(host, msg)
        state = not state
        led.value(state)
    else:
        print("no message")
        channel += 1
        if channel > 14:
            channel = 1
        sta.config(channel = channel)
        
        
        
        