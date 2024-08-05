Project of E-ink display showing all the informations from the heating system (temperatures, solar panel states etc). 
It is based on Raspberry Pi Zero 2W with Nymea system installed, Nymea system gathers all sensors data and send them via MQTT - ESP32 board gets that data and shows them on the e-ink display.

```mermaid
flowchart LR
  sensors["1Wire sensors chain"] --> nymea["Nymea system (RPi Zero 2W)"]
  nymea --> intMQTT["internal MQTT broker"]--> nymea
  intMQTT -.-> Network
  Network -.-> ESP32
  ESP32 --> Eink
```

Very alpha phase, but something is working ;)


![image](https://github.com/electro-soup/Heat-buffer-HMI/assets/16262155/740319c2-2b96-479b-804f-69a5b0ff3c9d)
