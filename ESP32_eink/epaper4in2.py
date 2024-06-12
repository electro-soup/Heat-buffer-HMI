"""
MicroPython Waveshare 4.2" Black/White/Red GDEW042Z15 e-paper display driver
https://github.com/mcauser/micropython-waveshare-epaper

MIT License
Copyright (c) 2017 Waveshare
Copyright (c) 2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# also works for black/white/yellow GDEW042C37?

from micropython import const
from time import sleep_ms

# Display resolution
EPD_WIDTH  = const(400)
EPD_HEIGHT = const(300)

# Display commands
PANEL_SETTING                  = const(0x00)
#POWER_SETTING                  = const(0x01)
POWER_OFF                      = const(0x02)
#POWER_OFF_SEQUENCE_SETTING     = const(0x03)
POWER_ON                       = const(0x04)
#POWER_ON_MEASURE               = const(0x05)
BOOSTER_SOFT_START             = const(0x06)
DEEP_SLEEP                     = const(0x07)
DATA_START_TRANSMISSION_1      = const(0x10)
#DATA_STOP                      = const(0x11)
DISPLAY_REFRESH                = const(0x12)
DATA_START_TRANSMISSION_2      = const(0x13)
#VCOM_LUT                       = const(0x20)
#W2W_LUT                        = const(0x21)
#B2W_LUT                        = const(0x22)
#W2B_LUT                        = const(0x23)
#B2B_LUT                        = const(0x24)
#PLL_CONTROL                    = const(0x30)
#TEMPERATURE_SENSOR_CALIBRATION = const(0x40)
#TEMPERATURE_SENSOR_SELECTION   = const(0x41)
#TEMPERATURE_SENSOR_WRITE       = const(0x42)
#TEMPERATURE_SENSOR_READ        = const(0x43)
VCOM_AND_DATA_INTERVAL_SETTING = const(0x50)
#LOW_POWER_DETECTION            = const(0x51)
#TCON_SETTING                   = const(0x60)
#RESOLUTION_SETTING             = const(0x61)
#GSST_SETTING                   = const(0x65)
GET_STATUS                     = const(0x71)
#AUTO_MEASURE_VCOM              = const(0x80)
#VCOM_VALUE                     = const(0x81)
#VCM_DC_SETTING                 = const(0x82)
PARTIAL_WINDOW                 = const(0x90)
PARTIAL_IN                     = const(0x91)
PARTIAL_OUT                    = const(0x92)
#PROGRAM_MODE                   = const(0xA0)
#ACTIVE_PROGRAM                 = const(0xA1)
#READ_OTP_DATA                  = const(0xA2)
#POWER_SAVING                   = const(0xE3)

BUSY = const(0)  # 0=busy, 1=idle

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def _command(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def init(self):
        self.reset()
        self._command(BOOSTER_SOFT_START, b'\x17\x17\x17') # 07 0f 17 1f 27 2F 37 2f #? is it needed?
        self._command(POWER_ON)
        self.wait_until_idle()
        self._command(PANEL_SETTING, b'\x0F') # LUT from OTP
        self.wait_until_idle()
        self._command(VCOM_AND_DATA_INTERVAL_SETTING, b'\xF7') #set floating border (no border flickering) and correct LUT for colors
        self.wait_until_idle()
        
    def wait_until_idle(self):
        while self.busy.value() == BUSY:
            sleep_ms(100)
            self._command(GET_STATUS)

    def reset(self): #it was changed
        self.rst(1)
        sleep_ms(200)
        self.rst(0)
        sleep_ms(2)
        self.rst(1)
        sleep_ms(200)

    def send_buffer(self, frame_buffer_black, frame_buffer_red):
        if (frame_buffer_black != None):
            self._command(DATA_START_TRANSMISSION_1)
            sleep_ms(2)
            for i in range(0, self.width * self.height // 8):
                self._data(bytearray([frame_buffer_black[i]]))
            sleep_ms(2)
        if (frame_buffer_red != None):
            self._command(DATA_START_TRANSMISSION_2)
            sleep_ms(2)
            for i in range(0, self.width * self.height // 8):
                self._data(bytearray([frame_buffer_red[i]]))
            sleep_ms(2)
    # draw the current frame memory
    def display_frame(self, frame_buffer_black, frame_buffer_red):
        self.send_buffer(frame_buffer_black, frame_buffer_red) 
        self._command(DISPLAY_REFRESH)
        self.wait_until_idle()

    # to wake call reset() or init()
    def sleep(self):
        self._command(VCOM_AND_DATA_INTERVAL_SETTING, b'\xF7') # border floating
        self._command(POWER_OFF)
        self.wait_until_idle()
        self._command(DEEP_SLEEP, b'\xA5') # check code
    
    def partial_refresh(self, horizontal_bank_start, horizontal_bank_stop, vertical_bank_start, vertical_bank_stop, PT_SCAN_ON_OFF):
        self._command(PARTIAL_IN) #enter partial refresh
        self.wait_until_idle()
       # self._command(PARTIAL_WINDOW)
       

        def bytearray_to_bytes(byte_array):
            return bytes([byte for byte in byte_array])

        byte_0 = (horizontal_bank_start // 0xFF) & 0x01 
        byte_1 = (horizontal_bank_start % 0xFF)  & 0xF8
        byte_2 = (horizontal_bank_stop // 0xFF)  & 0x01 
        byte_3 = (horizontal_bank_stop % 0xFF)   | 0x07
        byte_4 = (vertical_bank_start // 0xFF) & 0x01
        byte_5 = vertical_bank_start % 0xFF 
        byte_6 = (vertical_bank_stop // 0xFF) & 0x1
        byte_7 = vertical_bank_stop % 0xFF 
        byte_8 = PT_SCAN_ON_OFF 
        
        print(f"byte_7 {byte_7}" )
        data_to_send = bytearray([byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8])
        self._command(PARTIAL_WINDOW, bytearray_to_bytes(data_to_send))
        print(bytearray_to_bytes(data_to_send))
        self.wait_until_idle()
        sleep_ms(2)
        self._command(DISPLAY_REFRESH)
        self.wait_until_idle()
        self._command(PARTIAL_OUT)
        self.wait_until_idle()
    
    def wake_up(self):
        self.reset()
        self.init()
    
    #DDX[1:0] - 11 for proper red and black
    #VDB - border color - 00 - black, 01 - LUTW, 10 LUTR, 11 Floating - floating gets best result, no flashing border
    def VCOM_CDI_settings(self, VBD, CDInterval):
         
        def bytearray_to_bytes(byte_array):
            return bytes([byte for byte in byte_array])
    
        default = 0xF7
        byte_0 = default
    
         # Ustawienie bitów dla VBD (bity 7 i 8)
        VBD_bits = VBD & 0x03  # Upewnij się, że VBD ma maksymalnie 2 bity
        byte_0 &= ~(0x03 << 6)  # Wyczyść bity 7 i 8
        byte_0 |= (VBD_bits << 6)  # Ustaw nowe wartości
    
        # Ustawienie bitów dla CDInterval (bity od 1 do 4)
        CDInterval_bits = CDInterval & 0x0F  # Upewnij się, że CDInterval ma maksymalnie 4 bity
        byte_0 &= ~(0x0F << 0)  # Wyczyść bity od 1 do 4
        byte_0 |= (CDInterval_bits << 0)  # Ustaw nowe wartości
    
        data_to_send = bytearray([byte_0])
        print(data_to_send)
        self._command(VCOM_AND_DATA_INTERVAL_SETTING, bytearray_to_bytes(data_to_send))
        print(bytearray_to_bytes(data_to_send))
        self.wait_until_idle()
    
    