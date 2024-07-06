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

def clear_framebuffers():
    fb_red.fill(white)
    fb_black.fill(white)


def clear_screen():
    
    e.reset()
    e.init()
    clear_framebuffers()
    e.display_frame(buf_black, buf_red)
    e.sleep()


black = 0
white = 1


from ThreeColorFrameBuffer import ThreeColorFrameBuffer

framebuffer = ThreeColorFrameBuffer(400, 300, fb_black, fb_red)

def frame_update():
    e.display_frame(buf_black,buf_red)
    print("frame update")
     
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


outages = 0
temp = []

import time

from writer import Writer
import font42_bufferload
import font12_temperature
import font15_testall
import font3Mono

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
wri = Writer(my_text_display, font42_bufferload)
writer_temperatures = Writer(my_text_display, font12_temperature)
test_writer = Writer(my_text_display, font15_testall)
writer_red_power = Writer(my_text_display_red, font15_testall)
writer_temperatures_red = Writer(my_text_display_red, font12_temperature)
#loading too much objects create issue with wifi startup

class ColorWriter(Writer):
     def __init__(self, device_black, device_red, font, verbose=True):
          self.black_fb = device_black
          self.red_fb = device_red
          self.font = font #default font
          self.black_writer = Writer(self.black_fb, self.font, verbose)
          self.red_writer =  Writer(self.red_fb, self.font, verbose)

     def print(self, text, row, column, color = 'black', font = None): #assume implicitly that black is used
        
          if color == 'black':
               if font is not None:
                    self.black_writer.font = font
               self.black_writer.set_textpos(self.black_fb, row, column) #it is quite possible that there is only framebuffer to be changed
               self.black_writer.printstring(text, True)
          if color == 'red':
               if font is not None:
                    self.red_writer.font = font
               self.red_writer.set_textpos(self.red_fb,row,column)
               self.red_writer.printstring(text, True)
      
     def set_font(self,font): #to avoid typing font if we are intent to use it consecutively in the code
          self.black_writer.font = font
          self.red_writer.font = font

color_writer = ColorWriter(my_text_display, my_text_display_red, font15_testall) 

def eink_debug_print(string_to_print, row, column, color):
     e.reset()
     e.init()
     
     color_writer.print(string_to_print, row, column, color, font15_testall)
     frame_update()
     e.sleep()

def writer_print_text_temperatures(string_to_print, row, column, color):
    
    writer_temperatures.set_textpos(my_text_display, row, column)
    writer_temperatures_red.set_textpos(my_text_display_red, row, column)
    writer_temperatures.printstring('',True)
    writer_temperatures_red.printstring('',True) #clear both colors at the beginning
    
    if color == 'red':
                writer_temperatures_red.printstring(string_to_print,True)
    
    if color == 'black':
                writer_temperatures.printstring(string_to_print,True)
    
def print_and_color_temp_diffs(value, format_string, row, column): #positive values - "+" and red, negative - black and "-"

    color_writer.set_font(font12_temperature)
    
    if value > 0:
         color_writer.print('+' + format_string, row, column, "red")
         
    if value < 0:
         color_writer.print('+' + format_string, row, column, "black")
        
    if value == 0:
        color_writer("", row, column)
        
  
def show_temperature_and_load_difference(previous_meas_dict,global_dict_sensors):
        
          temperature_diff = {} 
          average_temp_change = 0
          
          kwh_change = 0

          for sensors, values in sorted(previous_meas_dict.items()):
            print(sensors, values)
            if 'temp' in sensors: 
                   if 'solar' not in sensors: #to be refactored
                     temp_difference = global_dict_sensors[sensors] - previous_meas_dict[sensors]  
                     print(f'{temp_difference}C diff')
                     temperature_diff[sensors]=temp_difference 
                     average_temp_change += temp_difference/9
          
          a = 'kWh'
          #1% - 0,628kWh
          kwh_change = global_dict_sensors[a] - previous_meas_dict[a]
          percent_diff = (kwh_change)/0.628 
          
          print(f'Percent_diff:{percent_diff:.2f}%')
         
          
          #i = 0
          #for temperature, value in sorted(temperature_diff.items()):
            
           # print_and_color_temp_diffs(value, f'{value:.2f}°C', 20 + i, 270)
           # i = i + 18
          
          print_and_color_temp_diffs(percent_diff, f'{percent_diff:.2f}%', 200, 270)
          #print_and_color_temp_diffs(kwh_change, f'{kwh_change:.2f}kWh', 215, 270)
          #print_and_color_temp_diffs(average_temp_change, f'{average_temp_change:.2f}°C',  262 , 10)

