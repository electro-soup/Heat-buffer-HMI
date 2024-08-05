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


#function/wrapper which ensures that eink display is initialised and then put to sleep after sending data to it
def eink_update(function):
    def wrapper():
        eink_display.reset()
        eink_display.init()
        function()
        eink_display.display_frame(buf_black, buf_red)
        eink_display.sleep()
    return wrapper

#creating two buffers, one for black, second for red pixels
fb_black = framebuf.FrameBuffer(buf_black, w, h, framebuf.MONO_HLSB)
fb_red = framebuf.FrameBuffer(buf_red, w, h, framebuf.MONO_HLSB)
black = 0
white = 1
red = 0


def clear_framebuffers():
    fb_red.fill(white)
    fb_black.fill(white)

@eink_update
def clear_screen():
     clear_framebuffers()

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
                    if 'solar' not in sensors and 'avg' not in sensors:  #to be refactored
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




def update_sensors_dict(dSourceSensors, dDestinationSensors): 
     for sensor, value in dSourceSensors.items():
          dDestinationSensors[sensor] = dSourceSensors[sensor]

def mock_sensors():
     update_sensors_dict(mock_buffer_sensors_dict, buffer_sensors_dict)
     update_sensors_dict(mock_solar_sensors_dict, solar_sensors_dict)


def solar_indicator(x_pos, y_pos, solar_width, solar_height, solar_dict):
          
     temperature_correction = [0, 0, 2,0]
 
     single_solar_width = round(solar_width/3)
     
     space_between_panels = 2
     
     for i in range(3):
      
        round_rectangle(x_pos + i*(single_solar_width + space_between_panels), y_pos, single_solar_width, solar_height, 4, 2, 2, "black")
        
        round_rectangle(x_pos + i*(single_solar_width + space_between_panels) +1, y_pos +1, single_solar_width-2, solar_height-2, 1, 2, 2, "white")
    
        #demo of filling space with dots
    
        for x in range(1,single_solar_width, 2):
           for y in range(1,solar_height, 2):
             framebuffer.pixel(x+x_pos + i*(single_solar_width + space_between_panels),y+y_pos,'black')

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
    lower_tempC = 30
    upper_tempC = 90
    delta_tempC = upper_tempC - lower_tempC
    image_width = round(buffer_width/buffer_height*image_height)
    
    #demo of filling space with dots
    
       
    line_thickness = 3
      
    #drawing order : red temp bars, then white bars which shorten red bars, at the end buffer perimeter and temps
    color_writer.set_font(font15_testall) 
    color_writer.print("bufor", y_pos, x_pos +3)
    color_writer.set_font(font12_temperature)
    
    
    #printing red temperature bars
    #estimate the empty area inside for better readibility of the code:
    empty_height = image_height - 2 *line_thickness
    empty_width = image_width - 2*line_thickness

    empty_x_pos = x_offset + x_pos + line_thickness
    empty_y_pos =  y_offset + y_pos+ line_thickness

    i = 0
    gap_size = 2
    buffer_tempbar_height = round((empty_height - 8*gap_size)/9)
    
    tempbar_spacing = buffer_tempbar_height + gap_size
    #adjust buffor image height to avoid misalignemnt because of fractionals
    new_buffer_image_height = 2 *line_thickness + 9 * buffer_tempbar_height + 8 * gap_size
    #demo filling buffer with dots:
    import math
    empty_image_width = image_width - 2 *line_thickness
    


    def draw_dithered_rect(x, y, w, h, percent):
    #https://medium.com/the-bkpt/dithered-shading-tutorial-29f57d06ac39
      # Wzorzec Bayera 8x8, znormalizowany do zakresu 0-255
        threshold_map = [
             [  0,  48,  12,  60,   3,  51,  15,  63],
             [ 32,  16,  44,  28,  35,  19,  47,  31],
             [  8,  56,   4,  52,  11,  59,   7,  55],
             [ 40,  24,  36,  20,  43,  27,  39,  23],
             [  2,  50,  14,  62,   1,  49,  13,  61],
             [ 34,  18,  46,  30,  33,  17,  45,  29],
             [ 10,  58,   6,  54,   9,  57,   5,  53],
             [ 42,  26,  38,  22,  41,  25,  37,  21]
           ]

     # Przeskalowanie mapy do zakresu 0-255
        threshold_map = [[int(val * 255 / 64) for val in row] for row in threshold_map]

        level = percent * 255 / 100  # Konwersja procentów na skalę 0-255

        for i in range(h):
         for j in range(w):
            threshold = threshold_map[i % 8][j % 8]
            color = "red" if level > threshold else "white"
            framebuffer.pixel(x + j, y + i, color)

     # draw 3D dots
    #radial resolution (make sure for closet pixel distance = 2)
    resolution = 10

    for alfa in range(0, 180, resolution):
           x =  round(empty_image_width/2 - (empty_image_width/2*math.cos(math.radians(alfa))))
           for y in range(1,new_buffer_image_height, 2):
             framebuffer.pixel(empty_x_pos + x,y+empty_y_pos,'black')
    demo = 1
    import random
    #draw red temperatture bars
    for temp_sens, value in sorted(temperature_dict.items()):
            if demo == 0:
                framebuffer.rect( empty_x_pos  ,empty_y_pos +i, round(((value - lower_tempC)/delta_tempC)*empty_width), buffer_tempbar_height,'red', True )
            color_writer.print(f'{value}°',empty_y_pos + i, x_pos )
            
            if demo == 1:
                draw_dithered_rect(empty_x_pos, empty_y_pos +i, empty_width, buffer_tempbar_height+gap_size, round(((value - lower_tempC)/delta_tempC*100)))

            i = i + tempbar_spacing #it must stay here! 

    
   
    
    def draw_stub(stub_x_pos, stub_height, stub_size, stub_length_in_px):
         
         scaling_factor = image_height/buffer_height
     
         stub_y_pos = round(scaling_factor * ((buffer_height - stub_height) - stub_size/2)) #upper edge
         stub_y_pos = stub_y_pos + y_pos + y_offset
         stub_size_in_pix = round(scaling_factor * stub_size) 
         framebuffer.hline(stub_x_pos, stub_y_pos, stub_length_in_px, 'black' )
         framebuffer.hline(stub_x_pos, stub_y_pos + stub_size_in_pix, stub_length_in_px, 'black' )
         
    
  
    
    second_wall_tank_x_pos = x_pos+ image_width + x_offset
    #drawing stubs - test
    draw_stub(second_wall_tank_x_pos, stub_0, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_1, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_2, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_3, stub_1_5inch_size, 10)
    draw_stub(second_wall_tank_x_pos, stub_solar_in, stub_1inch_size, 10)


    #printing buffer perimeter
    #test = clearing area for shaping red temp bars:
    for y_offs in range (round(image_height/12)):
        round_rectangle( x_offset+x_pos, y_offset + y_pos - y_offs, image_width, new_buffer_image_height + 2* y_offs, line_thickness, round(image_width/2.3), round(image_height/12), 'white') #make one big black rectangle 
    
    #draw perime
    round_rectangle( x_offset+x_pos, y_offset + y_pos, image_width, new_buffer_image_height, line_thickness, round(image_width/2.3), round(image_height/12), 'black') #make one big black rectangle 
    

