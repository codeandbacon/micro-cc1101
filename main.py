import sys
from machine import Pin, SPI
from cc1101 import CC1101
from configuration import *
import utime
from micropython import const
from strobes import *

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

t.reset()

# IOCFG2, IOCFG1, IOCFG0
t.set_gdo2_conf('SERIAL_CLOCK')
t.set_gdo0_conf('SYNC_WORD')

# FIFOTHR

# SYNC1, SYNC0
t.set_sync_word('1101001110010001')

# # PKTLEN
t.set_packet_len(61)

# # PKTCTRL1, PKTCTRL0
# t.set_crc_autoflush(0)
t.set_append_status(0)
t.set_address_check('NO_ADDR_CHECK')
t.set_data_whitening(0)
t.set_packet_format('NORMAL')
t.set_crc_calc(0)
t.set_packet_length_conf('VARIABLE')

# # ADDR

# # CHANNR

# # FSCTRL1, FSCTRL0
t.set_intermediate_frequency(203125)
# t.set_frequency_offset(0)

# # FREQ2, FREQ1, FREQ0
t.set_freq(915000000)

# # MDMCFG4, MDMCFG3, MDMCFG2, MDMCFG1, MDMCFG0
t.set_data_rate(115051)
t.set_qualifier_mode('30_32_SYNC')
t.set_forward_error_correction(0)
t.set_preamble_bits(4)
t.set_channel_bandwidth(325000)
# t.set_modulation_format('GFSK')
# t.set_dc_blocking_filter(0)
t.set_manchester_enc(0)

# # DEVIATN

# # MCSM2, MCSM1, MCSM0
t.set_fs_autocal('FROM_IDLE')
t.set_po_timeout(64)
t.set_rxoff_mode('RX')

# # FOCCFG
t.set_frequency_compensation('4K')
t.set_foc_limit('BW/8')

# # BSCFG
t.set_bs_pre_k('K')
t.set_bs_pre_kp('2K')

# # AGCCTRL2, AGCCTRL1, AGCCTRL0
t.set_max_dvga_gain('NOT_3_HIGHEST')
t.set_magn_target(42)
t.set_agc_lna_priority(0)
t.set_wait_time(32)
t.set_filter_length(32)

# # WOREVT1, WOREVT0

# # WORCTRL

# # FREND1, FREND0

# # FSCAL3, FSCAL2, FSCAL1, FSCAL0



def handler(pin):
    rxfifo = t.rx_bytes()
    data = t.rx_fifo(rxfifo)
    if len(data):
        print((b'RCV' + data).decode('utf8'))

gdo0.irq(trigger=Pin.IRQ_FALLING, handler=handler)

t.cc1101.strobe(SRX)

def send(data):
    if t.get_marc_state() == 'RXFIFO_OVERFLOW':
        t.cc1101.strobe(SFRX)
        while t.get_marc_state() != 'IDLE':
            utime.sleep_us(1000)
    data_len = len(data)
    d = bytearray([data_len]) + bytearray(data)
    t.tx_fifo(d)
    t.cc1101.strobe(STX)
    while(not gdo0.value()):
        utime.sleep_us(10)    
    while(gdo0.value()):
        utime.sleep_us(10)
    t.cc1101.strobe(SFTX)
    while t.get_marc_state() != 'IDLE':
        utime.sleep_us(1000)
    t.cc1101.strobe(SRX)

import uos
from machine import UART
uos.dupterm(None, 1)

uart = UART(0, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

# while True:
for i in range(5000):
    utime.sleep_us(1000)
    uart.write('hello')
    # uart.read(5) # read up to 5 bytes