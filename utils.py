
class TemperatureItem: 
    def __init__(self, start_VP_adrr, end_VP_adrr, byte_offset):
        self.start_address = start_VP_adrr
        self.end_address = end_VP_adrr
        self.byte_offset = byte_offset
        self.elements_count = (self.end_address - self.start_address)/self.byte_offset
