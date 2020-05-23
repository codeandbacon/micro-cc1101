from machine import Pin, SPI
from status import *
from configuration import *
from strobes import *
from time import sleep
from cc1101 import CC1101
from resp import read_resp

PATABLE = 0x3e
FIFO = 0x3f

SINGLE_WRITE = 0x00
BURST_WRITE = 0x40
SINGLE_READ = 0x80
BURST_READ = 0xc0

ENDIAN = 'big'

NORMAL = 0
SYNCH = 1
RANDOM = 2

FIXED = 0
VARIABLE = 1
INFINITE = 2

# TODO: figuring out the max time between CS LOW and sending the fist packet

class Transceiver(object):

    FREQ_XOSC = 26000000 # quartz, 26 MHz

    def __init__(self, spi, cs, gdo0=None, gdo2=None, endian='big'):
        
        self.cc1101 = CC1101(spi, cs, gdo0=gdo0, gdo2=gdo2, endian=endian)
        self.endian = endian

    def reset(self):
        res, status = self.cc1101.strobe(SRES)
        self.status_info(status)

    def set_freq(self, frequency):
        """
        Fcarrier = (Fxosc/2**16)*FREQ
        """
        f = int((frequency/self.FREQ_XOSC) * 2**16)
        return self.cc1101.burst_write(FREQ2, f.to_bytes(3, self.endian))
    
    def get_freq(self):
        res, status = self.cc1101.burst_read(FREQ2, 3)
        self.status_info(status)
        freq = int.from_bytes(res, self.endian)
        return (self.FREQ_XOSC/2**16)*freq

    def get_state(self):
        status_byte, state = self.cc1101.status(MARCSTATE)
        # self.status_info(state_byte)
        print(status_byte, state)
        bits = '{0:08b}'.format(state)
        print(bits)
        # marc_state = [3:]

    def set_packet_format(self, pkt_format):
        if pkt_format not in [NORMAL, SYNCH, RANDOM]:
            raise Exception('')
        status, val = self.cc1101.read(PKTCTRL0)
        self.cc1101.write(PKTCTRL0, 0b01100101)

    def set_packet_length(self, pkt_len):
        if pkt_len not in [FIXED, VARIABLE, INFINITE]:
            raise Exception('')
        status, val = self.cc1101.read(PKTCTRL0)
        print(val | pkt_len)

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


spi = SPI(1, baudrate=5000000, polarity=1, phase=1)
cs = Pin(15, Pin.OUT)
gdo0 = Pin(4, Pin.IN)
gdo2 = Pin(5, Pin.IN)

t = Transceiver(spi, cs, gdo0=gdo0, gdo2=gdo2)

from conf import conf

for k, v in list(conf.items()):
    addr = locals()[k]
    t.cc1101.write(addr, v)