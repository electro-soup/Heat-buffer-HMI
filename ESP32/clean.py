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
uart0 = UART(2, baudrate=115200, tx=17, rx=16)
temp = bytes([0x5A, 0xA5, 0x05, 0x82, 0x20, 0x00, 0x12, 0x11, 0x11, 0x11])
uart0.write(temp)

def get_Xiaomi(msg):
    temp_msg = msg.decode()
    temp_dict = json.loads(temp_msg)
    temperature = int(temp_dict['tempc'])
    humidify = temp_dict['hum']
    return temperature, humidify

# Subscription callback
def sub_cb(topic, msg, retained):
    temp_dict = {}
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    print(topic.decode())
    dwin_command  = 0x5AA5
    init_adress = 0x2000
    
    if topic.decode() == 'home/OMG_ESP32_BLE/BTtoMQTT/A4C138F53164':
         temperature, humidify = get_Xiaomi(msg)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x3004, temperature )
         uart0.write(payload)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x3006, humidify )
         uart0.write(payload)
         
    if topic.decode() == 'home/OMG_ESP32_BLE/BTtoMQTT/A4C138D1110F':
         temperature, humidify = get_Xiaomi(msg)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x300C, temperature )
         uart0.write(payload)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x300E, humidify )
         uart0.write(payload)
    if topic.decode() == 'home/OMG_ESP32_BLE/BTtoMQTT/A4C138250A06':
         temperature, humidify = get_Xiaomi(msg)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x3000, temperature )
         uart0.write(payload)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x3002, humidify )
         uart0.write(payload)
         ...
    if topic.decode() == 'home/OMG_ESP32_BLE/BTtoMQTT/A4C138768B1F':
         temperature, humidify = get_Xiaomi(msg)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x3010, temperature )
         uart0.write(payload)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x3012, humidify )
         uart0.write(payload)
         ...
    if topic.decode() == 'home/OMG_ESP32_BLE/BTtoMQTT/A4C138425C0D':
         temperature, humidify = get_Xiaomi(msg)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x3008, temperature )
         uart0.write(payload)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x300A, humidify )
         uart0.write(payload)
         ...
    
    if topic.decode() == 'home/kotlownia/bufor':
         temp_msg = msg.decode()
         temp_dict = json.loads(temp_msg)
         print(temp_dict)
         
        
         
         print(temp_dict)
         
         test_int = int(temp_dict['temp0'])
        


         temperatures_dict = {}
         for sensors, values in sorted(temp_dict.items()):
             print(sensors, values)
             if 'temp' in sensors:
                  temperatures_dict[sensors]=int(values)
         ram_offset = 0  
         for temp_sens, values in sorted(temperatures_dict.items()):
    
             test_int = int(values)
             payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, init_adress+ram_offset, test_int)
             uart0.write(payload)
             print(", ".join(hex(b) for b in payload))
             ram_offset+=2
        # some labels coloring - duplicated code for fast purpose
         ram_offset = 0
         lower_temp_limit = 30
         #for extrapolating
         temperature_list =[]
        
         ####doo some extrapolation
         
         temp_msg = msg.decode()
         temp_dict = json.loads(temp_msg)
         for key, value in sorted(temp_dict.items()):
              if 'temp' in key:
                  temperature_list.append(value)
                  
         print(temperature_list)
         extrapolated_list = []
         num_of_intervals_between = 9

         num_of_intervals_between+=1 #to get indeed such interval
         for i in range(0, len(temperature_list)-1):
    
            extrapolated_list.append(temperature_list[i]) #append first element from 
            #calculate some values 
            a = temperature_list[i+1]-temperature_list[i]
            b = temperature_list[i]

            for y in range(1,num_of_intervals_between): #1 - to omit calculating existing point x1, - 1 - x2 
                temporary_point = a*(y/num_of_intervals_between)+b
                extrapolated_list.append(int(temporary_point))
            #extrapolated_list.append(0)
         if i == (len(temperature_list)-2):
            extrapolated_list.append(temperature_list[i+1])
         
         lower_temp_limit = 20
         #master loop to show this on LCD
         master_init_adress = 0x4000
         ram_offset = 0
         for temperature in extrapolated_list:
               payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, master_init_adress+ram_offset, int(temperature - lower_temp_limit))
               uart0.write(payload)
               ram_offset+=2
               
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x2138, int(temp_dict['power']))
         uart0.write(payload)
         payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, 0x2140, int(temp_dict['load_percent']))
         uart0.write(payload)
                               
         #print(extrapolated_list)
         #print(len(extrapolated_list))

        

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
    await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138F53164', 0)
    await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138D1110F', 0)
    await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138425C0D', 0)
    await client.subscribe('home/OMG_ESP32_BLE/BTtoMQTT/A4C138250A06', 0)
    
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
