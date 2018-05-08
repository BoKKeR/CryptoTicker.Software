from machine import Pin, I2C
import machine
import sh1106
import urequests
import time
import LCD_font11p
from writer import Writer
import network
import urllib
import ujson
#import webserver
import btree
holder = {}
displays = []

global error_logging_server
error_logging_server = "http://10.0.0.168/esp32/index.php"

sta_if = network.WLAN(network.STA_IF)
i2c = I2C(scl=Pin(22), sda=Pin(23), freq=400000)
multiplexer_addr = 0x70

class SMBusEmulator:
    __slots__ = ('i2c',)
    def __init__(self, scl_pinno=22, sda_pinno=23):
        self.i2c = I2C(scl=Pin(scl_pinno, Pin.IN),
                       sda=Pin(sda_pinno, Pin.IN))

    def write_byte_data(self, addr, cmd, val):
        buf = bytes([cmd, val])
        self.i2c.writeto(addr, buf)

    def read_word_data(self, addr, cmd):
        assert cmd < 256
        buf = bytes([cmd])
        self.i2c.writeto(addr, buf)
        data = self.i2c.readfrom(addr, 4)
        return _bytes_to_int(data)
"""
Multiplexer
Switches between I2C channels 0-7 
Each channel can have one display of the same I2C address (0x3c for 1.3" oled-s)
"""
class multiplexer():
    def __init__(self):
        self.bus = SMBusEmulator()
        
    def change_channel(self, channel):  
    
        if   (channel==0): action = 0x01
        elif (channel==1): action = 0x02
        elif (channel==2): action = 0x04
        elif (channel==3): action = 0x08
        elif (channel==4): action = 0x10
        elif (channel==5): action = 0x20
        elif (channel==6): action = 0x40
        elif (channel==7): action = 0x80
        else : action = 0x00

        self.bus.write_byte_data(multiplexer_addr,0x04,action)  #0x04 is the register for switching channels 
        
    def scanner(self): 
        display_a = {}   #Left for PCB testing

        multiplexer_channel = 0
        while multiplexer_channel != 8:
            
            self.change_channel(multiplexer_channel)
            channel = multiplexer_channel

            try:
                disp = sh1106.SH1106_I2C(128, 64, i2c, None, 0x3c)
                state = 1
            except Exception:
                state = 0
            global displays
            displays.append(Xdisplay(channel, state))    
            display_a.update({multiplexer_channel : state})   #Left for PCB testing
            multiplexer_channel += 1 
          
        print(display_a)
        return display_a
        
class oled():
    #Initalizes and saves all the displays that are available.
    def __init__(self, orientation=0):
        for display in displays:
            if  display.state == 1:
                multiplex.change_channel(display.channel)
                display.driver = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)
                
    def clear(self, display_number):
        display[display_number].clear()
    
    def draw_image(self, coin, display_number):
        if 1 == 1:
            self.draw_landscape(coin, display_number)
        else:
            self.draw_portrait(coin, display_number)
            
    def draw_portrait(self):
        print("")
        
    def ticker_display(self , coin, currency, channel):
        
        multiplex.change_channel(channel)

        global priceM
        priceM = price()
        priceM.fetch_coin(coin, currency, channel)
        print("updated " + coin + " on display: " + str(channel))
    """    
    count out the font size - the width of the 
    display to place the string in the right corner.
    """
    def calculate_corner_position(self, string):
        corner_position = 128 - int(wri_serif.getsize(string))
        return corner_position
        
    def calculate_middle_position(self, string):
        corner_position = (128 - int(wri_serif.getsize(string))) // 2
        
        return corner_position    
        
    def draw_landscape(self, coin, display_number):

        wri_serif = Writer(displays[display_number].driver, LCD_font11p)
        Writer.set_clip(True, True)

        displays[display_number].driver.fill(0)
        displays[display_number].driver.line(0, 25, 128, 26, 1) #horizontal
        displays[display_number].driver.line(0, 26, 128, 25, 1) #horizontal

        #displays[display_number].driver.fill_rect(0, 0, 30, 10, 1)

        wri_serif.printstring(holder[coin].symbol, 3, 1) 

        if holder[coin].display_currency == "USD":
            wri_serif.printstring(holder[coin].price_usd, self.calculate_middle_position(holder[coin].price_usd) , 30)
        else:

            wri_serif.printstring(holder[coin].price_btc,  self.calculate_middle_position(holder[coin].price_btc), 30)
        
        wri_serif.printstring(holder[coin].percent_change_24h, self.calculate_corner_position(holder[coin].percent_change_24h), 1)        
        
        displays[display_number].driver.show()
        
    def show_ip():
        for display in displays:
            if  display.state == 1:

                multiplex.change_channel(display.channel)

                display.driver.fill(0)
                display.driver.text(str(sta_if.ifconfig()[0]), 3, 0, 1)
                display.driver.text(str(sta_if.ifconfig()[1]), 3, 15, 1)
                display.driver.text(str(sta_if.ifconfig()[2]), 3, 30, 1)
                display.driver.text(str(sta_if.ifconfig()[3]), 3, 45, 1)
                
                display.driver.show()

        time.sleep(6)
        
