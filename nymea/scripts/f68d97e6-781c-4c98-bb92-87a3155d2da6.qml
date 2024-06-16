import QtQuick 2.0
import nymea 1.0


Item {
    
 //everything has to be inside Item, function declaration etc.
function kWh_gathered (...args) {
    var kWh;
    
    kWh = energy_calculated_jules(...args);
    kWh = kWh/1000;
    kWh = kWh/3600;
    console.log("currentk kWh ",kWh);
    return kWh;
}

function energy_calculated_jules(){
    
    var sum = 0;
    var average = 0;
    var jules = 0;
    
    var water_spec_heat = 4190;
    var lower_temp_margin = 30; 
    var tank_mass = 900;
    
    var better_average = 0;
    
    for (var i = 0; i < arguments.length; i++) {
        average += (arguments[i] - lower_temp_margin)/arguments.length;
    }
    console.log("average", average);
    
  for (var i = 0; i < arguments.length; i++) {
      if (i === 0)  {          
                  better_average += arguments[i]/16;
          } else if ( i ===  (arguments.length - 1)) {
              better_average += arguments[i]/16;
          } else {
                  better_average += arguments[i]/8;
          }
}

    better_average = better_average - lower_temp_margin;
    console.log("better_average", better_average);
    jules = better_average*tank_mass*water_spec_heat;
    return jules;
}
    
 function test_power_from_kWh (previous, actual, timer_interval){
     
     var previous_kWh;
     var actual_kWh = 0;
     var power;
     
     console.log("previous", previous);
     console.log("actual test", actual);
     power = (actual - previous)*(3600*1000)/(timer_interval/1000); //assuming 1s interval xd
     console.log("power", power);
     return power;
 }   
 
 function average(avg, new_sample, N){
     avg -= avg/N;
     avg +=new_sample/N;
     return avg;
 }
 
 //tu niech będą wszelkie thingstate
 
    ThingState {
        id:temp_0
        thingId: "{c6f0aa6a-728a-401e-ab9e-96d4de305179}" // HeatBuffer_Temperature_0
        stateName: "temperature"
        }
    
    ThingState {
        id: temp_1
        thingId: "{698556ca-99dd-455d-8412-546a971a683a}" // HeatBuffer_Temperature_1
        stateName: "temperature"
    }
    
      ThingState {
        id: temp_2
        thingId: "{aae699cb-e109-48fc-a370-ef681980a1f5}" // HeatBuffer_Temperature_2
        stateName: "temperature"
    }
      ThingState {
        id: temp_3
        thingId: "{06393f8a-7e38-439c-818d-b9300278b3ce}" // HeatBuffer_Temperature_3
        stateName: "temperature"
    }
      ThingState {
        id: temp_4
        thingId: "{35daf33b-8004-4eb2-bea9-8406c01ffdc0}" // HeatBuffer_Temperature_4
        stateName: "temperature"
    }
      ThingState {
        id: temp_5
        thingId: "{c19fde1d-fae0-4baf-856f-7d70b369cd64}" // HeatBuffer_Temperature_5
        stateName: "temperature"
    }
    
      ThingState {
        id: temp_6
        thingId: "{817bb84e-e440-4d99-8755-43606ac6cb83}" // HeatBuffer_Temperature_6
        stateName: "temperature"
    }
    
      ThingState {
        id: temp_7
        thingId: "{fe59a2c0-cc2f-4ea6-aaa5-e7a3cc308814}" // HeatBuffer_Temperature_7
        stateName: "temperature"
    }  
    
    ThingState {
        id: temp_8
        thingId: "{3637d208-64dd-453b-8f18-c7338f9ee86d}" // HeatBuffer_Temperature_8
        stateName: "temperature"
    }
    
   ThingState {
       id: solar
       thingId: "{7e038a42-cc88-4679-a3d4-164c969a1012}" // Generic smart meter producer
       stateName: "currentPower"
       
          } 

   
    
    ThingState {
        id: bufor_power
        thingId: "{a9e96bce-dafc-483f-acf8-4ae03d7bd79d}" // Generic energy storage
        stateName: "currentPower"
    //    value: solar.value*-1
    }
    
    ThingState {
        id: bufor_level_percent
        thingId: "{a9e96bce-dafc-483f-acf8-4ae03d7bd79d}" // Generic energy storage
        stateName: "batteryLevel"
       // value: (root.previous_kWh/((60*4190*900)/(3600*1000)))*100 //kiedy to się updatuje? 
    }
    
    ThingState {
        id: bufor_charging
        thingId: "{a9e96bce-dafc-483f-acf8-4ae03d7bd79d}" // Generic energy storage
        stateName: "charging"
    }
    

    
    ThingAction  {
        id: update_buffer_percent
        thingId: "{9f4ed220-252b-4267-a2a0-90427b30361a}" // serial_port
        actionName: "trigger"
    }
    
    ThingAction {
        id: set_buffer_power
        thingId: "{a9e96bce-dafc-483f-acf8-4ae03d7bd79d}" // Bufor ciepła
        actionName: "currentPower"
    }
    
    ThingAction {
        id: set_buffer_charging_state
        thingId: "{a9e96bce-dafc-483f-acf8-4ae03d7bd79d}" // Bufor ciepła
        actionName: "charging"
    }
    
    ThingAction {
        id: buffer_kWh_capacity
        thingId: "{4c0d5eef-736d-455f-950a-405788d3848b}" // Generic energy meter
        actionName: "totalEnergyConsumed"

    }
    
    ThingAction {
        id: averaged_W_hourly
        thingId: "{4c0d5eef-736d-455f-950a-405788d3848b}" // Bufor kWh
        actionName: "currentPower"
    }
// end of thing

    id:root
    
    property int counter: 0
    property var previous_kWh: 0
    property var power: 0
    property int seconds: 0
    property var average_t0: 0
    property var previous_kWh_hourly: 0
    
    property var average_t1: 0
    property var average_t2: 0
    property var average_t3: 0
    property var average_t4: 0
    property var average_t5: 0
    property var average_t6: 0
    property var average_t7: 0
    property var average_t8: 0
    property var sample_number: 10
    property var loop_count: 0
    

    Timer {
        id: onStart
        interval: 10
        repeat: false
        running: true
        onTriggered: {
            root.previous_kWh = kWh_gathered(temp_0.value, temp_1.value, temp_2.value, temp_3.value, temp_4.value, temp_5.value, temp_6.value, temp_7.value, temp_8.value);
            root.previous_kWh_hourly = root.previous_kWh;
        //    solar.value = 0;
        //    bufor_power.value = 0;
             bufor_level_percent.value =   (root.previous_kWh/((60*4190*900)/(3600*1000)))*100;
            update_buffer_percent.execute({"outputData": bufor_level_percent.value + "\n"});
            console.log("onstart");
            buffer_kWh_capacity.execute({"totalEnergyConsumed": root.previous_kWh});
        }
        
    }
    
    
    Timer {
        id:timer
        interval: 1000*60*15
        repeat: true
        running: true // 
        onTriggered: {
            var actual_kWh = kWh_gathered(temp_0.value, temp_1.value, temp_2.value, temp_3.value, temp_4.value, temp_5.value, temp_6.value, temp_7.value, temp_8.value);
        //  var actual_kWh = kWh_gathered(root.average_t0, root.average_t1, root.average_t2, root.average_t3,root.average_t4,root.average_t5,root.average_t6,root.average_t7,root.average_t8);
            root.power = test_power_from_kWh(root.previous_kWh, actual_kWh,timer.interval);
            root.previous_kWh = actual_kWh;
            
            //changing some things
            solar.value = root.power*-1;
            bufor_power.value = solar.value*-1;
            
           buffer_kWh_capacity.execute({"totalEnergyConsumed": actual_kWh});
            
            set_buffer_power.execute({"currentPower": root.power});
            
            if(root.power >= 0) {
                set_buffer_charging_state.execute({"charging": true});
            }
            else {
                set_buffer_charging_state.execute({"charging": false});
            }
            
            bufor_level_percent.value =   (actual_kWh/((60*4190*900)/(3600*1000)))*100; //kiedy to się updatuje? + powywalać te magic numbery
             update_buffer_percent.execute({"outputData": bufor_level_percent.value + "\n"});
            
           
        }
    }
 

    Timer {
        id: debug
        interval: 1000*60*60
        repeat: true
        running: true // 
        onTriggered: {
         
          var actual_kWh = kWh_gathered(temp_0.value, temp_1.value, temp_2.value, temp_3.value, temp_4.value, temp_5.value, temp_6.value, temp_7.value, temp_8.value);
        //  var actual_kWh = kWh_gathered(root.average_t0, root.average_t1, root.average_t2, root.average_t3,root.average_t4,root.average_t5,root.average_t6,root.average_t7,root.average_t8);
          
          var h_power = test_power_from_kWh(root.previous_kWh_hourly, actual_kWh, debug.interval);
          root.previous_kWh_hourly = actual_kWh;
          averaged_W_hourly.execute({"currentPower": h_power});
        }
        
    }
   
}


