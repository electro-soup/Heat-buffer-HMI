import paho.mqtt.client as mqtt
import json
import struct
import time
import serial
import settings
import DWIN_LCD

dwin_command  = 0x5AA5
master_init_adress = 0x4000

lcd = DWIN_LCD.DWIN_LCD_Control("COM6")
lcd.set_brigthness(50)

def interpolate_temperature_data(temperature_list):
     #interpolating temperature data
    extrapolated_list = []
    num_of_intervals_between = 9

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


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    # Be careful, the reason_code_list is only present in MQTTv5.
    # In MQTTv3 it will always be empty
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")
    client.disconnect()

def on_message(client, userdata, message):
    # userdata is the structure we choose to provide, here it's a list()
    #userdata.append(message.payload)
    temp_dict = json.loads(message.payload)
    temperature_list = []
    for key, value in sorted(temp_dict.items()):
        if 'temp' in key:
            temperature_list.append(value)
    
    write_to_init_temp_bar(temperature_list, 0x3000)
    write_temperature_list_to_serial_no_proccessing(temperature_list, 0x2000)
        
    interpolated_temps_list = interpolate_temperature_data(temperature_list)    
    write_temperature_list_to_serial(interpolated_temps_list, 0x4000)
    
    #write power value
    direct_write_serial(temp_dict['power'], 0x2138, 0) #może tu po prostu sam adres?
    direct_write_serial(temp_dict['load_percent'], 0x2140, 0)
    print(temp_dict)
    



    
    

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("$SYS/#")

#serial = serial.Serial("COM6", 115200)
serial = lcd.serial #nasty way of passing reference to the serial port
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

mqttc.user_data_set([])
mqttc.connect(settings.mqtt_broker_ip)
for topic in settings.mqtt_subscribe_list:
    mqttc.subscribe(topic)
mqttc.loop_forever()
print(f"Received the following message: {mqttc.user_data_get()}")