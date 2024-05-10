"""
	Example for 4.2 inch black & white Waveshare E-ink screen
	Run on ESP32
"""

import epaper4in2
from machine import Pin, SPI

# SPIV on ESP32
#VCC - GREY
#GND - BROWN
sck = Pin(13) 		#CLK YELLOW
miso = Pin(19)		#?? whatever, connected to anything
mosi = Pin(14)		#DIN BLUE
dc = Pin(27)		#GREEN
cs = Pin(15)		#ORANGE
rst = Pin(26)		#WHITE
busy = Pin(25)		#VIOLET
spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)

e = epaper4in2.EPD(spi, cs, dc, rst, busy)
e.init()

w = 400
h = 300
x = 0
y = 0

# --------------------

# use a frame buffer
# 400 * 300 / 8 = 15000 - thats a lot of pixels
import framebuf
buf_black = bytearray(w * h // 8)
buf_red = bytearray(w * h // 8)

#creating two buffers, one for black, second for red pixels
fb_black = framebuf.FrameBuffer(buf_black, w, h, framebuf.MONO_HLSB)
fb_red = framebuf.FrameBuffer(buf_red, w, h, framebuf.MONO_HLSB)
black = 0
white = 1
red = 0

def clear_screen():
	fb_red.fill(white)
	fb_black.fill(white)
	e.display_frame(buf_black, buf_red)

#clear_screen()

black = 0
white = 1

# display as much as this as fits in the box
str = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam vel neque in elit tristique vulputate at et dui. Maecenas nec felis lectus. Pellentesque sit amet facilisis dui. Maecenas ac arcu euismod, tempor massa quis, ultricies est.'

# this could be useful as a new method in FrameBuffer
def text_wrap(str,x,y,color,w,h,border=None):
	# optional box border
	if border is not None:
		fb_black.rect(x, y, w, h, border)
	cols = w // 8
	# for each row
	j = 0
	for i in range(0, len(str), cols):
		# draw as many chars fit on the line
		fb_black.text(str[i:i+cols], x, y + j, color)
		j += 8
		# dont overflow text outside the box
		if j >= h:
			break

# draw text box 3
bx = 0
by = 184
bw = w//2 # 64 = 8 cols
bh = 8 * 8 # 64 = 8 rows (64 chars in total)
#text_wrap(str,bx,by,black,bw,bh,None)


from ThreeColorFrameBuffer import ThreeColorFrameBuffer

framebuffer = ThreeColorFrameBuffer(400, 300, fb_black, fb_red)

#frame_buffer_eink.rect(0,0, 200, 150, "red")



def frame_update():
    e.display_frame(buf_black,buf_red)
     
clear_screen()


#how to handle arrays 
#import array
#myData = array.array('I', [10,10,120,30,30,61])


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
        
        temperatures_dict = {}
        
        for sensors, values in sorted(temp_dict.items()):
            print(sensors, values)
            if 'temp' in sensors:
                temperatures_dict[sensors]=int(values)

        framebuffer.fill('white')          
        i = 0
        lower_tempC = 30
        x, y = 20, 20
        for temp_sens, values in sorted(temperatures_dict.items()):
            if i%20 == 0:
                framebuffer.text(f'{temp_sens}: {values}C', x, y + i, 'black')
                framebuffer.rect(x + 100, y + i, 60, 25, 'black', False)
                framebuffer.rect(x + 101,y+i+1,values - lower_tempC,23,'red', True )
            else:
                framebuffer.text(f'{temp_sens}: {values}C', x, y + i, 'red')
                framebuffer.rect(x + 100, y + i, 60, 25, 'black', False)
                framebuffer.rect(x + 101,y+i+1,values - lower_tempC,23,'red', True )
            i = i + 30
        # percent load bar
        percent_value = int(temp_dict['load_percent'])
        actual_power = int(temp_dict['power'])
        
        rest_x = 250
        framebuffer.rect(rest_x, 99, 30, 102, 'black', False)
        framebuffer.rect(rest_x+1, 100 + 100 - percent_value, 28, percent_value, 'red', True)
        framebuffer.text( f'procent:{percent_value}%', rest_x, 220, 'black')
        framebuffer.text( f'moc:{actual_power}W', rest_x, 230, 'red')    
        #frame_update()

       
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

async def frame_update_async():
     while True:
          e.reset()
          e.init()
          frame_update()
          e.sleep
          await asyncio.sleep(60)

async def main(client):
    try:
        await client.connect()
        
    except OSError:
        print('Connection failed.')
        import machine
        machine.reset()
        print("ESP32 reset")
   
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
        #await frame_update_async()
        

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
asyncio.create_task(frame_update_async())
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop()
