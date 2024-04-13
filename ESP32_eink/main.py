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

# --------------------

# write hello world with black bg and white text
from image_dark import hello_world_dark
from image_light import hello_world_light
print('Image dark')
bufImage = hello_world_dark
fbImage = framebuf.FrameBuffer(bufImage, 128, 296, framebuf.MONO_HLSB)
fb_black.blit(fbImage, 20, 2)
bufImage = hello_world_light
fbImage = framebuf.FrameBuffer(bufImage, 128, 296, framebuf.MONO_HLSB)
fb_black.blit(fbImage, 168, 2)

#e.display_frame(buf,buf) #why there is signle buf?

# --------------------

# write hello world with white bg and black text
print('Image light')
#e.display_frame(hello_world_light)

# --------------------


print('Frame buffer things')
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

# clear
#fb.fill(white)

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
e.display_frame(buf_black,buf_black)

for row in range(0,8):
	fb_black.text("temperatura",200,row*16,black)


e.display_frame(buf_black,None)

for row in range(0,8):
	fb_red.text("temperatura",0,row*16,black)

for row in range(0,8):
	fb_black.text("temperatura",0,row*16,black)

print("diplaying frame")
e.display_frame(buf_black, buf_red)
print("displaying frame end")

#e.sleep()
print("test, 0-1 0-1, PT OFF")
e.partial_refresh(100,200,0,1,0)
# --------------------
print("test, 0-1 0-1, PT ON")
e.partial_refresh(0,100,0,100,1)