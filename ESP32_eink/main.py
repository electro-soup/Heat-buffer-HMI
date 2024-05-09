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

clear_screen()



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
text_wrap(str,bx,by,black,bw,bh,None)

fb_black.fill(white)
fb_red.fill(white)
#e.display_frame(buf_black,buf_black)


#dev function		








from ThreeColorFrameBuffer import ThreeColorFrameBuffer

framebuffer = ThreeColorFrameBuffer(400, 300, fb_black, fb_red)

#frame_buffer_eink.rect(0,0, 200, 150, "red")
width, height = 400, 300

def calculate_max_depth_and_size(width, height, min_size):
    depth = 0
    size = min(width, height)
    while size % 3 == 0 and size // 3 >= min_size:
        size //= 3
        depth += 1
    size *= 3**depth  # Powrót do pełnej wielkości dywanu
    return depth, size

def draw_sierpinski_carpet(framebuffer, x, y, size, depth, max_depth):
    if depth > max_depth or size < 5:
        return

    new_size = size // 3

    # Tylko dwa kolory używane do rysowania kwadratów (biały i czerwony), tło jest czarne
    color = ['red', 'white']
    color_name = color[depth % 2]  # Przełączanie między czerwonym a białym

    # Rysuj środkowy kwadrat
    framebuffer.rect(x + new_size, y + new_size, new_size, new_size, color_name, fill=True)

    if new_size >= 5:
        for i in range(3):
            for j in range(3):
                # Pomiń rysowanie środkowego kwadratu
                if i == 1 and j == 1:
                    continue
                draw_sierpinski_carpet(framebuffer, x + i * new_size, y + j * new_size, new_size, depth + 1, max_depth)

# Ustawienie początkowe całego ekranu na czarne tło
framebuffer.fill('black')

# Obliczanie głębokości rekursji i maksymalnego rozmiaru
max_depth, full_size = calculate_max_depth_and_size(width, height, 5)

# Ustawienie pozycji początkowej, aby dywan był wyśrodkowany
start_x = (width - full_size) // 2
start_y = (height - full_size) // 2


# Rozpocznij rysowanie dywanu
draw_sierpinski_carpet(framebuffer, start_x, start_y, full_size, 5, 7) 
e.display_frame(buf_black,buf_red)

#how to handle arrays 
#import array
#myData = array.array('I', [10,10,120,30,30,61])


