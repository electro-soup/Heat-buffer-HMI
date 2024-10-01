import network
import espnow
import time
from machine import Pin



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


led_pin = Pin(8, Pin.OUT)
# A WLAN interface must be active to send()/recv()

sta.config(channel = 1)
sta.active(True)


e = espnow.ESPNow()
e.active(True)
peer = b'\x18\x8B\x0E\x2C\x59\x28'   # MAC address of peer's wifi interface
peer2 =  b'\x18\x8B\x0E\x2D\x4E\x80' 
e.add_peer(peer)      # Must add_peer() before send()
e.add_peer(peer2)
state = 0
e.send(peer, "Starting...")
channel= 0
e_state = False
while True:
    print(e.send(peer, "test", True))
    e_state=e.send(peer2, "test", True)
    print(channel)
    
    if e_state == False:
        
         channel += 1
         if channel > 14:
            channel = 1
         sta.config(channel = channel)
    else:
        print(f'sended on channel {channel}')
        e.send(peer2, f'channel: {channel}', True)
    
         
    
    state = not state
    led_pin.value(state)
    time.sleep(1)
    