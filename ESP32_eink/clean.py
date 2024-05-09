# clean.py Test of asynchronous mqtt client with clean session.
# (C) Copyright Peter Hinch 2017-2019.
# Released under the MIT licence.

# Public brokers https://github.com/mqtt/mqtt.github.io/wiki/public_brokers

# The use of clean_session means that after a connection failure subscriptions
# must be renewed (MQTT spec 3.1.2.4). This is done by the connect handler.
# Note that publications issued during the outage will be missed. If this is
# an issue see unclean.py.

# red LED: ON == WiFi fail
# blue LED heartbeat: demonstrates scheduler is running.

from mqtt_as import MQTTClient
from mqtt_local import wifi_led, blue_led, config
import uasyncio as asyncio
from machine import UART
import json
import struct

outages = 0
temp = []


# Subscription callback
def sub_cb(topic, msg, retained):
    temp_dict = {}
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    print(topic.decode())
   
    
   
    if topic.decode() == 'home/kotlownia/bufor':
         temp_msg = msg.decode()
         temp_dict = json.loads(temp_msg)
         print(temp_dict)
 
         test_int = int(temp_dict['temp0'])

         temperatures_dict = {}
         for sensors, values in sorted(temp_dict.items()):
             print(sensors, values)
             if 'temp' in sensors:
                  temperatures_dict[sensors]=int(values)
     
         #for temp_sens, values in sorted(temperatures_dict.items()):
    
             
# Demonstrate scheduler is operational.
async def heartbeat():
    s = True
    while True:
        await asyncio.sleep_ms(500)
        blue_led(s)
        s = not s

async def wifi_han(state):
    global outages
    wifi_led(not state)
    if state:
        print('WiFi is up.')
    else:
        outages += 1
        print('WiFi is down.')
    await asyncio.sleep(1)
    
# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe('foo_topic', 1)

async def main(client):
    try:
        await client.connect()
        
    except OSError:
        print('Connection failed.')
        #await client._keep_connected()
        return
    n = 0
    await client.subscribe('home/kotlownia/bufor', 0)
    #await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138F53164', 0)
    #await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138D1110F', 0)
    #await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138425C0D', 0)
    #await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138250A06', 0)
    
    while True:
        await asyncio.sleep(5)
        print('publish', n)
        # If WiFi is down the following will pause for the duration.
        await client.publish('result', '{} repubs: {} outages: {}'.format(n, client.REPUB_COUNT, outages), qos = 1)
        n += 1
        await client.wait_msg()
        await client._keep_connected()
        

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
#config['connect_coro'] = conn_han
config['clean'] = False
config['will'] = ('result', 'Goodbye cruel world', False, 0 )
config['keepalive'] = 120

# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

asyncio.create_task(heartbeat())
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop()
