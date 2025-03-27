import ubinascii
import network
wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(True)
wlan_mac = wlan_sta.config('mac')
print(wlan_mac)
print(ubinascii.hexlify(wlan_mac).decode())

hex_mac = ubinascii.hexlify(wlan_mac, ':').decode().upper()
print(hex_mac) #pretty XX:XX:XX:XX:XX:XX mac address

print(ubinascii.unhexlify(hex_mac.replace(':',''))) # revert to byte string again