buffer_sensors_dict = {
     'temp1': 0,
     'temp2': 0,
     'temp3': 0,
     'temp4': 0,
     'temp5': 0,
     'temp6': 0,
     'temp7': 0,
     'temp8': 0,
     'kWh'  : 0,
     'load_percent': 0,
     'power': 0,
     'update_time' : ''

}

solar_sensors_dict = {
      'solar_T0': 0, 
      'solar_T1': 0, 
      'solar_T2': 0,
      'solar_T3': 0
}      



def solar_indicator(solar_dict):
     
     x_pos = 265
     y_pos = 15
     solar_width = 120
     solar_height = 70
     temperature_correction = [0, 0, 2,0]
     

    
     framebuffer.rect(x_pos, y_pos, solar_width, solar_height, "black")
     framebuffer.rect(x_pos + 1, y_pos + 1, solar_width - 2, solar_height - 2, "red")

     t_spacing = int((solar_width - font15_testall.max_width()*2)/3)
     #print all temps in once
     
     color_writer.set_font(font15_testall)
     for i in range(4):
        color_writer.print(f'T{i}',y_pos-14,  x_pos + i*t_spacing )
       
     t_spacing = int((solar_width - font15_testall.max_width()*3)/3)
     
     for i in range(4):
        key = f'solar_T{i}'
        value = solar_dict[key] + temperature_correction[i]
        
        color_writer.print(f'{int(value)}°', y_pos+2, x_pos + i*t_spacing)

     color_writer.print("solar", 39, 300)
     #vertical lines simulating panels separation
     framebuffer.vline(x_pos + int(solar_width/3), y_pos, solar_height, "red")
     framebuffer.vline(x_pos + int(solar_width*2/3), y_pos, solar_height, "red")
     



def update_sensors_dict(dSourceSensors, dDestinationSensors): #risky - for now no handling if something is not definied 
     for sensor, value in dDestinationSensors.items():
          dDestinationSensors[sensor] = dSourceSensors[sensor]

