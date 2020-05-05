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

            # gdo0.irq(trigger=Pin.IRQ_RISING, handler=self.data_received)

        self.spi.init()

    def data_received(self, pin):
        print('data recevied')

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

    def reset(self):
        self._spi_read(SRES)

    def read(self, address):
        res = self._spi_read(address + SINGLE_READ)
        return res[1], res[0]

    def burst_read(self, address, n):
        res = self._spi_read(address + BURST_READ, length=n+1)
        return res[1:], res[0]

    def write(self, address, byte):
        write_buf = bytearray([address, byte])
        return self._spi_write(write_buf)
        
    def burst_write(self, address, databytes):
        address += BURST_WRITE
        write_buf = bytearray([address]) + databytes
        return self._spi_write(write_buf)

    def set_freq(self, frequency):
        """
        Fcarrier = (Fxosc/2**16)*FREQ
        """
        f = int((frequency/self.FREQ_XOSC) * 2**16)
        return self.burst_write(FREQ2, f.to_bytes(3, self.endian))
    
    def get_freq(self):
        freq = int.from_bytes(self.burst_read(FREQ2, 3)[0], self.endian)
        return (self.FREQ_XOSC/2**16)*freq

    def status_info(self, state_byte):
        bits = '{0:08b}'.format(state_byte)
        chip_ready = bits[0]
        main_state = bits[1:4]
        fifo_bytes = bits[4:]

        # chip ready
        if chip_ready == '1':
            print('Chip not ready')
        else:
            print('Chip ready')

        # main state
        if main_state == '000':
            print('IDLE')
        elif main_state == '001':
            print('RX')
        elif main_state == '010':
            print('TX')
        

spi = SPI(1, baudrate=5000000, polarity=1, phase=1)

cs = Pin(15, Pin.OUT)

gdo0 = Pin(4, Pin.IN)
gdo2 = Pin(5, Pin.IN)

c = CC1101(spi, cs, gdo0=gdo0, gdo2=gdo2)
