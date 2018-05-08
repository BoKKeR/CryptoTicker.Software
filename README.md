# CryptoTicker.Software
CryptoTicker is an information display board that supports over 1500 coin pairs. The pcb consists of 4 individual 1.3" OLED displays controled by an ESP32. These displays can show a coin pair each. The display outputs are shifted using a multiplexor. Updating or changing the infromation on the fly is possible from the localhost webserver that is running on the device. Vertical and Horizontal positionining is possible. There are 4 programable push-buttons located on the back of the device.
The device can be extendable to support up to 8 displays or with extra multiplexors up to 64 displays.
# About the script
The software is written in [MicroPython](https://micropython.org). MicroPython is a lean and efficient implementation of the Python 3 programming language that includes a small subset of the Python standard library and is optimised to run on microcontrollers and in constrained environments. 
# Firmware
Done firmwares with the script for the ESP32 will be available later.

# Is [coin] supported?
Full list of supported coins can be found at: https://coinmarketcap.com/all/views/all/
# What is missing?
* The localhost webserver needs a remake. 
* The programable buttons need some simple implementation. 
* Custom Fonts are missing. 
* Custom themes are missing. 
* Vertical mode is missing

# Where is the hardware? 
https://github.com/BoKKeR/CryptoTicker.Hardware
