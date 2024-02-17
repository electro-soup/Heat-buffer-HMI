import serial
#import paho.mqtt.client as mqtt 
import struct
import time


def interpolate_temperature_data(temperature_list):
     #interpolating temperature data
    extrapolated_list = []
    num_of_intervals_between = 7

    num_of_intervals_between+=1 #to get indeed such interval
            
    for i in range(0, len(temperature_list)-1):
        
        extrapolated_list.append(temperature_list[i]) #append first element from 
        #calculate some values 
        a = temperature_list[i+1]-temperature_list[i]
        b = temperature_list[i]

        for y in range(1,num_of_intervals_between): #1 - to omit calculating existing point x1, - 1 - x2 
            temporary_point = a*(y/num_of_intervals_between)+b
            extrapolated_list.append(int(temporary_point))
                #extrapolated_list.append(0)
        if i == (len(temperature_list)-2):
            extrapolated_list.append(temperature_list[i+1])
    return extrapolated_list

def getTemperatures_from_log(log_line):
    temperatures = []
    if log_line and log_line.strip():
        date, temperatures_csv = log_line.split(',')
        temperatures = temperatures_csv.split(';')
        temperatures = list(filter(None,temperatures))
        temperatures = [float(i) for i in temperatures]
    return temperatures

def direct_write_serial(value, init_adress_ram, ram_offset):
   
       payload = struct.pack('>HBBHh',dwin_command, 0x05, 0x82, init_adress_ram+ram_offset, int(value))
       serial.write(payload)

def write_temperature_list_to_serial_no_proccessing(temperature_list, init_adress_ram):   
 #do some serial writing
    ram_offset = 0

    lower_temp_limit = 20
    for temperature in temperature_list:
        direct_write_serial(temperature, init_adress_ram, ram_offset)
        #print(", ".join(hex(b) for b in payload))
        ram_offset+=2     
def write_to_init_temp_bar(temperature_list, init_adress_ram):
#do some serial writing
    ram_offset = 0
    lower_temp_limit = 30
    upper_temp_limit = 80
    # 0-50 - image set values 
    values_set = [ lower_temp_limit if x<lower_temp_limit else x for x in temperature_list ]
    values_set = [upper_temp_limit if x>upper_temp_limit else x for x in values_set]
    values_set = [x-lower_temp_limit for x in values_set]

    print(values_set) 
    for value in values_set:
        
        direct_write_serial(value, init_adress_ram, ram_offset)
                
        #print(", ".join(hex(b) for b in payload))
        ram_offset+=2

def write_temperature_list_to_serial(temperature_list, init_adress_ram):
    #do some serial writing
    ram_offset = 0
    #there we have a lot to map - 0-70 - 20-90 degrees

    lower_temp_limit = 20
    value_set = [lower_temp_limit if x < lower_temp_limit else x for x in temperature_list]
    value_set = [x-lower_temp_limit for x in value_set]

    for value in value_set:
       
        direct_write_serial(value, init_adress_ram, ram_offset)
                
        #print(", ".join(hex(b) for b in payload))
        ram_offset+=2


def write_log_values_to_serial(file_name):
    
    file = open(file_name, "r")
    text = file.read()
    file_content = text.splitlines()
    
    for line in file_content:
        temperatures = getTemperatures_from_log(line)
        write_to_init_temp_bar(temperatures, 0x3000)
        write_temperature_list_to_serial_no_proccessing(temperatures, 0x2000)
        
        interpolated_temps_list = interpolate_temperature_data(temperatures)    
        write_temperature_list_to_serial(interpolated_temps_list, 0x4000) 
            
        time.sleep(0.0001)
        
serial = serial.Serial("COM11", 115200)


dwin_command  = 0x5AA5
master_init_adress = 0x4000

write_log_values_to_serial("capture.txt")

#while True:
    

serial.close()