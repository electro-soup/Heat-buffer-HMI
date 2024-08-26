from machine import Pin, Timer, PWM, UART
import time
import machine
import json

#pwm0 = PWM(Pin(5), freq=75, duty_u16=32768) # create PWM object from a pin
#pwm1 = PWM(Pin(6), freq= 1000, duty_u16 = 32768)

duty_u16 = 1

high_pulses_75 = 0
low_pulses_75 = 0

total_pulses_75 = 0

high_pulses_1000 = 0
low_pulses_1000 = 0

total_pulses_1000 = 0

pin_75Hz = Pin(1, Pin.IN)
pin_1000Hz = Pin(0, Pin.IN)

# def change_pwm(step_percent):
#         percent_pulses = round(65535/100)
#         duty= pwm0.duty_u16()
#         new_duty = duty + round(percent_pulses * step_percent)
#         if new_duty>65535:
#                 new_duty = 2
#         pwm0.duty_u16(new_duty)
#         pwm1.duty_u16(new_duty)
#         print(f"PWMout duty:f{round(new_duty/65536 * 100)}%")

def timer_callback_75Hz(t):
       global high_pulses_75, total_pulses_75
       high_pulses_75 += pin_75Hz.value()
       total_pulses_75 +=1


def timer_callback_1000Hz(t):
       global high_pulses_1000, total_pulses_1000
       high_pulses_1000 += pin_1000Hz.value()
       total_pulses_1000 +=1

from micropython import const
GPIO_IN_REG = const(0x6000403C)
#adding const to this address changed S/s from 44300 to 46000
from machine import mem8

def timer_callback_1000Hz_direct(t):
       global high_pulses_1000, total_pulses_1000
       high_pulses_1000 += 0x1 & mem8[GPIO_IN_REG]
       total_pulses_1000 +=1

def measure_duty_75(timer, PWM_freq, callback, sleep_time):
     global high_pulses_75, total_pulses_75
     

     timer.init(mode = Timer.PERIODIC, freq = PWM_freq * 200, callback = callback)
     
     time.sleep(sleep_time)
     timer.deinit()
     duty = high_pulses_75/total_pulses_75 * 100
     print(f"freq: {PWM_freq}, duty = {round(duty)}%, high:{high_pulses_75}, total:{total_pulses_75}, fs = {total_pulses_75/sleep_time}S/s")
     high_pulses_75 = 0
     total_pulses_75 = 0
     return duty

def measure_duty_1000(timer, PWM_freq, callback, sleep_time):
     global high_pulses_1000, total_pulses_1000
     

     timer.init(mode = Timer.PERIODIC, freq = PWM_freq * 50, callback = callback)
     print(f"sleep time {sleep_time}")
     time.sleep(sleep_time)
     timer.deinit()
     duty = high_pulses_1000/total_pulses_1000 * 100
     print(f"freq: {PWM_freq}, duty = {round(duty)}%, high:{high_pulses_1000}, total:{total_pulses_1000}, fs = {total_pulses_1000/sleep_time}S/s")
     high_pulses_1000 = 0
     total_pulses_1000 = 0
     return duty
     

sleep_time = 0.1


mqtt_solar_dict = {
       'freq_solar_pump_Hz': 1000,
       'PWM_duty_solar_pump_%': 0,
       'Tech_driver_percent_value':0,
       'freq_feedback_Hz': 75,
       'PWM_duty_feedback_%':0,
       'solar_power_W' : 0,
       'pump_power_W' : 0,
       'pump_state' : "", 
       'pump_gear' : 4
}

def pump_power_and_state(solar_dict):
     
     pump_state = ""
     pump_power = 0
     pump_duty_key = 'PWM_duty_feedback_%'
     pump_duty = solar_dict[pump_duty_key]

     if 0 <= pump_duty <= 70:
          pump_power = pump_power
     #acc do spec - 2% precision
     #value 75% - D - Warning - voltage  below nominal level
     elif 73 <= pump_duty <= 77:
        
        pump_state = "Warning - voltage out of range"
    # value 85% - C - alarm - pump stopped - electronic failure
     elif 83 <= pump_duty <= 87:
    
          pump_state = "Alarm! - pump stopped - electronic failure"
    # 90% - B- alarm - pump stopped - pump is clogged
     elif 88 < pump_duty < 92:
          pump_state = "Alarm! - pump is clogged!"
     # 95% - A - idle
     elif 93 <= pump_duty <= 97:
          pump_state = "idle"
     elif pump_duty > 97:
          pump_state = "off"

     #update dictonary:
     solar_dict['pump_power_W'] = pump_power
     solar_dict['pump_state'] = pump_state


   
# clean.py Test of asynchronous mqtt client with clean session False.
# (C) Copyright Peter Hinch 2017-2022.
# Released under the MIT licence.

# Public brokers https://github.com/mqtt/mqtt.github.io/wiki/public_brokers

# The use of clean_session = False means that during a connection failure
# the broker will queue publications with qos == 1 to the device. When
# connectivity is restored these will be transmitted. If this behaviour is not
# required, use a clean session (clean.py). (MQTT spec section 3.1.2.4).

# red LED: ON == WiFi fail
# blue LED heartbeat: demonstrates scheduler is running.
# Publishes connection statistics.

from mqtt_as import MQTTClient
from mqtt_local import wifi_led, blue_led, config
import uasyncio as asyncio

outages = 0
watchdog = machine.WDT(timeout = 1000 * 60 * 1)
# Demonstrate scheduler is operational.
async def heartbeat():
    s = True
    while True:
        await asyncio.sleep_ms(500)
        blue_led(s)
        s = not s

def sub_cb(topic, msg, retained):
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')

async def wifi_han(state):
    global outages
    wifi_led(not state)
    if state:
        print('WiFi is up.')
    else:
        outages += 1
        print('WiFi is down.')
    await asyncio.sleep(1)
timer = Timer(0)
timer2 = Timer(2)
async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        return
    
    n = 0
    while True:
        watchdog.feed()
        
        
        

        #change_pwm(1)
        #polling timers during loop: first 75Hz wave
        mqtt_solar_dict['duty_feedback_%'] = round( measure_duty_75(timer,75, timer_callback_75Hz,0.4))
        # round(measure_duty_1000(timer2,1000, timer_callback_1000Hz,0.2))
        mqtt_solar_dict['duty_solar_pump_%'] = measure_duty_1000(timer2,1000, timer_callback_1000Hz_direct,0.2 )
        
        pump_power_and_state(mqtt_solar_dict)
        await client.publish('solar_pwm', json.dumps(mqtt_solar_dict), qos = 0)
        await asyncio.sleep(5)
        print('publish', n)
        # If WiFi is down the following will pause for the duration.
        
        n += 1

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['clean'] = False
config['will'] = ('result', 'Goodbye cruel world!', False, 0)
config['keepalive'] = 120
config['response_time'] = 90 

asyncio.create_task(heartbeat())
# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

try:
    asyncio.run(main(client))

finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    asyncio.new_event_loop()