class Coin:
    def __init__(self,name=None, symbol=None, price_btc=None, price_usd=None, percent_change_24h=None, display_currency=None,  **kwargs):
        self.name = name
        self.symbol = symbol
        self.price_btc = price_btc
        self.price_usd = price_usd
        self.percent_change_24h = percent_change_24h
        self.display_currency = display_currency

class Xdisplay:
    def __init__(self, channel=None, state=None, driver=None,  **kwargs):
        self.channel = channel
        self.state = state
        self.driver = driver
            
class price():

    def fetch_coin(self, coin, currency, display_number):
        
        url = "https://api.coinmarketcap.com/v1/ticker/" + coin + "/"
        try:
            ticker_json = urequests.get(url).json()
            price_btc = ticker_json[0]['price_btc']
            symbol = ticker_json[0]['symbol']
            price_usd = ticker_json[0]['price_usd']
            percent_change_24h = ticker_json[0]['percent_change_24h']
            display_currency = currency
            name = coin

            global holder

            holder[coin] = Coin(name, symbol, price_btc, price_usd, percent_change_24h, display_currency)

            self.format_data(coin, display_number)

        except Exception as e:
            d.error_logging(e)
            pass
            
    def format_data(self, coin, display_number):

        if holder[coin].percent_change_24h[0] != "-":
            holder[coin].percent_change_24h = "+" + holder[coin].percent_change_24h
        
        holder[coin].percent_change_24h = str(holder[coin].percent_change_24h) + "%"
        
        holder[coin].price_usd = str(holder[coin].price_usd) + "$"
        
        oled_display.draw_image(coin, display_number)

class data():
    def error_logging(self, error):
        data = {'error': str(error) ,'ip': str(sta_if.ifconfig()[0])}
        data_json = ujson.dumps(data).encode()
        r = urequests.get(error_logging_server, data=data_json)

multiplex = multiplexer()
available_displays = multiplex.scanner()
#while True:
#    available_displays = multiplex.scanner()    #Left for PCB testing     
#    time.sleep(1) 
                
oled_display = oled()

# ↓ needs rework ↓
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)
wri_serif = Writer(display, LCD_font11p)
# ↑ needs rework ↑

def callback0(p): 
    print('pin change', p)
    d.error_logging("test_button")
    
def callback1(p):
    print('pin change', p)
    oled.show_ip()
    
def callback2(p):
    print('pin change', p)
    
def callback3(p):
    print('pin change', p)
    machine.reset()

led=Pin(5,Pin.OUT)
global d
d = data()

global priceM
priceM = price()

button0 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
button1 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP)

button0.irq(trigger=Pin.IRQ_FALLING, handler=callback0)
button1.irq(trigger=Pin.IRQ_FALLING, handler=callback1)
button2.irq(trigger=Pin.IRQ_FALLING, handler=callback2)
button3.irq(trigger=Pin.IRQ_FALLING, handler=callback3)

f = open("settings", "r+b")

while True:
    db = btree.open(f)

    led.value(1)
    oled_display.ticker_display(db[b"display0"].decode("utf-8"), "USD", 1)
    led.value(0)
    time.sleep(1)
    led.value(1)
    oled_display.ticker_display(db[b"display1"].decode("utf-8"),"BTC", 4)
    led.value(0)

    time.sleep(5)

    db.close()