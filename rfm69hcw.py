import sys
import math
from machine import Pin, SPI
from status import *
from configuration import *
from strobes import *
from time import sleep
from esp_spi import EspSPI
from response import *
from helper import *

# TODO: time to find a better name for the repo

class RFM69HCW(object):

    def __init__(self, spi, cs, gdo0=None, endian='big', xosc=32000000):
        
        self.spi = EspSPI(spi, cs)
        self.FREQ_XOSC = xosc
        self.endian = endian