def buffer_indicator(buffer_dict):
        
        temperatures_dict = {}
        #test_writer.set_textpos(my_text_display, 4, 4)
        #test_writer.printstring("!%()*+,-./0123456789:\n;<=>?@ABCDEFGHI\nJKLMNOPQRSTUVW \n XYZ[\]^_`abcd\nefghijklmnopqr\nstuvwxyz{|}°\nąężźćó\nĄĘŻŹĆÓ", True)
        
        for sensors, values in sorted(buffer_dict.items()):
            print(sensors, values)
            if 'temp' in sensors:
                if 'solar' not in sensors: #quick workaround for added sensor
                    temperatures_dict[sensors]=int(values)
        
        screen_width = 400
        screen_height = 300
        

        screen_horizontal_middle = screen_width/2

        i = 0
        lower_tempC = 30
        upper_tempC = 90
        delta_tempC = upper_tempC - lower_tempC
        average_temperature = 0
        buffer_tempbar_width = 100
        buffer_tempbar_height = 18
        
        buffer_x, buffer_y = int(screen_horizontal_middle - buffer_tempbar_width/2), 20
        #printing temperature values and creating temperature bars

        color_writer.set_font(font12_temperature)

        for temp_sens, value in sorted(temperatures_dict.items()):
           
            framebuffer.rect(buffer_x + 1,buffer_y+i+1, int(((value - lower_tempC)/delta_tempC)*buffer_tempbar_width), buffer_tempbar_height - 1,'red', True )
            #test - using writer class to show temperatures (works fine)
            color_writer.print(f'{value}°C',buffer_y + i, buffer_x-40 )
        
            i = i + buffer_tempbar_height
            average_temperature += value/8
        
        column = 270
        row = 100
        color_writer.set_font(font15_testall)

        color_writer.print('średnia', row, column)
        color_writer.print('temperatura', row+20, column)
        
        color_writer.set_font(font42_bufferload)
        color_writer.print(f'{int(average_temperature)}°C', row+40, column)
        
        
        bar_thickness = 2

        for layer in range(bar_thickness):    
            framebuffer.rect(buffer_x - layer, buffer_y - layer, buffer_tempbar_width + 2*layer, i+2*layer, 'black', False) #make one big black rectangle
        
        # percent load bar
        percent_value = int(buffer_dict['load_percent'])
        actual_power = int(buffer_dict['power'])
        
        screen_margin_y = 10
        bar_width = 150
        bar_height = 30
        load_buffer_x_pos = int(screen_horizontal_middle - bar_width/2)
        load_bufer_y_pos = 250
        

        bar_thickness = 5
        for layer in range(bar_thickness):
            framebuffer.rect(load_buffer_x_pos-layer, load_bufer_y_pos-layer, bar_width+layer*2, bar_height+layer*2, 'black', False) #black frame #1
        
        for layer in range(bar_thickness-3):
            framebuffer.rect(load_buffer_x_pos-layer, load_bufer_y_pos-layer, bar_width+layer*2, bar_height+layer*2, 'white', False) #black frame #1
        
       

        red_bar_width = int(bar_width * (percent_value/100))
        framebuffer.rect(load_buffer_x_pos+1, load_bufer_y_pos+1, red_bar_width, bar_height-2, 'red', True)
        
        #add some vertical line to buffer bar 
        step = int(bar_width/10)
        for factor in range(1,10):
             color_str = ''
             vline_pos = step * factor
             if vline_pos < red_bar_width:
                color = "white"
             else:
                color = "black"
             
             color = "white"
             framebuffer.vline(load_buffer_x_pos + vline_pos-1, load_bufer_y_pos+1,bar_height, color)
             framebuffer.vline(load_buffer_x_pos + vline_pos, load_bufer_y_pos+1,bar_height, color)
             framebuffer.vline(load_buffer_x_pos + vline_pos+1, load_bufer_y_pos+1,bar_height, color)

        color_writer.set_font(font15_testall)
        color_writer.print(f"moc: {actual_power}W", 250, 300)
      
        #big fonted percent value 
        writer_row_pos = 195
        writer_col_pos = 160 
        color_writer.set_font(font42_bufferload)
        color_writer.print(f'{percent_value}%',writer_row_pos, writer_col_pos )
       
        
        color_writer.set_font(font15_testall)
        row = 140
        color_writer.print('ostatnia', row + 20, 10)
        color_writer.print('aktualizacja:', row + 40, 10)
        color_writer.print(buffer_sensors_dict['update_time'],row + 60, 10)

        

def GUI_update():
     global solar_sensors_dict
     global buffer_sensors_dict
     global global_dict_sensors

     #buffer_sensors_dict = global_dict_sensors #how it is working if global_dict_sensors is not definied here?
     #update_sensors_dict(global_dict_sensors, buffer_sensors_dict)
     #update_sensors_dict(global_dict_sensors, solar_sensors_dict)

     buffer_indicator(buffer_sensors_dict)
     solar_indicator(solar_sensors_dict)   #to be changed after refactor  
     
counter = 0
    
global_dict_sensors = {}

# Subscription callback
def sub_cb(topic, msg, retained):
    global counter
    temp_dict = {}
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    print(topic.decode())
   
    global global_dict_sensors

    if topic.decode() == 'home/kotlownia/bufor':

        
        temp_msg = msg.decode()
        temp_dict = json.loads(temp_msg)
        print(temp_dict)
        global_dict_sensors = temp_dict  #copy it to the global dict (temp solution)
        framebuffer.fill('white')          
        if counter == 0: #before GUI update - to prevent from unwanted resets because of bug in buffer_ind
             asyncio.create_task(frame_first_update())
        counter += 1
        update_sensors_dict(global_dict_sensors, buffer_sensors_dict)
        update_sensors_dict(global_dict_sensors, solar_sensors_dict)
        GUI_update()
        #buffer_indicator(temp_dict)
        print(counter)
        
        
