
solar_state_dict = {
    'sun_power_W': 0,
    'PWM_driver_pump_duty_%': 0,
    'pump_power_W': 0,
    'PWM_pump_feedback_%': 0,
    'pump_state': "",

}

mqtt_solarTECH_dict = { #taken from ESP32-C3 which monitors solar driver signal
       'freq_solar_pump_Hz': 1000,
       'PWM_duty_solar_pump_%': 0,
       'TECH_driver_percent_value':0,
       'freq_feedback_Hz': 75,
       'PWM_duty_feedback_%':0,
       'solar_power_W' : 0,
       'pump_power_W' : 0,
       'pump_state' : "", 
       'pump_gear' : 10
}
  
solarTECH_pump_state_description = [ #PWM return from the pump - 75Hz
    {"range":(0, 70),  "code": "E", "state": "The pump is working"},
    {"range":(73, 78), "code": "D", "state": "Warning - pump voltage out of range!"},
    {"range":(83, 88), "code": "C", "state": "Alarm! - pump clogged - electronic failure"},
    {"range":(90, 93), "code": "B", "state": "Alarm! - pump is clogged!"},
    {"range":(93, 97), "code": "A", "state": "Idle"},
    {"range":(97, 100),"code": "_", "state" :"Off"}
]

def update_solar_stats(solar_state_dict, mqqt_solar_source_message):
    ...

def find_pump_state(duty_cycle, state_description):
    
    for state in state_description:
        lower, upper = state["range"]
        if lower < duty_cycle <= upper:
            return state

#tests 

if __name__ == "__main__":
    for duty in range(0, 101, 1):
        print(f'duty: {duty}, state: {find_pump_state(duty, solarTECH_pump_state_description)}')
        
    