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
    print("frame update")
     
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

import time

from writer import Writer
import out_font
#getting bigger font using Writer class and some code from the internet
class NotionalDisplay(framebuf.FrameBuffer):
    def __init__(self, width, height,buffer):
        self.width = width
        self.height = height
        self.buffer = buffer
        self.mode = framebuf.MONO_HLSB
        super().__init__(self.buffer, self.width, self.height, self.mode)
    def show():
        ...

my_text_display = NotionalDisplay(400, 300, buf_black)
my_text_display_red = NotionalDisplay(400, 300,buf_red)
wri = Writer(my_text_display, out_font)
wri_red = Writer(my_text_display_red, out_font) #quick workaround to get black on red
Writer.set_textpos(my_text_display, 235, 170)  # verbose = False to suppress console output
Writer.set_textpos(my_text_display_red,235,170)



  
def buffer_indicator(buffer_dict):
       
        temperatures_dict = {}

        for sensors, values in sorted(buffer_dict.items()):
            print(sensors, values)
            if 'temp' in sensors:
                temperatures_dict[sensors]=int(values)
        
        screen_width = 400
        screen_height = 300
        
        screen_horizontal_middle = screen_width/2

        i = 0
        lower_tempC = 30
        upper_tempC = 90
        delta_tempC = upper_tempC - lower_tempC
        
        buffer_tempbar_width = 100
        buffer_tempbar_height = 18
        
        buffer_x, buffer_y = int(screen_horizontal_middle - buffer_tempbar_width/2), 20
        #printing temperature values and creating temperature bars
        for temp_sens, value in sorted(temperatures_dict.items()):
            
            framebuffer.text(f'{value}C', buffer_x-30, buffer_y + int(buffer_tempbar_height/2) -3 + i, 'black')
            framebuffer.rect(buffer_x + 1,buffer_y+i+1, int(((value - lower_tempC)/delta_tempC)*buffer_tempbar_width), buffer_tempbar_height - 1,'red', True )
            i = i + buffer_tempbar_height

        bar_thickness = 2
        for layer in range(bar_thickness):    
            framebuffer.rect(buffer_x - layer, buffer_y - layer, buffer_tempbar_width + 2*layer, i+2*layer, 'black', False) #make one big black rectangle
        
        # percent load bar
        percent_value = int(buffer_dict['load_percent'])
        actual_power = int(buffer_dict['power'])
        
        screen_margin_y = 10
        bar_width = 150
        bar_height = 60
        load_buffer_x_pos = int(screen_horizontal_middle - bar_width/2)
        load_bufer_y_pos = 230
        load_bufer_y_pos = load_bufer_y_pos - screen_margin_y

        bar_thickness = 3
        for layer in range(bar_thickness):
            framebuffer.rect(load_buffer_x_pos-layer, load_bufer_y_pos-layer, bar_width+layer*2, bar_height+layer*2, 'black', False) #black frame #1

        framebuffer.rect(load_buffer_x_pos+1, load_bufer_y_pos+1, int(bar_width * (percent_value/100)), bar_height-2, 'red', True)
        framebuffer.text( f'procent:{percent_value}%', 300, 220, 'black')
        framebuffer.text( f'moc:{actual_power}W', 300, 230, 'red')    

        #wri.printstring(f'{percent_value}%\n', True) #showing bigger font for percent value -> but now disrupts all from whatever reason
        wri.printstring(f'{percent_value}', True)
        wri_red.printstring(f'{percent_value}') # %% is causing wwifi crash :O probably because it reads not existing chars
    
     
counter = 0
    

# Subscription callback
def sub_cb(topic, msg, retained):
    global counter
    temp_dict = {}
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    print(topic.decode())
   
    if topic.decode() == 'home/kotlownia/bufor':
        temp_msg = msg.decode()
        temp_dict = json.loads(temp_msg)
        print(temp_dict)
    
        framebuffer.fill('white')          
        buffer_indicator(temp_dict)
        print(counter)
        if counter == 0:
             asyncio.create_task(frame_first_update())
             counter += 1
        
async def frame_first_update():
     e.reset()
     e.init()
     current_time = time.localtime()
     formatted_time = "{:02}:{:02}:{:02}".format(current_time[3], current_time[4], current_time[5])
     framebuffer.text(formatted_time, 300, 270,'red')
     frame_update()
     e.sleep()

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
          current_time = time.localtime()
          formatted_time = "{:02}:{:02}:{:02}".format(current_time[3], current_time[4], current_time[5])
          framebuffer.text(formatted_time, 300, 270,'red')
          frame_update()
          e.sleep()
          await asyncio.sleep(60*5)

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
