Project of E-ink display showing all the informations from the heating system (temperatures, solar panel states etc). 
It is based on Raspberry Pi Zero 2W with Nymea system installed, Nymea system gathers all sensors data and send them via MQTT - ESP32 board gets that data and shows them on the e-ink display.

ESP32 board is flashed with MicroPython v1.21.0 from 2023-10-05, newer version have issue with Wi-fi during startup 

Very alpha phase, but something is working ;) It can even do screenshots of GUI and save them as .bmp or .qoi files

Here is progress in GUI development:

![test](https://github.com/user-attachments/assets/1571a8e6-325b-4fea-bb99-c05deeb5f775)

And how screen looks like:
![image](https://github.com/electro-soup/Heat-buffer-HMI/assets/16262155/740319c2-2b96-479b-804f-69a5b0ff3c9d)

```mermaid
flowchart LR
  sensors["1Wire sensors chain"] --> nymea["Nymea system (RPi Zero 2W)"]
  nymea --> intMQTT["internal MQTT broker"]--> nymea
  intMQTT -.-> Network
  Network -.-> ESP32
  ESP32 --> Eink
```
Project consist of couple of elements:
 - ESP32_DWINLCD - first HMI was based on DWIN 7" LCD with touch, driven by ESP32, for now abandoned as I focused on e-ink screen
 - ESP32_eink - currently developed - I am using this screen: https://www.waveshare.com/pico-epaper-4.2-b.htm - red, black and white - picture clarity is very good, but it lacks proper partial refresh and refresh time is very long (15s), but it is ok for displaying temperatures etc.

Ideas to develop:
- wheather display
- getting state of solar panels driver to properly calculate solar power
- measuring temperatures of heating itself
- water pressure sensor in heating installation and also solar system - for fault/leak detection
  

History:

The main problem after upgrading boiler room to 900l water buffer tank and wood boiler was - how to assess how much energy is stored? One termometer was not enough, because it can be very on the top (eg. 80°C) and cold in the middle (30-40°C). 
So I came up with idea I will attach nine DS18B20 sensors directly on the tank with magnets:

![356671924-50bb507e-9171-46c5-b194-4a0811f5c0e84](https://github.com/user-attachments/assets/add8e3f9-1729-4c93-8ffd-9f39b9a04425)

then I connected it to Rapsberry Pi Zero 2W flashed with Nymea system and after some mingling with Javascript I was able to calculate energy stored inside the tank, and also incoming and outgoing power calculating it straight from changes of those temperatures sensors. Nymea does not have proper plugin for such installation, but mimicking with other devices I could finally display some percentage values using eg. battery device: 

<img width="747" alt="image" src="https://github.com/user-attachments/assets/a980475f-5726-44aa-9d32-6614294528cb">



But there was still problem - how to display it somewhere else, not in the mobile app or PC? So I came up with idea, that I will agregate all readings and calculation and send them via MQTT to elsewhere, in this case - ESP32 gathers those data, process and make them visible on eink screen:)
 


