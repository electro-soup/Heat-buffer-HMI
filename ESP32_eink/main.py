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

eink_display = epaper4in2.EPD(spi, cs, dc, rst, busy)
eink_display.init()

w = 400
h = 300
#TODO - timeout for waiting to idle
# --------------------

# use a frame buffer
# 400 * 300 / 8 = 15000 - thats a lot of pixels
import framebuf
buf_black = bytearray(w * h // 8)
buf_red = bytearray(w * h // 8)

#function to be always sure that eink is handled properly - if there is no reset, then we can not update anything
def eink_init_deinit_execute(callback):
    eink_display.reset()
    eink_display.init()
    callback()
    eink_display.display_frame(buf_black, buf_red)
    eink_display.sleep()

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
     eink_init_deinit_execute(clear_framebuffers)

black = 0
white = 1


from ThreeColorFrameBuffer import ThreeColorFrameBuffer

framebuffer = ThreeColorFrameBuffer(400, 300, fb_black, fb_red)

def frame_update():
    eink_display.reset()
    eink_display.init()
    eink_display.display_frame(buf_black,buf_red)
    print("frame update")
    eink_display.sleep()
     
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


#loading too much objects create issue with wifi startup

class ColorWriter(Writer):
     _instance = None
     
     def __new__(singleton_cls, device_black, device_red, font, verbose=True):
        if not singleton_cls._instance:
            singleton_cls._instance = super(ColorWriter, singleton_cls).__new__(singleton_cls)
            singleton_cls._instance._initialized = False
        return singleton_cls._instance

     def __init__(self, device_black, device_red, font, verbose=True):
          if self._initialized:
            return
          self.black_fb = device_black
          self.red_fb = device_red
          self.font = font #default font
          self.black_writer = Writer(self.black_fb, self.font, verbose)
          self.red_writer =  Writer(self.red_fb, self.font, verbose)
          self._initialized = True

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

     def get_stringlen_in_px(self, string, font_color):
         if font_color == 'black':
            return self.black_writer.stringlen(string)
         if font_color == 'red':
            return self.red_writer.stringlen(string)
    
class GUI_drawing:
    def __init__(self, x_pos, y_pos, width, height, drawing_function, *args):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.draw_func = drawing_function
        self.args = args
        self.height = height
        self.width = width
        self.previous_x_pos = None
        self.previous_y_pos = None
        gui_elements_list.append(self) #add each created object to that list

    def draw_element(self):
        self.draw_func(self.x_pos, self.y_pos,self.width, self.height, *self.args)
    
    def update(self):
        self.clear_area()
        self.draw_element()

    def clear_area(self):
        framebuffer.rect(self.x_pos, self.y_pos, self.width, self.height, 'white', fill = True)

    def update_position(self, new_pos_X, new_pos_y, refresh = False):
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos
        self.clear_area() #clean previous occupied area
        self.x_pos = new_pos_X
        self.y_pos = new_pos_y
        self.clear_area() #clear newly set area
        self.draw_element()
        if refresh is True:
            frame_update()
    
    def get_coords(self):
        return self.x_pos, self.y_pos
    
    def get_x_pos(self):
        return self.x_pos
    
    def get_y_pos(self):
        return self.y_pos

class GUI_text:
    
    def __init__(self, x_pos, y_pos, font, font_color = 'black'):
        self.y_pos = y_pos
        self.x_pos = x_pos
        self.font = font
        self.text = None
        self.color = font_color
        self.writer = ColorWriter(my_text_display, my_text_display_red, self.font)
        self.previous_x_pos = None
        self.previous_y_pos = None
        self.string_pixel_length = None
        gui_texts_list.append(self)
    
    def print(self, str_text, refresh = False):
        self.text = str_text
        self.writer.set_font(self.font)
        self.string_pixel_length = self.writer.get_stringlen_in_px(self.text, self.color)
        self.clear_background(self.x_pos, self.y_pos, self.string_pixel_length, self.font.height())
        self.writer.print(self.text, self.y_pos, self.x_pos, self.color, self.font)
        print("print")
        if refresh is True: 
            frame_update()

    def update(self):
        self.print(self.text, refresh = False)

    def get_text(self):
        return(self.text)
    
    def get_coords(self):
        return self.x_pos, self.y_pos
    
    def get_x_pos(self):
        return self.x_pos
    
    def get_y_pos(self):
        return self.y_pos
    
    def set_font(self, font):
        self.writer.set_font(font)

    def set_new_pos(self, new_x, new_y):
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos

        self.x_pos = new_x
        self.y_pos = new_y
        
    #init version - just redraw:

    def reprint(self, refresh = False):
        self.clear_background(self.previous_x_pos, self.previous_y_pos, self.string_pixel_length, self.font.height()) # make white rectangle to cover old string
        self.print(self.text, refresh)
       

    def clear_background(self, x_pos, y_pos, width, height, color = 'white', fill = True):
        framebuffer.rect(x_pos, y_pos, width, height, color, fill) # make white rectangle to cover old string/new string
    
    def test_partial_update(self):
        eink_display.wake_up()
        eink_display.send_buffer(buf_black, buf_red)
        eink_display.partial_refresh(self.x_pos, self.x_pos + self.string_pixel_length, self.y_pos, self.y_pos + self.font.height(), 1)
        eink_display.sleep()

color_writer = ColorWriter(my_text_display, my_text_display_red, font15_testall) 

   
def print_and_color_temp_diffs(value, format_string, row, column): #positive values - "+" and red, negative - black and "-"

    color_writer.set_font(font12_temperature)
    
    if value > 0:
         color_writer.print('+' + format_string, row, column +42, "red")
         draw_arrow(column, row, 30, 40, 'red')
         
    if value < 0:
         color_writer.print(format_string, row, column+42, "black")
         draw_arrow(column, row, 30, 40, 'black', direction="down")
        
    if value == 0:
        color_writer.print("", row, column, 'black')
        color_writer.print("", row, column, 'red')
       
  
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

          #print_and_color_temp_diffs(percent_diff, f'{percent_diff:.2f}%', 200, 270)
     

buffer_sensors_dict = {
     'temp0': 0,
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
     'update_time' : '',
     'avg_temp' : 0

}

solar_sensors_dict = {
      'solar_T0': 0, 
      'solar_T1': 0, 
      'solar_T2': 0,
      'solar_T3': 0
}      

mock_buffer_sensors_dict = {
     'temp0': 59,
     'temp1': 54,
     'temp2': 54,
     'temp3': 51,
     'temp4': 50,
     'temp5': 48,
     'temp6': 48,
     'temp7': 48,
     'temp8': 50,
     'kWh'  : 49,
     'load_percent': 35,
     'power': 990,
     'update_time' : '99/99/2137 99:99'
}

mock_solar_sensors_dict = {
      'solar_T0': 90, 
      'solar_T1': 89, 
      'solar_T2': 89,
      'solar_T3': 79
}

def mock_sensors():
     update_sensors_dict(mock_buffer_sensors_dict, buffer_sensors_dict)
     update_sensors_dict(mock_solar_sensors_dict, solar_sensors_dict)

def solar_indicator(x_pos, y_pos, solar_width, solar_height, solar_dict):
     
     
     temperature_correction = [0, 0, 2,0]
     
     framebuffer.rect(x_pos, y_pos, solar_width, solar_height, "black")
     framebuffer.rect(x_pos + 1, y_pos + 1, solar_width - 2, solar_height - 2, "red")

     t_spacing = round((solar_width - font15_testall.max_width()*2)/3)
     #print all temps in once
     
     color_writer.set_font(font15_testall)
     for i in range(4):
        color_writer.print(f'T{i}',y_pos-14,  x_pos + i*t_spacing )
       
     t_spacing = round((solar_width - font15_testall.max_width()*3)/3)
     
     for i in range(4):
        key = f'solar_T{i}'
        value = solar_dict[key] + temperature_correction[i]
        
        color_writer.print(f'{int(value)}°', y_pos+2, x_pos + i*t_spacing)

     #vertical lines simulating panels separation
     framebuffer.vline(x_pos + round(solar_width/3), y_pos, solar_height, "red")
     framebuffer.vline(x_pos + round(solar_width*2/3), y_pos, solar_height, "red")
     

def update_sensors_dict(dSourceSensors, dDestinationSensors): 
     for sensor, value in dSourceSensors.items():
          dDestinationSensors[sensor] = dSourceSensors[sensor]


"""
PSHS1000
          F = 0.79m
  <------------------->
   ___________________   <--- A,J,K,W | 2 m
  |                   |
  |                   |_
  |                   |_ <--- B,L     | 1.7m
  |                   |
  |                   |
  |                   |_
  |                   |_ <--- C,M     | 1.25m
  |                   |
  |                   |
  |                   |= (solar in)   | 0.9m
  |                   |_ 
  |                   |_ <--- D,N     | 0.75m
  |                   |
  |                   |  
  |                   |_
  |                   |_ <--- E,O,I   | 0.3m
  |                   |
  |                   | 
  |___________________|

"""
#buffer dimensions, in m

#TODO margin handling, because it causes very strange effects
def buffer_image(x_pos, y_pos, image_height, temperature_dict):
     
    buffer_height = 2.0
    buffer_width = 0.79
    stub_0 = 1.7
    stub_1 = 1.25
    stub_2 = 0.75
    stub_3 = 0.3
    stub_solar_in = 0.9  
    stub_1_5inch_size = 0.0375
    stub_1inch_size = 0.025

    x_offset = 30
    y_offset = 18

    def draw_stub(stub_x_pos, stub_height, stub_size, stub_length_in_px):
         
         scaling_factor = image_height/buffer_height
     
         stub_y_pos = round(scaling_factor * ((buffer_height - stub_height) - stub_size/2)) #upper edge
         stub_y_pos = stub_y_pos + y_pos + y_offset
         stub_size_in_pix = round(scaling_factor * stub_size) 
         framebuffer.hline(stub_x_pos, stub_y_pos, stub_length_in_px, 'black' )
         framebuffer.hline(stub_x_pos, stub_y_pos + stub_size_in_pix, stub_length_in_px, 'black' )
         
    
    lower_tempC = 30
    upper_tempC = 90
    delta_tempC = upper_tempC - lower_tempC
    image_width = round(buffer_width/buffer_height*image_height)
    
    buffer_tempbar_height = round(image_height/9)  
    
    second_wall_tank_x_pos = x_pos+ image_width + x_offset
    #drawing stubs - test
    draw_stub(second_wall_tank_x_pos, stub_0, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_1, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_2, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_3, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_solar_in, stub_1inch_size, 10)


    #printing buffer perimeter
    bar_thickness = 3
    for layer in range(bar_thickness):    
        framebuffer.rect( x_offset+x_pos - layer, y_offset + y_pos - layer, image_width + 2*layer, image_height+2*layer, 'black', False) #make one big black rectangle 
     
    color_writer.set_font(font15_testall) 
    color_writer.print("bufor", y_pos, x_pos +3)
    color_writer.set_font(font12_temperature)
    
    i = 0
    #printing temperature bars
    for temp_sens, value in sorted(temperature_dict.items()):
           
            framebuffer.rect(x_offset + x_pos + 1,y_offset + y_pos+i+1, round(((value - lower_tempC)/delta_tempC)*image_width), buffer_tempbar_height - 1,'red', True )
            color_writer.print(f'{value}°',y_offset+y_pos + i, x_pos )
            i = i + buffer_tempbar_height     

# TODO - showing position and sizes of given graphic element (debug mode)



def buffer_indicator(x_pos, y_pos, dummy_width, image_height, buffer_dict):
        
        temperatures_dict = {}
        #test_writer.set_textpos(my_text_display, 4, 4)
        #test_writer.printstring("!%()*+,-./0123456789:\n;<=>?@ABCDEFGHI\nJKLMNOPQRSTUVW \n XYZ[\]^_`abcd\nefghijklmnopqr\nstuvwxyz{|}°\nąężźćó\nĄĘŻŹĆÓ", True)
         
        for sensors, values in sorted(buffer_dict.items()):
            print(sensors, values)
            if 'temp' in sensors:
                if 'solar' not in sensors: #quick workaround for added sensor
                    temperatures_dict[sensors]=round(values)
        
        buffer_image(x_pos, y_pos, image_height, temperatures_dict)

        big_fonted_avg_temperature(buffer_dict)
        last_update_time(buffer_dict)
        print_power(buffer_dict)
        #percentage_load_bar(30,250, 100, 20,buffer_dict)
        big_fonted_percentage(buffer_dict)

          
def big_fonted_avg_temperature(buffer_dict):
        global g_average_temperature
        temperatures_dict={}
        for sensors, values in sorted(buffer_dict.items()):
            print(sensors, values)
            if 'temp' in sensors:
                if 'solar' not in sensors: #quick workaround for added sensor
                    temperatures_dict[sensors]=round(values)
       
        average_temperature = 0
        for temp_sens, value in sorted(temperatures_dict.items()):
           
            average_temperature += value/9
        buffer_dict['avg_temp']= average_temperature #to remove in the future
        GUI_loadbuffer_avg_temperature.print(f'{round(average_temperature)}°C')


def last_update_time(buffer_dict):
    color_writer.set_font(font15_testall)
    row = 140
    #color_writer.print('ostatnia', row + 20, 10)
    #color_writer.print('aktualizacja:', row + 40, 10)
    color_writer.print(buffer_sensors_dict['update_time'],row + 60, 10)

def print_power(buffer_dict):
        actual_power = round(buffer_dict['power'])
        text_power.print(f"moc: {actual_power}W")

def big_fonted_percentage(buffer_dict):
    percent_value = round(buffer_dict['load_percent'])
    GUI_loadbuffer_percentage.print(f'{percent_value}%')

def percentage_load_bar(x_pos, y_pos, bar_width, bar_height, buffer_dict):
        
        percent_value = round(buffer_dict['load_percent'])
       

        load_buffer_x_pos = x_pos
        load_bufer_y_pos = y_pos
        

        bar_thickness = 5
        for layer in range(bar_thickness):
            framebuffer.rect(load_buffer_x_pos-layer, load_bufer_y_pos-layer, bar_width+layer*2, bar_height+layer*2, 'black', False) #black frame #1
        
        for layer in range(bar_thickness-3):
            framebuffer.rect(load_buffer_x_pos-layer, load_bufer_y_pos-layer, bar_width+layer*2, bar_height+layer*2, 'white', False) #black frame #1
        
        red_bar_width = round(bar_width * (percent_value/100))
        framebuffer.rect(load_buffer_x_pos+1, load_bufer_y_pos+1, red_bar_width, bar_height-2, 'red', True)
        
        #add some vertical line to buffer bar 
        step = round(bar_width/10)
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

def draw_temperature_icon(x_pos, y_pos, width, height, buffer_dict):

    #draw bulb with mercury
    outer_radius = 10
    white_gap_radius = outer_radius - 2
    inner_red_radius = white_gap_radius - 1
    temperature_value = buffer_dict['avg_temp']
    right_x_pos = x_pos-round(width/2)
    
    #[middle_x_pos --- xpos ]
    relative_x = x_pos 
    relative_y = y_pos + height + inner_red_radius

    framebuffer.rect(right_x_pos-2, y_pos-2, width + 4 , height, 'black', False) # 
    framebuffer.rect(right_x_pos-3, y_pos-3, width + 6 , height, 'black', False) # 
    
    framebuffer.ellipse(relative_x, relative_y, outer_radius, outer_radius, 'black', True) #first black circle
    framebuffer.ellipse(relative_x, relative_y, white_gap_radius, white_gap_radius, 'white', False)
    framebuffer.rect(right_x_pos -1, y_pos-1, width + 2 , height, 'white', False) # white gap 
    framebuffer.rect( right_x_pos, y_pos +1, width, height, 'red', True) #red inside
    
    framebuffer.ellipse(relative_x, relative_y, inner_red_radius, inner_red_radius, 'red', True) #this should be rendered in the end

    #now make it do visuals:

    upper_temp_margin = 100
    lower_temp_margin = 0

    height_white_bar = height -  (height * temperature_value)/(upper_temp_margin-lower_temp_margin)
    height_white_bar = round(height_white_bar)
    framebuffer.rect( right_x_pos, y_pos, width, height_white_bar, 'white', True) #red inside
    print(f'executed draw_temperature_icon {temperature_value}')


gui_elements_list = []
gui_texts_list = []
GUI_loadbuffer_avg_temperature = GUI_text(250, 245, font42_bufferload, 'black')
GUI_loadbuffer_percentage = GUI_text(120, 245, font42_bufferload, 'black')

  #framebuffer.rect(240, 220,3,80,'black', fill=True)
  
solar = GUI_drawing(15, 15, 120, 70,solar_indicator, solar_sensors_dict)  
bufor = GUI_drawing(150,0,100, 150, buffer_indicator, buffer_sensors_dict) 
load_bar = GUI_drawing(10, 245, 100, 42, percentage_load_bar, buffer_sensors_dict)     
test_linia = GUI_drawing(0, 218, 340, 3, framebuffer.rect,'black', True)
test_linia2 = GUI_drawing(240, 218, 3, 400-218, framebuffer.rect,'black', True)
test_linia3 = GUI_drawing(test_linia.width, 0, 3, test_linia.y_pos + 3, framebuffer.rect, 'black', True)

text_bufor = GUI_text(20, 225, font15_testall, 'black')
text_bufor.print("naładowanie bufora:")

text_power = GUI_text(10, 100,font15_testall, 'black')

text_temperature = GUI_text(250, 225, font15_testall, 'black')
text_temperature.print("śr. temperatura:")

temperature_scale = GUI_drawing(375, 10, 6, 180, draw_temperature_icon, buffer_sensors_dict)
#




# some mingling with drawing assets as vectors
def draw_arrow(x_pos, y_pos, width, height, color, fill = True, direction = 'up'):
#how to handle arrays 
#import array
#myData = array.array('I', [10,10,120,30,30,61])
#The coords must be specified as a array of integers, e.g. array('h', [x0, y0, x1, y1, ... xn, yn]).   
     import array
     #for now - very naive representation
     x_zero_coord = 0
     y_zero_coord = 0

     y_middle = round(height/2)

     if direction == 'down':
        y_zero_coord = height
        height = 0


     points = [
         (round(width/3), height),  #point_0
         (round(width*2/3),height), #point_1
         (round(width*2/3), y_middle), #point_2
         (width, y_middle), #point_3
         (round(width/2), y_zero_coord), #point_4
         (x_zero_coord, y_middle), #point_5
         (round(width/3), y_middle) #point_6
        ]
     # Rozpakowanie krotek do jednej listy
     flattened_points = [value for point in points for value in point]
     arrow_coords = array.array('h', flattened_points)
     
     framebuffer.poly(x_pos, y_pos, arrow_coords, color, fill)
     


def GUI_update():
     global solar_sensors_dict
     global buffer_sensors_dict
     global global_dict_sensors

     for gui_item in gui_elements_list:
         gui_item.update()

     for text_item in gui_texts_list:
         text_item.update()
     #bufor.update()
     #load_bar.update()
     #buffer_indicator(170, 20,150,buffer_sensors_dict)
      
     

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
        color_writer.set_font(font3Mono)
         

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
        #GUI_update()
        print(counter)
    try:
        dMQTT_function_mapping[decoded_topic](eval_dict) #it completely brokes that function 
    except:
        print(f"internal error for function mapped for {eval_dict}")


async def frame_first_update():
     await asyncio.sleep(1) # wait a second
     def local_time():
        current_time = time.localtime()
        formatted_time = "{:02}:{:02}:{:02}".format(current_time[3], current_time[4], current_time[5])
        framebuffer.text(formatted_time, 300, 270,'red')
   
     eink_init_deinit_execute(GUI_update) #this function is very unclear right now

def debug_draw_grid():
    #50px x 50px
     x_width = 400
     y_width = 300
     color_writer.set_font(font3Mono)
     for test_x in range(0,400, 50):
       color_writer.print(f'{test_x}', 250, test_x, 'red')
     
     for test_y in range(0,300, 50):
         color_writer.print(f'{test_y}', test_y,48,  'black')

     
     for test_x in range(0,400, 50):
        for y in range(0,300,5):
            framebuffer.pixel(test_x, y, 'red')

     for test_y in range(0,300, 50):
        for test_x in range(0,400, 5):
             framebuffer.pixel(test_x,test_y, 'black')
     
     frame_update()
     


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
                  clear_framebuffers()
                  text_to_print = "brak ramek z danymi z kotłowni"
                  x_pos_of_string = (400 - (font15_testall.max_width()*len(text_to_print)))/2
                  x_pos_of_string = round(x_pos_of_string)
                  color_writer.print(text_to_print, 150, x_pos_of_string, "black")
                  frame_update()
              
              if waiting_counter == 60:
                  clear_screen()


          print("async frame update")
          previous_meas_dict = global_dict_sensors
          # TODO - check timings here and flow
          minutes_to_wait = 5
          await asyncio.sleep(60*minutes_to_wait)
          eink_display.reset()
          eink_display.init()

          show_temperature_and_load_difference(previous_meas_dict,global_dict_sensors)
        
          
          #current_time = time.localtime()
          #formatted_time = "{:02}:{:02}:{:02}".format(current_time[3], current_time[4], current_time[5])
          #framebuffer.text(formatted_time, 300, 270,'red')
          GUI_update()
          frame_update()
          

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
                
                
                frame_update()
                print("reset after 3min from startup - no mqtt")
                machine.reset()

        temp_counter = counter # TODO: check if this makes sense at all

        await asyncio.sleep(60*10)
        if counter == temp_counter:
            # TODO clean this up     
            clear_framebuffers()
           
            frame_update()
            print("reset from simple watchdog")  
            machine.reset() #if there is no new mqtt message - reset - but in the future it should be error handling (mqtt server maybe down etc)


async def main(client):
    try:
        await client.connect()
        
    except OSError:
        print('Connection failed.')
        clear_framebuffers()
           
        
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

except OSError as eink_display:
        print("OSError:", eink_display)
        
        # TODO handling of those errors - when I ctr-c repl, then it goes straight to reset point
except Exception as eink_display:
        print("exception error:", eink_display)
        
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop() #this works? 
 
# TODO displaying errors on eink
# TODO sending and subscribing same topic as closed loop
# TODO if ecu is close to router, it keeps going blank (wifi is down)
        
# TODO if there is no connection over long period of time - screen should be cleared once per hour