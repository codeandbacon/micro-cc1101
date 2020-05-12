from machine import Pin, SPI
from status import *
from configuration import *
from strobes import *
from time import sleep

PATABLE = 0x3e
FIFO = 0x3f

SINGLE_WRITE = 0x00
BURST_WRITE = 0x40
SINGLE_READ = 0x80
BURST_READ = 0xc0

ENDIAN = 'big'

# TODO: figuring out the max time between CS LOW and sending the fist packet

class CC1101(object):

    FREQ_XOSC = 26000000 # quartz, 26 MHz

    def __init__(self, spi, cs, gdo0=None, gdo2=None, endian='big'):
        self.spi = spi
        self.cs = cs
        self.endian = endian

        if gdo0:
            while gdo0.value():
                sleep(1)
            print('chip ready')

        self.spi.init()
    
    def register_addr_space(self, address):
        if address > 0x2f:
            raise Exception('address is above configuration registers')

    def _spi_read(self, address, length=2):
        self.cs.value(0)
        res = self.spi.read(length, address)
        self.cs.value(1)
        return res

    def _spi_write(self, write_buf):
        read_buf = bytearray(len(write_buf))
        self.cs.value(0)
        self.spi.write_readinto(write_buf, read_buf)
        self.cs.value(1)
        return read_buf

    def read(self, address):
        self.register_addr_space(address)
        res = self._spi_read(address + SINGLE_READ)
        return res[1], res[0]

    def burst_read(self, address, n):
        self.register_addr_space(address)
        res = self._spi_read(address + BURST_READ, length=n+1)
        return res[1:], res[0]

    def write(self, address, byte):
        self.register_addr_space(address)
        write_buf = bytearray([address, byte])
        return self._spi_write(write_buf)
        
    def burst_write(self, address, databytes):
        self.register_addr_space(address)
        address += BURST_WRITE
        write_buf = bytearray([address]) + databytes
        return self._spi_write(write_buf)

    def strobe(self, address):
        if address < 0x30 or address > 0x3d:
            raise Exception('not a strobe address')
        return self._spi_read(address)

    def status(self, address):
        if address < 0xf0 or address > 0xfd:
            raise Exception('not a status register address')
        return self._spi_read(address)