import QtQuick 2.0
import nymea 1.0

Item {
    
    
    ThingEvent {
        thingId: "{f3b6c93f-1f01-4bf1-b593-08e3a7484f90}" // MQTT Łazienka
        eventName: "triggered"
        onTriggered: {
           
            console.log("recieved:", JSON.stringify(params))
            console.log("data dield", params["data"])
            console.log("parsed data", JSON.stringify(params["data"]))
          var temp =  JSON.parse(params["data"])
          // temp1.value = (1.0 * temp["tempc"]  + 20) / 70
          temp1.value = temp["tempc"]
          hum1.value = temp["hum"]
            console.log("params", temp["tempc"])
        }
    }
    
    ThingState {
        id: temp1
        thingId: "{38dc46c2-ec7f-4a4a-8118-1979208c0b0e}" // Temperatura Łazienka
        stateName: "temperature"
    }
    
    ThingState {
        id: hum1
        thingId: "{82223135-21c4-4fe1-94d9-9689b74e4881}" // Wilgotność Łazienka
        stateName: "humidity"
    }
    
      ThingEvent {
        thingId: "{6b13259b-3603-4012-8fff-328e711f11fa}" // MQTT Kuchnia 1
        eventName: "triggered"
        onTriggered: {
           
          console.log("recieved:", JSON.stringify(params))  
          console.log("parsed data", JSON.stringify(params["data"]))
          var temp =  JSON.parse(params["data"])
      
          temp2.value = temp["tempc"]
          hum2.value = temp["hum"]
          
        }
    }
    
    ThingState {
        id: temp2
        thingId: "{67f0a067-9198-4429-af8d-87adf4f01359}" // Temperatura Kuchnia mama
        stateName: "temperature"
    }
    
    ThingState {
        id: hum2
        thingId: "{0dc9a853-3ec5-406f-9d46-207d70ad3baf}" // Wilgotność kuchnia mama
        stateName: "humidity"
    }
    
    
        ThingEvent {
        thingId: "{4c7e19a5-7cba-498d-a318-c6ce3197f8a2}" // MQTT Pokój 1
        eventName: "triggered"
        onTriggered: {
           
          console.log("recieved:", JSON.stringify(params))  
          console.log("parsed data", JSON.stringify(params["data"]))
          var temp =  JSON.parse(params["data"])
      
          temp3.value = temp["tempc"]
          hum3.value = temp["hum"]
          
        }
    }
    
    ThingState {
        id: temp3
        thingId: "{ea11426d-d911-44e4-970c-7c72a69743b7}" // Temperatura Pokój 1
        stateName: "temperature"
    }
    
    ThingState {
        id: hum3
        thingId: "{3937f2be-1541-4478-b6b8-30427ff7c980}" // Wilgotność Pokój 1
        stateName: "humidity"
    }
    
    
       ThingEvent {
        thingId: "{f2cdb31b-9740-4ff0-9f83-4c0c28201507}" // MQTT Czujka 1
        eventName: "triggered"
        onTriggered: {
           
          console.log("recieved:", JSON.stringify(params))  
          console.log("parsed data", JSON.stringify(params["data"]))
          var temp =  JSON.parse(params["data"])
      
          temp4.value = temp["tempc"]
          hum4.value = temp["hum"]
          
        }
    }
    
    ThingState {
        id: temp4
        thingId: "{fd131e96-0001-4a15-b707-33ff415d8253}" // Temperatura czujka 1
        stateName: "temperature"
    }
    
    ThingState {
        id: hum4
        thingId: "{7f9de90c-aae0-470c-9973-6c7d09aa2e05}" // Wilgotność czujka 1
        stateName: "humidity"
    }
    
       ThingEvent {
        thingId: "{56463691-e003-41f9-b880-ba2cecb5ce4c}" // MQTT Kuchnia 2
        eventName: "triggered"
        onTriggered: {
           
          console.log("recieved:", JSON.stringify(params))  
          console.log("parsed data", JSON.stringify(params["data"]))
          var temp =  JSON.parse(params["data"])
      
          temp5.value = temp["tempc"]
          hum5.value = temp["hum"]
          
        }
    }
    
    ThingState {
        id: temp5
        thingId: "{0a15ce5c-ffb3-4440-9f08-09639816cd58}" // Temperatura kuchnia 2
        stateName: "temperature"
    }
    
    ThingState {
        id: hum5
        thingId: "{665f42be-ff35-47cd-9da0-5a490aa6c434}" // Wilgotność kuchnia 2
        stateName: "humidity"
    }
    
}
