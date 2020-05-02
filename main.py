from machine import Pin, SPI
from status import *
from configuration import *

ENDIAN = 'big'

# TODO: figuring out the max time between CS LOW and sending the fist packet

class CC1101(object):

    def __init__(self, spi, cs, endian='big'):
        self.spi = spi
        self.cs = cs
        self.endian = endian

        self.spi.init()

    def read(self, address, n):
        if n > 1:
            address += 0xc0
        else:
            address += 0x80
        self.cs.value(0)
        res = self.spi.read(n + 1, address)
        self.cs.value(1)
        return res

    def write(self, address, data):
        if len(data) > 1:
            # burst access, add 0x40
            address += 0x40
        read_buf = bytearray(len(data) + 1) # include first status byte
        addr = bytearray(1)
        addr[0] = address
        write_buf = addr + data
        self.cs.value(0)
        self.spi.write_readinto(write_buf, read_buf)
        self.cs.value(1)
        return read_buf

    def set_freq(self, frequency):
        """
        Fcarrier = (Fxosc/2**16)*FREQ
        """
        freq_xosc = 26000000
        f = int((frequency/freq_xosc) * 2**16)
        return self.write(FREQ2, f.to_bytes(3, ENDIAN))
    
    def get_freq(self):
        freq = int.from_bytes(self.read(FREQ2, 3)[1:], ENDIAN)
        return (26000000/2**16)*freq

spi = SPI(1, baudrate=5000000, polarity=1, phase=1)

cs = Pin(15, Pin.OUT)

gd0 = Pin(4, Pin.IN)
gd2 = Pin(5, Pin.IN)

c = CC1101(spi, cs)