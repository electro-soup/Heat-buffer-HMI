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
fb_black.fill(white)
fb_red.fill(white)

# --------------------

# write hello world with black bg and white text
#from image_dark import hello_world_dark
#from image_light import hello_world_light
#print('Image dark')
#bufImage = hello_world_dark
#fbImage = framebuf.FrameBuffer(bufImage, 128, 296, framebuf.MONO_HLSB)
#fb_black.blit(fbImage, 20, 2)
#bufImage = hello_world_light
#fbImage = framebuf.FrameBuffer(bufImage, 128, 296, framebuf.MONO_HLSB)
#fb_black.blit(fbImage, 168, 2)





#fb.fill(white)
#fb.text('Hello World',30,0,black)
#fb.pixel(30, 10, black)
#fb.hline(30, 30, 10, black)
#fb.vline(30, 50, 10, black)
#fb.line(30, 70, 40, 80, black)
#fb.rect(30, 90, 10, 10, black)
#fb.fill_rect(30, 110, 10, 10, black)
#for row in range(0,36):
#	fb.text(str(row),0,row*8,black)
#fb.text('Line 36',0,288,black)
#e.display_frame(buf,buf)

# --------------------



# wrap text inside a box
black = 0
white = 1
# clear
#fb.fill(white)
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


# draw text box 1
# box position and dimensions
print('Box 1')
bx = 8
by = 8
bw = 112 #  = 14 cols
bh = 112 #  = 14 rows (196 chars in total)
text_wrap(str,bx,by,black,bw,bh,black)
#e.display_frame(buf,buf)

# draw text box 2
print('Box 2 & 3')
bx = 0
by = 128
bw = w # 128 = 16 cols
bh = 6 * 8 # 48 = 6 rows (96 chars in total)
text_wrap(str,bx,by,black,bw,bh,black)

# draw text box 3
bx = 0
by = 184
bw = w//2 # 64 = 8 cols
bh = 8 * 8 # 64 = 8 rows (64 chars in total)
text_wrap(str,bx,by,black,bw,bh,None)

fb_black.fill(white)
fb_red.fill(white)
#e.display_frame(buf_black,buf_black)

#adding another font test
from writer import Writer
import out_font

class eink_text_display(framebuf.FrameBuffer):
	def __init__(self, width, height, buffer):
		self.width = width
		self.height = height
		self.buffer = buffer
		self.mode = framebuf.MONO_HLSB
		super().__init__(self.buffer,self.width,self.height, self.mode) #super?!?

	def show(self):
		...
#dev function		
def clear_screen():
	fb_red.fill(white)
	fb_black.fill(white)
	e.display_frame(buf_black, buf_red)

black_text_display = eink_text_display(400, 300, buf_black)
red_text_display = eink_text_display(400,300, buf_red)

writer_black = Writer(black_text_display, out_font)
writer_red = Writer(red_text_display, out_font)

#writer_black.bgcolor = white
#writer_black.fgcolor = black

#writer_red.bgcolor = white
#writer_black.fgcolor = red

#writer_black.set_textpos(black_text_display, 0, 0)
#writer_black.printstring("30°C")
#e.display_frame(buf_black, buf_red)


#test of generating text

def draw_char(fb, x, y, char, c, scale=1):
    char_coords = {
        'A': [(0, 30), (5, 10), (10, 0), (15, 10), (20, 30), (17, 25), (13, 15), (7, 15), (3, 25), (0, 30)],
        'B': [(0, 0), (0, 30), (10, 30), (15, 25), (15, 20), (10, 15), (15, 10), (15, 5), (10, 0), (0, 0)],
        'C': [(20, 0), (0, 0), (0, 30), (20, 30)],
        'D': [(0, 0), (0, 30), (10, 30), (15, 25), (15, 5), (10, 0), (0, 0)],
        'E': [(20, 0), (0, 0), (0, 30), (20, 30), (0, 15), (15, 15)],
        'F': [(20, 0), (0, 0), (0, 30), (20, 30), (0, 15)],
        # Można dodać więcej znaków
    }
    scaled_coords = [(int(xx * scale), int(yy * scale)) for xx, yy in char_coords.get(char, [])]
    
    flat_coords = bytearray()
    for coord in scaled_coords:
        flat_coords.append(coord[0])
        flat_coords.append(coord[1])
        
    fb.poly(x, y, flat_coords, c)

def text(fb, x, y, text, c=1, scale=1):
    char_width = 20 * scale  # Szerokość pojedynczego znaku
    char_height = 30 * scale  # Wysokość pojedynczego znaku
    
    current_x = x
    current_y = y
    
    for char in text:
        if char == '\n':  # Nowa linia
            current_x = x
            current_y += char_height
            continue
        
        draw_char(fb, current_x, current_y, char, c, scale)
        
        current_x += char_width  # Przesunięcie do następnego znaku


#todo - write general function which will handle white/red/black display relation

def dev_color_handling_rect(x, y, width, height, color_name, fill):
    
    if color_name == 'red':
        fb_red.rect(x, y, width, height, red, fill)
		
    if color_name == 'black':
        fb_red.rect(x, y, width, height, white, fill)  # fill red with white - to turn off overlapping
        fb_black.rect(x, y, width, height, black, fill)
		
    if color_name == 'white':
        fb_black.rect(x, y, width, height, white, fill)
        fb_red.rect(x, y, width, height, fill)
    

#text(fb_black, 200, 100, "ABDC", black, scale=2)

#draw a demo cat

#you can always overlay graphic - from simple triangles to something complicated    

#fb_black.ellipse(200,170, 100, 100, black, True) #head
#fb_red.ellipse(200,170, 20, 20, black, True) #nose




    #def blit(self, fbuf, x, y, transparent=False):
     #   for py in range(fbuf.height):
      #      for px in range(fbuf.width):
       #         if not transparent or fbuf.pixel(px, py) != 0:
        #            self.pixel(x + px, y + py, fbuf.pixel(px, py))

    # Other methods can be added similarly

# Example usage:
# black_buf and red_buf are instances of framebuf for black and red colors
# width and height represent the dimensions of the display

from ThreeColorFrameBuffer import ThreeColorFrameBuffer

frame_buffer_eink = ThreeColorFrameBuffer(400, 300, fb_black, fb_red)

#frame_buffer_eink.rect(0,0, 200, 150, "red")