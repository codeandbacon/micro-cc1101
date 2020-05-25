import sys
from machine import Pin, SPI
from status import *
from configuration import *
from strobes import *
from time import sleep
from cc1101 import CC1101
from resp import read_resp

BITS_F = '{0:08b}'

PATABLE = 0x3e
FIFO = 0x3f

SINGLE_WRITE = 0x00
BURST_WRITE = 0x40
SINGLE_READ = 0x80
BURST_READ = 0xc0

ENDIAN = 'big'

NORMAL = 0
SYNC = 1
RANDOM = 2
ASYNC = 3

FIXED = 0
VARIABLE = 1
INFINITE = 2

def init_spi():
    chip = sys.platform
    if chip == 'esp32':
        return SPI(1, baudrate=5000000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    elif chip == 'esp8266':
        return SPI(1, baudrate=5000000, polarity=1, phase=1)
    else:
        raise Exception('')


# TODO: figuring out the max time between CS LOW and sending the fist packet

class Transceiver(object):

    FREQ_XOSC = 26000000 # quartz, 26 MHz

    def __init__(self, spi, cs, gdo0=None, gdo2=None, endian='big'):
        
        self.cc1101 = CC1101(spi, cs, gdo0=gdo0, gdo2=gdo2, endian=endian)
        self.endian = endian

    def reset(self):
        return self.cc1101.strobe(SRES)

    # frequency
    def set_freq(self, frequency):
        """
        Fcarrier = (Fxosc/2**16)*FREQ
        """
        f = int((frequency/self.FREQ_XOSC) * 2**16)
        self.cc1101.burst_write(FREQ2, f.to_bytes(3, self.endian))
    
    def get_freq(self):
        resp = self.cc1101.burst_read(FREQ2, 3)
        freq = int.from_bytes(resp, self.endian)
        return (self.FREQ_XOSC/2**16)*freq

    # TODO: merge the get/set into a single method to read and write?
    # packet format
    def set_packet_format(self, pkt_format):
        if pkt_format not in [NORMAL, SYNC, RANDOM, ASYNC]:
            raise Exception('')
        status, val = self.cc1101.read(PKTCTRL0)
        self.cc1101.write(PKTCTRL0, 0b01100101)

    def get_packet_format(self):
        resp = {
            0: 'NORMAL',
            1: 'SYNC',
            2: 'RANDOM',
            3: 'ASYNC'
        }
        form = int(BITS_F.format(self.cc1101.read(PKTCTRL0))[2:4], 2)
        return resp[form]

    def get_marc_state(self):
        resp = {
            0: 'SLEEP',
            1: 'IDLE',
            2: 'XOFF',
            13: 'RX',
            17: 'RXFIFO_OVERFLOW',
            19: 'TX',
            22: 'TXFIFO_UNDERFLOW'
        }
        state = int(BITS_F.format(self.cc1101.status(MARCSTATE))[3:], 2)
        return resp[state]

    def get_packet_length_conf(self):
        resp = {
            0: 'FIXED',
            1: 'VARIABLE',
            2: 'INFINITE'
        }
        form = int(BITS_F.format(self.cc1101.read(PKTCTRL0))[6:], 2)
        return resp[form]

    def set_packet_length_conf(self, pkt_len):
        if pkt_len not in [FIXED, VARIABLE, INFINITE]:
            raise Exception('')
        status, val = self.cc1101.read(PKTCTRL0)
        print(val | pkt_len)

    def get_packet_len(self):
        return int(BITS_F.format(self.cc1101.read(PKTLEN)), 2)

    def get_deviation(self):
        bits_resp = '{0:08b}'.format(self.cc1101.read(DEVIATN))
        exp = int(bits_resp[1:4], 2)
        mantissa = int(bits_resp[5:], 2)
        return (self.FREQ_XOSC/2**17)*(8+mantissa)*(2**exp)

    def get_modulation_format(self):
        resp = {
            1: '2FSK',
            2: 'GFSK',
            3: 'ASK',
            4: '4FSK',
            7: 'MSK'
        }
        bits_resp = '{0:08b}'.format(self.cc1101.read(MDMCFG2))
        mod = int(bits_resp[1:4], 2)
        return resp[mod]

    def get_chip_ready(self):
        state = self.cc1101.strobe(SNOP)
        state_bits = '{:08b}'.format(state)[0]
        return int(state_bits, 2)

    def get_state(self):
        state = self.cc1101.strobe(SNOP)
        state_bits = '{:08b}'.format(state)[1:4]
        return int(state_bits, 2)

    def get_fifo_bytes(self):
        state = self.cc1101.strobe(SNOP)
        state_bits = '{:08b}'.format(state)[4:]
        return int(state_bits, 2)

    def tx_fifo(self, databytes):
        addr = FIFO + 0x40
        buf = bytearray([addr]) + databytes
        return self.cc1101._spi_write(buf)

    def send(self, data):
        # load TX buffer
        return self.write(FIFO, data)

if sys.platform == 'esp32':
    cs = Pin(17, Pin.OUT)
    gdo0 = Pin(4, Pin.IN)
    gdo2 = Pin(16, Pin.IN)
else:
    cs = Pin(15, Pin.OUT)
    gdo0 = Pin(4, Pin.IN)
    gdo2 = Pin(5, Pin.IN)

spi = init_spi()

t = Transceiver(spi, cs, gdo0=gdo0, gdo2=gdo2)

from conf import conf

for k, v in list(conf.items()):
    addr = locals()[k]
    t.cc1101.write(addr, v)

data = bytearray('this is a test, qwerty123456')

if sys.platform == 'esp32':
    pass
    # for i in range(200):
    #     pass
else:
    for i in range(10):
        st = t.get_marc_state()
        if st == 'TXFIFO_UNDERFLOW':
            t.cc1101.strobe(SFTX)
        t.tx_fifo(data)
        t.cc1101.strobe(STX)
        sleep(1)

