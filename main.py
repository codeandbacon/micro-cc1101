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
        raise Exception('Cannot detect platform')

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

data = bytearray('this is a test')

print(t.cc1101.read(0x02))

t.set_freq(915000000)
t.set_packet_length_conf('INFINITE')
t.set_address_check('NO_ADDR_CHECK')
t.set_modulation_format('ASK')
t.set_data_whitening(0)
t.set_crc_calc(0)
t.set_preamble_bits(8)
t.set_sync_word('1100110011001100')
t.set_qualifier_mode('NO_PRE_SYNC')

# SRES = 0x30
# SFSTXON = 0x31
# SXOFF = 0x32
# SCAL = 0x33
SRX = 0x34
STX = 0x35
# SIDLE = 0x36
# SWOR = 0x38
# SPWD = 0x39
SFRX = 0x3a
SFTX = 0x3b
# SWORRST = 0x3c
# SNOP = 0x3d

def cb(pin):
    print('interrupt value is', gdo0.value())
    marc_state = t.get_marc_state()
    print('marc state is {}'.format(marc_state))
    if marc_state == 'RXFIFO_OVERFLOW':
        print('resetting')
        rb = t.rx_bytes()
        print(rb, ' bytes in the rx queue')
        b = t.rx_fifo(length=rb)
        print(b)
        t.cc1101.strobe(SFRX)
        t.cc1101.strobe(SRX)
    print(t.get_marc_state())

def rec():
    t.rx_fifo()
    st = t.get_marc_state()
    if st == 'RXFIFO_OVERFLOW':
        t.cc1101.strobe(SFRX)
    t.cc1101.strobe(SRX)

def send():
    st = t.get_marc_state()
    if st == 'TXFIFO_UNDERFLOW':
        t.cc1101.strobe(SFTX)
    t.tx_fifo(data)
    t.cc1101.strobe(STX)

if sys.platform == 'esp32':
    print('interrupt')
    t.cc1101.write(IOCFG0, 0x04)
    gdo0.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb)

    t.cc1101.strobe(SRX)