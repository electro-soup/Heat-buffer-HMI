from machine import Pin, Timer, PWM
import time
import machine

pwm0 = PWM(Pin(5), freq=75, duty_u16=32768) # create PWM object from a pin
pwm1 = PWM(Pin(6), freq= 1000, duty_u16 = 32768)

duty_u16 = 1
class PWM_meas():
    def __init__(self, pin, PWM_freq, timer, name = None):
        self.high_pulse_counter = 0
        self.low_pulse_counter = 0
        self.high_pulse_end = 0
        self.counter = 0
        self.PWM_freq = PWM_freq
        self.PWM_sampling = self.PWM_freq * 10
        self.pin = pin
        self.timer = timer
        self.name = name
        self.duty = 0
        self.timer.init(mode = Timer.PERIODIC, freq = self.PWM_sampling, callback = self.timer_cb)
    
    def timer_cb(self, tim):

        if self.pin.value() == 1:
              self.high_pulse_counter += 1
        else:
              self.low_pulse_counter +=1 
        self.counter += 1

        if self.counter > self.PWM_sampling - 1:
             self.high_pulse_end = self.high_pulse_counter
             self.counter = 0
             self.low_pulse_counter = 0
             self.high_pulse_counter = 0

    def get_duty(self):
         self.duty = self.high_pulse_end/self.PWM_sampling * 100
         print(self.duty)
         
    def debug(self):
         self.duty = self.high_pulse_end/self.PWM_sampling * 100
         print(f'name:{self.name}, timer:{self.timer},duty: {self.duty}%, counter: {self.counter}, high pulses: {self.high_pulse_counter}, low:{self.low_pulse_counter}')
#only 0 and 2 timers are working - 1 does nothin, 3 causes panick
test_feedback = PWM_meas(Pin(1, Pin.IN), 75, Timer(0), "feedback z pompy")
test_pompa = PWM_meas(Pin(0, Pin.IN),1000,Timer(2),"pwm do pompy")
while True:
        time.sleep(0.9)
        state = machine.disable_irq()
        test_feedback.debug()
        
        test_pompa.debug()
        pwm0.duty_u16(duty_u16)
        pwm1.duty_u16(duty_u16)
        duty_u16 += 1200
        if duty_u16 > 65000:
             duty_u16 = 1
        machine.enable_irq(state)