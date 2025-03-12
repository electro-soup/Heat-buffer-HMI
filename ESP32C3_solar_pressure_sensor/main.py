from machine import ADC, Pin, WDT
import time
import machine

#machine.freq(80 * 1000000)
#configure ADC
adc = ADC(Pin(0), atten = ADC.ATTN_11DB)

watchdog = WDT(timeout=1000 * 60 * 5) 
watchdog.feed()

from mqtt_as import MQTTClient
from mqtt_local import wifi_led, blue_led, config
import uasyncio as asyncio
import json

value_dict = { 'sensor_voltage_mV': 0, 'pressure_bar' : 0
    }

outages = 0
async def heartbeat():
    s = True
    while True:
        await asyncio.sleep_ms(500)
        blue_led(s)
        s = not s

def sub_cb(topic, msg, retained):
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    
async def wifi_han(state):
    global outages 
    wifi_led(not state)
    if state:
        print('WiFi is up.')
    else:
        outages += 1
        print('WiFi is down.')
    await asyncio.sleep(1)

async def main(client):
    try:
        await client.connect()
    except OSError as e:
        print(f'{e}')
        print('Connection failed.')
        machine.reset()
        return
    
    n = 0
    while True:
        watchdog.feed()
        calculated_pressure = 0
        mVolt_avg = 0
        #every minute
        for i in range(60):
            mVolt_avg += adc.read_uv()/60
            await asyncio.sleep_ms(1000)
        value_dict['pressure_bar'] = 2.095 * mVolt_avg/1000000 - 0.6318
        value_dict['sensor_voltage_mV'] = mVolt_avg/1000
        print(f'u16: {adc.read_u16()}')
        print(f'uv: {value_dict['sensor_voltage_mV']} mV')
        print(f'cisnienie (bar): {value_dict['pressure_bar']}')
        await client.publish('home/kotlownia/CO/pressure_sensor', json.dumps(value_dict), qos = 0)
        

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['clean'] = False
config['will'] = ('result', 'Goodbye cruel world!', False, 0)
config['keepalive'] = 120
config['response_time'] = 90

asyncio.create_task(heartbeat())
# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

try:
    asyncio.run(main(client))

finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    asyncio.new_event_loop()

