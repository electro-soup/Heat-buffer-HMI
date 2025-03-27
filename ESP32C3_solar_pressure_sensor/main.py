from machine import ADC, Pin, WDT
import time
import machine
import espnow
import network
import json
import ubinascii
#machine.freq(80 * 1000000)
#configure ADC


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


adc = ADC(Pin(0), atten = ADC.ATTN_11DB)

watchdog = WDT(timeout=1000 * 60 * 5) 
watchdog.feed()

sta.active(True)
sta.config(channel = 6)
sta.config(reconnects=20)



value_dict = { 'sensor_voltage_mV': 0, 'pressure_bar' : 0
    }

mac_peer = "40:4C:CA:F5:A5:68"
mac_peer_test = "18:8B:0E:84:3F:C0"

e = espnow.ESPNow()
e.active(True)


peer = ubinascii.unhexlify(mac_peer.replace(':',''))

peer_test =ubinascii.unhexlify(mac_peer_test.replace(':',''))
e.add_peer(peer)
e.add_peer(peer_test)



e.send(peer,"starting...")
e.send(peer_test,"starting...")

def auto_wifi_channel():
    
    sta.config(channel = 1)
    state = False
    #scan through channel at init:
    for ch_no in range(1, 15):
        sta.config(channel = ch_no)
        if e.send(peer,"wifi test") == True:
            state = True
            break
    
    if state == True:
        print(f"channel set {sta.config('channel')}")
    else:
        print("no channel configured - peer is disconnected")
            
    
auto_wifi_channel()

while True:
        watchdog.feed()
        calculated_pressure = 0
        mVolt_avg = 0
        #every minute
        print("started measurement")
        for i in range(60):
            mVolt_avg += adc.read_uv()/60
            time.sleep(1)
        value_dict['pressure_bar'] = 2.095 * mVolt_avg/1000000 - 0.6318
        value_dict['sensor_voltage_mV'] = mVolt_avg/1000
        print(f'u16: {adc.read_u16()}')
        print(f'uv: {value_dict['sensor_voltage_mV']} mV')
        print(f'cisnienie (bar): {value_dict['pressure_bar']}')
        
        #e.send(peer,json.dumps(value_dict))
        state =  e.send(peer, json.dumps(value_dict))
        
        if state == False:
            print("message not sent")
            auto_wifi_channel()
            print(f'channel: {sta.config('channel')}')
        else:
            print("message sent")
         



