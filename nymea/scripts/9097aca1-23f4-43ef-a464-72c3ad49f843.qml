import QtQuick 2.0
import nymea 1.0

Item {
    
    ThingAction {
        id:mqtt_bufor_temperatures
        thingId: "{f2cdb31b-9740-4ff0-9f83-4c0c28201507}" // MQTT Czujka 1
        actionName: "trigger"
     }
    
  Things {
  id:myThings
  }
  
  // things setups, to get access to particular values
  
  ThingState {
      id: bufor_temp0
      thingId: "{c6f0aa6a-728a-401e-ab9e-96d4de305179}" // HeatBuffer_Temperature_0
      stateName: "temperature"
  }
  
    ThingState {
      id: bufor_temp1
      thingId: "{698556ca-99dd-455d-8412-546a971a683a}" // HeatBuffer_Temperature_1
      stateName: "temperature"
  }
  
  ThingState {
      id: bufor_temp2
      thingId: "{aae699cb-e109-48fc-a370-ef681980a1f5}" // HeatBuffer_Temperature_2
      stateName: "temperature"
  }
  
  ThingState {
      id: bufor_temp3
      thingId: "{06393f8a-7e38-439c-818d-b9300278b3ce}" // HeatBuffer_Temperature_3
      stateName: "temperature"
  }
  
  ThingState {
      id: bufor_temp4
      thingId: "{35daf33b-8004-4eb2-bea9-8406c01ffdc0}" // HeatBuffer_Temperature_4
      stateName: "temperature"
  }
  
  ThingState {
      id: bufor_temp5
      thingId: "{c19fde1d-fae0-4baf-856f-7d70b369cd64}" // HeatBuffer_Temperature_5
      stateName: "temperature"
  }
  
  ThingState {
      id: bufor_temp6
      thingId: "{817bb84e-e440-4d99-8755-43606ac6cb83}" // HeatBuffer_Temperature_6
      stateName: "temperature"
  }
  
  ThingState {
      id: bufor_temp7
      thingId: "{fe59a2c0-cc2f-4ea6-aaa5-e7a3cc308814}" // HeatBuffer_Temperature_7
      stateName: "temperature"
  }
  
  ThingState {
      id: bufor_temp8
      thingId: "{3637d208-64dd-453b-8f18-c7338f9ee86d}" // HeatBuffer_Temperature_8
      stateName: "temperature"
  }
  
  ThingState {
      id:bufor_load_percent
      thingId: "{a9e96bce-dafc-483f-acf8-4ae03d7bd79d}" // Bufor ciepła
      stateName: "batteryLevel"
  }
  
  ThingState {
      id:bufor_kWh_load
      thingId: "{4c0d5eef-736d-455f-950a-405788d3848b}" // Bufor kWh
      stateName: "totalEnergyConsumed"
  }
 
 ThingState {
     id: bufor_power
     thingId: "{7e038a42-cc88-4679-a3d4-164c969a1012}" // Panele słoneczne
     stateName: "currentPower"
 }
 
 
 ThingState {
     id: solar_temp1
     thingId: "{e1ae2205-c449-4b7b-9426-1fa41ef0d074}" // Solar_T1
     stateName: "temperature"
 }
 
 ThingState {
     id: solar_temp2
     thingId: "{838d808c-05ea-4b54-87aa-49a34681a90b}" // Gen_T_Sensor_1
     stateName: "temperature"
 }
//InterfaceState {
 //   interfaceName: "temperaturesensor"
  //  onStateChanged: {console.log("Battery level changed to", value, "for", myThings.getThing(thingId).name)
   // mqtt_bufor_temperatures.execute({"topic": "homePoręba/"+ myThings.getThing(thingId).name , "data": "{temp =" + value + "}", "qos": 0, "retain": false}) 
  // }    
//}
   
   
  
    //time control and triggerring
    
 
      Timer {
        id: mqtt_sender
        interval: 1000*30
        repeat: true
        running: true
        onTriggered:{
            var mqtt_topic = "home/kotlownia/bufor"
            var mqtt_data = ""
            mqtt_data = JSON.stringify({id: "bufor", temp0: bufor_temp0.value, temp1: bufor_temp1.value, temp2: bufor_temp2.value, temp3: bufor_temp3.value, temp4: bufor_temp4.value, temp5: bufor_temp5.value, temp6: bufor_temp6.value, temp7: bufor_temp7.value, temp8: bufor_temp8.value,
             load_percent: bufor_load_percent.value, kWh: bufor_kWh_load.value, power: -1*bufor_power.value, solar_temp1: solar_temp1.value, solar_temp2:solar_temp2.value})
            console.log(mqtt_topic, mqtt_data)
            mqtt_bufor_temperatures.execute({"topic": mqtt_topic, "data": mqtt_data, "qos": 0, "retain": false})
            
        }
        
    }
    
    
}