# TODO - showing position and sizes of given graphic element (debug mode)

def buffer_indicator(x_pos, y_pos, dummy_width, image_height, buffer_dict):
        
        temperatures_dict = {}
        #test_writer.set_textpos(my_text_display, 4, 4)
        #test_writer.printstring("!%()*+,-./0123456789:\n;<=>?@ABCDEFGHI\nJKLMNOPQRSTUVW \n XYZ[\]^_`abcd\nefghijklmnopqr\nstuvwxyz{|}°\nąężźćó\nĄĘŻŹĆÓ", True)
         
        for sensors, values in sorted(buffer_dict.items()):
            print(sensors, values)
            if 'temp' in sensors:
                 if 'solar' not in sensors and 'avg' not in sensors:  #quick workaround for added sensor
                    temperatures_dict[sensors]=round(values)
        
        buffer_image(x_pos, y_pos, image_height, temperatures_dict)

        big_fonted_avg_temperature(buffer_dict)
        last_update_time(buffer_dict)
        print_power(buffer_dict)
        big_fonted_percentage(buffer_dict)

          
def big_fonted_avg_temperature(buffer_dict):
        global g_average_temperature
        temperatures_dict={}
        for sensors, values in sorted(buffer_dict.items()):
            print(sensors, values)
            if 'temp' in sensors:
                 if 'solar' not in sensors and 'avg' not in sensors:  #quick workaround for added sensor
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
    temp_temperature_division(-2*width, 0, width, temperature_scale)



def temp_temperature_division(x_offset, y_offset, width, temperature_scale):
    
    div_x_pos = x_offset + temperature_scale.x_pos
    div_scale_10_height = round(temperature_scale.height/10)
    font_offset_y = round(div_scale_10_height/2) 
    font_offset_x = 35


    for i in range(0, 11): #big divisions (10 degres)
      div_y_pos = y_offset + temperature_scale.y_pos + i * div_scale_10_height
       
      framebuffer.hline(div_x_pos,div_y_pos, width+1, 'black')
      color_writer.set_font(font15_testall)
      color_writer.print(f'{100 - i *10}', div_y_pos - font_offset_y , temperature_scale.x_pos - font_offset_x , 'black')
      if i != 10:
        framebuffer.hline(div_x_pos + round(width/2) , div_y_pos + round(div_scale_10_height/2), round(width/2)+1, 'black') # 5 degree div


