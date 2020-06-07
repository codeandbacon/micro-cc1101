import sys
from machine import Pin, SPI
from cc1101 import CC1101
from configuration import *

def init_spi():
    chip = sys.platform
    if chip == 'esp32':
        return SPI(1, baudrate=5000000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    elif chip == 'esp8266':
        return SPI(1, baudrate=5000000, polarity=1, phase=1)
    else:
        raise Exception('')

if sys.platform == 'esp32':
    cs = Pin(17, Pin.OUT)
    gdo0 = Pin(4, Pin.IN)
    gdo2 = Pin(16, Pin.IN)
else:
    cs = Pin(15, Pin.OUT)
    gdo0 = Pin(4, Pin.IN)
    gdo2 = Pin(5, Pin.IN)

spi = init_spi()

t = CC1101(spi, cs, gdo0=gdo0, gdo2=gdo2)

from conf import conf

for k, v in list(conf.items()):
    addr = locals()[k]
    t.cc1101.write(addr, v)

# data = bytearray('this is a test, qwerty123456')
data = bytearray([1,2,3,4,5,6,7,8,9,10])

# if sys.platform == 'esp32':
#     pass
#     # for i in range(200):
#     #     pass
# else:
#     for i in range(1):
#         st = t.get_marc_state()
#         if st == 'TXFIFO_UNDERFLOW':
#             t.cc1101.strobe(SFTX)
#         t.tx_fifo(data)
#         t.cc1101.strobe(STX)
#         sleep(1)

t.set_address_check('NO_ADDR_CHECK')
t.set_modulation_format('2FSK')
t.set_preamble_bits(8)
t.set_sync_word('110011001100110')
t.cc1101.write(IOCFG0, 0x06)

# # def cb(pin):
# #     marc_state = t.get_marc_state()
# #     print('marc state is {}'.format(marc_state))

def rec():
    t.rx_fifo()
    st = t.get_marc_state()
    if st == 'RXFIFO_UNDERFLOW':
        t.cc1101.strobe(SFRX)
    t.cc1101.strobe(SRX)

def send():
    st = t.get_marc_state()
    if st == 'TXFIFO_UNDERFLOW':
        t.cc1101.strobe(SFTX)
    t.tx_fifo(data)
    t.cc1101.strobe(STX)

# if sys.platform == 'esp32':
#     gdo0.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb)