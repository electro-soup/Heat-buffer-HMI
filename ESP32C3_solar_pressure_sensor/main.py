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

mac_peer_master = "40:4C:CA:F5:A5:68"
mac_peer_test = "18:8B:0E:84:3F:C0"

e = espnow.ESPNow()
e.active(True)


peer_master = ubinascii.unhexlify(mac_peer_master.replace(':',''))

peer_test =ubinascii.unhexlify(mac_peer_test.replace(':',''))
e.add_peer(peer_master)
e.add_peer(peer_test)



e.send(peer_master,"starting...")
e.send(peer_test,"starting...")

def auto_wifi_channel():
    
    sta.config(channel = 1)
    state = False
    #scan through channel at init:
    #scan through all channel - because it sets to 5 or 7 if main channel is 6
    
    wifi_stats = {}
    best_channel = -1
    for key in range(-4,20): #lazy way for latter best channel seek (cho 1 and 14)
        wifi_stats[key]=0
    
    print("starting wifi channel scanning")
    
    for ch_no in range(1, 15):
        sta.config(channel = ch_no)
        
        for i in range(0,50):
            if e.send(peer_master,f"wifi_{ch_no}") == True:
                wifi_stats[ch_no] += 1 
                
    #best_channel = max(wifi_stats, key = lambda key: wifi_stats[key])
    #search for 3 adjacent channels
    
    for i in range(1,15):
        
        if wifi_stats[i-1]>0 and wifi_stats[i]>0 and wifi_stats[i+1]>0:
            best_channel = i
            break
    print(wifi_stats)
    
    
    
    if best_channel > 0:
        sta.config(channel = best_channel)
        print(f"channel set {sta.config('channel')}")
    else:
        print("no channel configured - peer is disconnected")
        wifi_reset()
        
    
    
            
    
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
        for send_attempts in range(0, 10):
            state =  e.send(peer_master, json.dumps(value_dict))
            if state == True:
                print(f"resend attempts: {send_attempts}")
                break
        
        if state == False:
            print("message not sent")
            auto_wifi_channel()
            print(f'channel: {sta.config('channel')}')
        else:
            print("message sent")
         