def round_rectangle(x_pos, y_pos, width, height, line_width,radius_x, radius_y,  color):

    upper_line_x = x_pos+radius_x
    upper_line_y = y_pos
    left_line_x = x_pos
    left_line_y = y_pos+radius_y
    
    horizontal_line_width = width - 2* radius_x
    vertical_line_height = height - 2*radius_y
    
    #test left upper part:

    #draw left and upper line:
    framebuffer.rect(left_line_x,left_line_y ,line_width,vertical_line_height,color, True)
    framebuffer.rect(upper_line_x,upper_line_y,horizontal_line_width,line_width,color, True)

    #draw right and down line:
    framebuffer.rect(left_line_x + horizontal_line_width + 2*radius_x - line_width, left_line_y,line_width,vertical_line_height,color, True)
    framebuffer.rect(upper_line_x,upper_line_y + vertical_line_height + 2*radius_y - line_width,horizontal_line_width ,line_width, color, True)
    
    #TODO - handling minus values (it stucks the system!) if radius is 0 or lower ( radius_y-i)
    #and connect both and make a corner:
    def assert_one(number): #temp patch for framebuffer.ellipse 
        if number < 1:
            return 1
        else:
            return number

    for i in range(line_width):
        
        #upper left
        framebuffer.ellipse(upper_line_x + i, left_line_y, radius_x, radius_y, color,False, 0b0010)
        framebuffer.ellipse(upper_line_x, left_line_y+i, radius_x, radius_y, color, False, 0b0010)
        framebuffer.ellipse(upper_line_x, left_line_y, assert_one(radius_x-i), assert_one(radius_y-i), color, False, 0b0010) #additional circles
        
        right_up_corner_x = upper_line_x + horizontal_line_width -1
        
        #upper right
        framebuffer.ellipse(right_up_corner_x - i, left_line_y, radius_x, radius_y, color,False, 0b0001)
        framebuffer.ellipse(right_up_corner_x, left_line_y+i, radius_x, radius_y, color, False, 0b0001)
        framebuffer.ellipse(right_up_corner_x , left_line_y, assert_one(radius_x-i), assert_one(radius_y-i), color, False, 0b0001)
        
        right_down_corner_x = right_up_corner_x
        down_y = left_line_y+vertical_line_height -1
        #upper right
        framebuffer.ellipse(right_down_corner_x - i, down_y, radius_x, radius_y, color,False, 0b1000)
        framebuffer.ellipse(right_down_corner_x, down_y-i, radius_x, radius_y, color, False, 0b1000)
        framebuffer.ellipse(right_down_corner_x , down_y, assert_one(radius_x-i), assert_one(radius_y-i), color, False, 0b1000)

        #down left
        framebuffer.ellipse(upper_line_x + i, down_y, radius_x, radius_y, color,False, 0b0100)
        framebuffer.ellipse(upper_line_x, down_y-i, radius_x, radius_y, color, False, 0b0100)
        framebuffer.ellipse(upper_line_x , down_y, assert_one(radius_x-i), assert_one(radius_y-i), color, False, 0b0100)
        


gui_elements_list = []
gui_texts_list = []
GUI_loadbuffer_avg_temperature = GUI_text(250, 245, font42_bufferload, 'black')
GUI_loadbuffer_percentage = GUI_text(120, 245, font42_bufferload, 'black')

  #framebuffer.rect(240, 220,3,80,'black', fill=True)
  
solar = GUI_drawing(15, 15, 120, 70,solar_indicator, solar_sensors_dict)  
bufor = GUI_drawing(150,0,100, 170, buffer_indicator, buffer_sensors_dict) 
load_bar = GUI_drawing(10, 245, 100, 42, percentage_load_bar, buffer_sensors_dict)     
test_linia = GUI_drawing(0, 218, 330, 3, framebuffer.rect,'black', True)
test_linia2 = GUI_drawing(240, test_linia.y_pos, 3, 400-test_linia.y_pos, framebuffer.rect,'black', True)
test_linia3 = GUI_drawing(test_linia.width, 0, 3, test_linia.y_pos + 3, framebuffer.rect, 'black', True)

text_bufor = GUI_text(20, 225, font15_testall, 'black')
text_bufor.print("naładowanie bufora:")

text_power = GUI_text(10, 100,font15_testall, 'black')

text_temperature = GUI_text(250, 225, font15_testall, 'black')
text_temperature.print("śr. temperatura:")

temperature_scale = GUI_drawing(375, 15, 6, 180, draw_temperature_icon, buffer_sensors_dict)
#

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
 
     for gui_item in gui_elements_list:
         gui_item.update()

     for text_item in gui_texts_list:
         text_item.update()
  

def fast_debug():
    mock_sensors()
    GUI_update()
    frame_update()     


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
        for test_x in range(0,400, 10):
             framebuffer.pixel(test_x,test_y, 'black')
     
     frame_update()        