async def frame_first_update():
     await asyncio.sleep(1) # wait a second
     e.reset()
     e.init()
     current_time = time.localtime()
     formatted_time = "{:02}:{:02}:{:02}".format(current_time[3], current_time[4], current_time[5])
     framebuffer.text(formatted_time, 300, 270,'red')
     frame_update()
     e.sleep()

async def frame_clear_async():
     clear_screen()


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


async def frame_update_async():
     while True:
          global counter
          while (counter == 0):
              print("waiting for first mqtt frame ")
              await asyncio.sleep(5)


          print("async frame update")
          previous_meas_dict = global_dict_sensors
          # TODO - check timings here and flow
          minutes_to_wait = 5
          await asyncio.sleep(60*minutes_to_wait)
          e.reset()
          e.init()

          show_temperature_and_load_difference(previous_meas_dict,global_dict_sensors)
        
          
          current_time = time.localtime()
          formatted_time = "{:02}:{:02}:{:02}".format(current_time[3], current_time[4], current_time[5])
          framebuffer.text(formatted_time, 300, 270,'red')
          frame_update()
          e.sleep()

#temp function to reset system if there is no proper error handling coded
async def reset_system():
     import machine
     while True:
          await asyncio.sleep(60*60*6) # perform reset after 6 hours
          print("reset in the loop")
          machine.reset()

async def simple_watchdog():
    
    global counter
    import machine
    temp_counter = 0
    while True:
    # TODO - here everything is to be refactored, it is not clear at all
        while counter == 0:
            await asyncio.sleep(60*3) #wait 1 minute - if counter is 0 (no MQTT frames )
            if counter == 0:
                clear_framebuffers()
                
                for i in range (9):
                  test_writer.set_textpos(my_text_display,10 , 170 )
                  test_writer.printstring("brak połączenia przez okres 3 minut przy starcie, restart systemu") 
                frame_update()
                print("reset after 3min from startup - no mqtt")
                machine.reset()

        temp_counter = counter # TODO: check if this makes sense at all

        await asyncio.sleep(60*10)
        if counter == temp_counter:
            # TODO clean this up     
            clear_framebuffers()
            for i in range (9):
                test_writer.set_textpos(my_text_display,170, 10 + i * 14)
                test_writer.printstring("brak nowych MQTT w ciągu 10 minut, restart systemu") 
            frame_update()
            print("reset from simple watchdog")  
            machine.reset() #if there is no new mqtt message - reset - but in the future it should be error handling (mqtt server maybe down etc)


    

async def main(client):
    try:
        await client.connect()
        
    except OSError:
        print('Connection failed.')
        clear_framebuffers()
           
        for i in range (9):
            test_writer.set_textpos(my_text_display,10 + i * 14, 20 )
            test_writer.printstring("brak połączenia przez okres 1 minuty przy starcie, restart systemu\n") 
        #frame_update()
        asyncio.create_task(frame_clear_async())
       
     
        # TODO - proper handling of this error - it just stays here (without reset)
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
#increasing response time fixed issue with disconnecting wifi
#init gui update
clear_framebuffers() # TODO without it screen is red - to investigate
GUI_update()
frame_update()
# Set up client
MQTTClient.DEBUG = True  # Optional




client = MQTTClient(config)


asyncio.create_task(heartbeat())
asyncio.create_task(frame_update_async())


from machine import WDT
minutes = 20
watchdog = WDT(timeout = 1000 * 60 * minutes)

try:
    asyncio.run(main(client))

except OSError as e:
        print("OSError:", e)
        eink_debug_print(e, 1, 1, "black")
        # TODO handling of those errors - when I ctr-c repl, then it goes straight to reset point
except Exception as e:
        print("exception error:", e)
        eink_debug_print(e, 50, 1, "red")
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop() #this works? 
 
# TODO displaying errors on eink
# TODO sending and subscribing same topic as closed loop
# TODO if ecu is close to router, it keeps going blank (wifi is down)
        
# TODO if there is no connection over long period of time - screen should be cleared once per hour