import serial
import struct

class DWIN_LCD_Control:
    commands = {}
    commands['dwin'] = 0x5AA5
    commands['set_brigthness'] = 0x82

    def __init__(self, COM_port):
        self.serial =  serial.Serial(COM_port, 115200)

    def _send_data(self, data):
        self.serial.write(data)
        print(", ".join(hex(b) for b in data))

    def _prepare_data_to_send(self, VP_adress, data, commands):
        payload = struct.pack('>HBBHh',commands['dwin'], 0x04, 0x82, VP_adress, int(data)) #todo - different payload handling
        return payload
    
    def set_brigthness(self, brigthness_value):
        data = self._prepare_data_to_send(self.commands['set_brigthness'], int(brigthness_value), self.commands)
        self._send_data(data)

    

class TemperatureItem: 
    def __init__(self, start_VP_adrr, end_VP_adrr, byte_offset, DWIN_LCD_Control):
        self.dwin_command = 0x5AA5
        self.start_address = start_VP_adrr
        self.end_address = end_VP_adrr
        self.byte_offset = byte_offset
        self.elements_count = (self.end_address - self.start_address)/self.byte_offset
        
