from machine import Pin, Timer, PWM
import time
import machine

pwm0 = PWM(Pin(5), freq=75, duty_u16=32768) # create PWM object from a pin
pwm1 = PWM(Pin(6), freq= 1000, duty_u16 = 32768)

duty_u16 = 1

high_pulses_75 = 0
low_pulses_75 = 0
high_pulses_end_75 = 0
total_pulses_75 = 0
total_pulses_end_75 = 0
high_pulses_1000 = 0
low_pulses_1000 = 0
high_pulses_end_1000 = 0
total_pulses_1000 = 0
total_pulses_end_1000 = 0
pin_75Hz = Pin(1, Pin.IN)
pin_1000Hz = Pin(0, Pin.IN)

def change_pwm(step_percent):
        percent_pulses = round(65535/100)
        duty= pwm0.duty_u16()
        new_duty = duty + round(percent_pulses * step_percent)
        if new_duty>65535:
                new_duty = 2
        pwm0.duty_u16(new_duty)
        pwm1.duty_u16(new_duty)
        print(f"PWMout duty:f{new_duty/65536 * 100}%")

def timer_callback_75Hz(t):
       global high_pulses_75, total_pulses_75
       high_pulses_75 += pin_75Hz.value()
       total_pulses_75 +=1
   
def timer_callback_1000Hz(t):
       global high_pulses_1000, total_pulses_1000
       high_pulses_1000 += pin_1000Hz.value()
       total_pulses_1000 +=1
       


def measure_duty_75(timer, PWM_freq, callback, sleep_time):
     global high_pulses_75, total_pulses_75
     

     timer.init(mode = Timer.PERIODIC, freq = PWM_freq * 200, callback = callback)
     
     time.sleep(sleep_time)
     timer.deinit()
     duty = high_pulses_75/total_pulses_75 * 100
     print(f"freq: {PWM_freq}, duty = {duty}%, high:{high_pulses_75}, total:{total_pulses_75}, fs = {total_pulses_75/sleep_time}S/s")
     high_pulses_75 = 0
     total_pulses_75 = 0

def measure_duty_1000(timer, PWM_freq, callback, sleep_time):
     global high_pulses_1000, total_pulses_1000
     

     timer.init(mode = Timer.PERIODIC, freq = PWM_freq * 50, callback = callback)
     print(f"sleep time {sleep_time}")
     time.sleep(sleep_time)
     timer.deinit()
     duty = high_pulses_1000/total_pulses_1000 * 100
     print(f"freq: {PWM_freq}, duty = {duty}%, high:{high_pulses_1000}, total:{total_pulses_1000}, fs = {total_pulses_1000/sleep_time}S/s")
     high_pulses_1000 = 0
     total_pulses_1000 = 0
     

sleep_time = 0.1
while True:
        time.sleep(0.9)
        timer = Timer(0)
        timer2 = Timer(2)

        change_pwm(1)
        #polling timers during loop: first 75Hz wave
        measure_duty_75(timer,75, timer_callback_75Hz,0.4)
        measure_duty_1000(timer2,1000, timer_callback_1000Hz,0.2)
        print('\n')
        
        
