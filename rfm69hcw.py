from machine import Pin, SPI
from time import sleep
from esp_spi import EspSPI
from helper import *
from rfm69.registers import *

# TODO: time to find a better name for the repo

PACKET_LENGTH_CONF = {
    0: 'FIXED',
    1: 'VARIABLE',
    2: 'INFINITE'
}

class RFM69HCW(object):

    def __init__(self, spi, cs, gdo0=None, endian='big', xosc=32000000):
        
        self.spi = EspSPI(spi, cs)
        self.FREQ_XOSC = xosc
        self.endian = endian

    # RegFifo 0x00

    # RegOpMode 0x01

    # RegDataModul 0x02

    # RegBitrateMsb 0x03

    # RegBitrateMsb 0x04

    # RegPacketConfig1 0x37

    def get_packet_length_conf(self):
        res = read_bits(self.spi.read(PACKETCONFIG1), 0x00, 0x01)
        return PACKET_LENGTH_CONF[res]

    def set_packet_length_conf(self, pkt_len):
        codes = reverse(PACKETCONFIG1)
        self.set_bits(PKTCTRL0, codes[pkt_len], 0x00, 0x01)