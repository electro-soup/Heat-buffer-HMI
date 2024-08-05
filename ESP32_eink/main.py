


#for quick demo version - clean.py is copied here
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
import json
import GUI 

outages = 0
temp = []

#WDT setup:

from machine import WDT
minutes = 20
watchdog = WDT(timeout = 1000 * 60 * minutes)



def test_mapping(dummy):
    print('home/kotlownia/bufor decoded')

def display_MQTT_control(command): #there is error for that, but still works
    print(command) #prototype for remote function execution 
    eval(command['execute'])
    #clear_screen()
    print("s, MQTT control works!")

#prototype function mapping for MQTT callback - to keep it clean and not growing for each added mqtt topic
dMQTT_function_mapping = {
    'home/kotlownia/bufor' : test_mapping,
    'eink_ctrl/screen_onoff':display_MQTT_control
    
}

counter = 0
global_dict_sensors = {}

# Subscription callback
def sub_cb(topic, msg, retained):
    global counter
    temp_dict = {}
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    print(topic.decode())
   
    global global_dict_sensors
    try:
        decoded_topic = topic.decode()
        decoded_message = msg.decode()
        eval_dict = json.loads(decoded_message)
    except:
        print(f'incorrect json format of incoming message from {decoded_topic}')
    
    #TODO - dictionary of topics and connected function for them
    if decoded_topic == 'home/kotlownia/bufor':
        
        #test debug output with Mono3x3
        GUI.color_writer.set_font(GUI.font3Mono)
         

        temp_msg = msg.decode()
        temp_dict = json.loads(temp_msg)
        print(temp_dict)
        global_dict_sensors = temp_dict  #copy it to the global dict (temp solution)
        GUI.framebuffer.fill('white')
       

        if counter == 0: #before GUI update - to prevent from unwanted resets because of bug in buffer_ind
             asyncio.create_task(frame_first_update())
        counter += 1
        GUI.update_sensors_dict(global_dict_sensors, GUI.buffer_sensors_dict) #probably this is not needed at all
        GUI.update_sensors_dict(global_dict_sensors, GUI.solar_sensors_dict)
        #GUI_update()
        print(counter)
    try:
        dMQTT_function_mapping[decoded_topic](eval_dict) #it completely brokes that function 
    except:
        print(f"internal error for function mapped for {eval_dict}")


async def frame_first_update():
     await asyncio.sleep(1) # wait a second
     
     GUI.eink_update(GUI.GUI_update) 


     


async def frame_clear_async():
     GUI.clear_screen()


# Demonstrate scheduler is operational.
async def heartbeat():
    s = True
    while True:
        await asyncio.sleep_ms(500)
        blue_led(s)
        s = not s

async def wifi_han(state):
    global outages
    global counter
    wifi_led(not state)
    if state:
        print('WiFi is up.')
    else:
        outages += 1
        print('WiFi is down.')
        print(f'wifi han state: {state}')
        asyncio.create_task(frame_clear_async())
        counter = 0 #reset counter, to show dipslay if mqtt is reestablished
    await asyncio.sleep(1)
    
# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe('foo_topic', 1)
    await client.subscribe('home/kotlownia/bufor', 0)
    await client.subscribe('eink_ctrl/screen_onoff', 0)


async def frame_update_async():
     while True:
          global counter

          waiting_counter = 0
          while (counter == 0):
              print(f"waiting for first mqtt frame for {waiting_counter*5}s")
              await asyncio.sleep(5)
              waiting_counter += 1

              if waiting_counter == 12: # 5*12 = 1min - in case if there is nothing sent by nymea
                  GUI.clear_framebuffers()
                  text_to_print = "brak ramek z danymi z kotłowni"
                  x_pos_of_string = (400 - (GUI.font15_testall.max_width()*len(text_to_print)))/2
                  x_pos_of_string = round(x_pos_of_string)
                  GUI.color_writer.print(text_to_print, 150, x_pos_of_string, "black")
                  GUI.frame_update()
              
              if waiting_counter == 60:
                  GUI.clear_screen()


          print("async frame update")
          previous_meas_dict = global_dict_sensors
          # TODO - check timings here and flow
          minutes_to_wait = 5
          await asyncio.sleep(60*minutes_to_wait)
          GUI.eink_display.reset() #it needs to be removed
          GUI.eink_display.init()

          GUI.show_temperature_and_load_difference(previous_meas_dict,global_dict_sensors)
        
          
          #current_time = time.localtime()
          #formatted_time = "{:02}:{:02}:{:02}".format(current_time[3], current_time[4], current_time[5])
          #framebuffer.text(formatted_time, 300, 270,'red')
          GUI.GUI_update()
          GUI.frame_update()
          

async def main(client):
    try:
        await client.connect()
        
    except OSError:
        print('Connection failed.')
        GUI.clear_framebuffers()
           
        
        #frame_update()
        asyncio.create_task(frame_clear_async())
       
    n = 0

    while True:
        await asyncio.sleep(5)
        print('publish', n)
        # If WiFi is down the following will pause for the duration.
        await client.publish('result', '{} repubs: {} outages: {}'.format(n, client.REPUB_COUNT, outages), qos = 1)
        n += 1
        watchdog.feed()
     
    
# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = False
config['will'] = ('result', 'Goodbye cruel world', False, 0 )
config['keepalive'] = 120
config['response_time'] = 90 # TODO - what is the function
#increasing response time fixed issue with disconnecting wifi !!!

#init gui update
GUI.clear_framebuffers() # TODO without it screen is red - to investigate
GUI.GUI_update()
GUI.frame_update()

# Set up client
MQTTClient.DEBUG = True  # Optional

client = MQTTClient(config)


asyncio.create_task(heartbeat())
asyncio.create_task(frame_update_async())

### main part - starting asyncio loop event

try:
    asyncio.run(main(client))

except OSError as eink_display:
        print("OSError:", eink_display)
        
        # TODO handling of those errors - when I ctr-c repl, then it goes straight to reset point
except Exception as eink_display:
        print("exception error:", eink_display)
        
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop() 
 
# TODO displaying errors on eink
# TODO sending and subscribing same topic as closed loop
# TODO if ecu is close to router, it keeps going blank (wifi is down)
        
# TODO if there is no connection over long period of time - screen should be cleared once per hour

