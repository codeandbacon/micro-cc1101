import sys
from machine import Pin, SPI
from status import *
from configuration import *
from strobes import *
from time import sleep
from esp_spi import EspSPI
from response import *

BITS_F = '{0:08b}'

PATABLE = 0x3e
FIFO = 0x3f

NORMAL = 0
SYNC = 1
RANDOM = 2
ASYNC = 3

def reverse(codes):
    return dict([(v, k) for k, v in codes.items()])

def to_bits_string(value):
    return str.format(BITS_F, value)

def read_bits(value, start=0, length=8):
    return int(to_bits_string(value)[start:start+length], 2)

def change_bits(byte, change, start=0, length=8):
    # TODO: find something less convoluted
    mask = str.format(BITS_F, 255)
    mask = mask[0:start] + '0'*length + mask[start+length:8]
    change_mask = str.format(BITS_F, 0)
    bits_change = str.format(BITS_F, change)[8-length:8]
    change_mask = change_mask[0:start] + bits_change + change_mask[start+length:8]
    return byte & int(mask, 2) | int(change_mask, 2)

# TODO: re-think class names
class CC1101(object):

    def __init__(self, spi, cs, gdo0=None, gdo2=None, endian='big', xosc=26000000):
        
        self.cc1101 = EspSPI(spi, cs, gdo0=gdo0, gdo2=gdo2)
        self.FREQ_XOSC = xosc
        self.endian = endian

    # 0x00, 0x01, 0x02, output pin configuration

    # 0x03, RX TX thresholds

    def get_fifo_thresholds(self):
        res = read_bits(self.cc1101.read(FIFOTHR), 4, 4)
        return FIFO_THRESHOLDS[res]

    # 0x04, 0x05, sync word

    # 0x06, packet length

    # 0x07, 0x08, packet automation control

    def get_data_whitening(self):
        return read_bits(self.cc1101.read(FIFOTHR), 1, 1)

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

    def get_crc_autoflush(self):
        return read_bits(self.cc1101.read(PKTCTRL1), 4, 1)

    def set_crc_autoflush(self, autoflush):
        current = read_bits(self.cc1101.read(PKTCTRL1), 4, 1)
        change = change_bits(current, autoflush, 4, 1)
        self.cc1101.write(PKTCTRL1, change)

    def get_append_status(self):
        return read_bits(self.cc1101.read(PKTCTRL1), 5, 1)

    def set_append_status(self, status):
        current = read_bits(self.cc1101.read(PKTCTRL1), 5, 1)
        change = change_bits(current, status, 5, 1)
        self.cc1101.write(PKTCTRL1, change)

    def get_address_check(self):
        res = read_bits(self.cc1101.read(PKTCTRL1), 6, 2)
        return ADDRESS_CHECK[res]

    def set_address_check(self, check):
        codes = dict([(v, k) for k, v in ADDRESS_CHECK.items()])
        current = read_bits(self.cc1101.read(PKTCTRL1), 6, 2)
        change = change_bits(current, codes[check], 6, 2)
        self.cc1101.write(PKTCTRL1, change)

    # TODO: merge the get/set into a single method to read and write?
    # packet format
    def set_packet_format(self, pkt_format):
        if pkt_format not in [NORMAL, SYNC, RANDOM, ASYNC]:
            raise Exception('')
        status, val = self.cc1101.read(PKTCTRL0)
        self.cc1101.write(PKTCTRL0, 0b01100101)

    def get_packet_format(self):
        form = int(BITS_F.format(self.cc1101.read(PKTCTRL0))[2:4], 2)
        return PACKET_FORMAT[form]

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
        res = read_bits(self.cc1101.read(PKTCTRL0), 6, 2)
        return PACKET_LENGTH_CONF[res]

    def set_packet_length_conf(self, pkt_len):
        codes = dict([(v, k) for k, v in PACKET_LENGTH_CONF.items()])
        current = read_bits(self.cc1101.read(PKTCTRL0), 6, 2)
        change = change_bits(current, codes[pkt_len], 6, 2)
        self.cc1101.write(PKTCTRL0, change)

    def get_packet_len(self):
        return int(BITS_F.format(self.cc1101.read(PKTLEN)), 2)

    def get_deviation(self):
        bits_resp = '{0:08b}'.format(self.cc1101.read(DEVIATN))
        exp = int(bits_resp[1:4], 2)
        mantissa = int(bits_resp[5:], 2)
        return (self.FREQ_XOSC/2**17)*(8+mantissa)*(2**exp)

    def get_forward_error_correction(self):
        return read_bits(self.cc1101.read(MDMCFG1), 0, 1)

    def set_forward_error_correction(self, fec):
        current = read_bits(self.cc1101.read(MDMCFG1), 0, 1)
        change = change_bits(current, fec, 0, 1)
        self.cc1101.write(MDMCFG1, change)

    # modulation
    def get_modulation_format(self):
        res = read_bits(self.cc1101.read(MDMCFG2), 1, 3)
        return MODULATION_FORMAT[res]

    def set_modulation_format(self, modulation):
        codes = dict([(v, k) for k, v in MODULATION_FORMAT.items()])
        current = read_bits(self.cc1101.read(MDMCFG2), 1, 3)
        change = change_bits(current, codes[modulation], 1, 3)
        self.cc1101.write(MDMCFG2, change)

    def get_preamble_bits(self):
        res = read_bits(self.cc1101.read(MDMCFG1), 1, 3)
        return PREAMBLE_BITS[res]

    def set_preamble_bits(self, num):
        codes = dict([(v, k) for k, v in PREAMBLE_BITS.items()])
        current = read_bits(self.cc1101.read(MDMCFG1), 1, 3)
        change = change_bits(current, codes[num], 1, 3)
        self.cc1101.write(MDMCFG1, change)

    def get_data_rate(self):
        exp = int(to_bits_string(self.cc1101.read(MDMCFG4))[4:], 2)
        mantissa = int(to_bits_string(self.cc1101.read(MDMCFG3)), 2)
        return (((256+mantissa)*(2**exp))/2**28)*self.FREQ_XOSC

    def get_manchester_enc(self):
        return read_bits(self.cc1101.read(MDMCFG2), 4, 1)

    def set_manchester_enc(self, enable):
        current = self.cc1101.read(MDMCFG2)
        change = change_bits(current, enable, 4, 1)
        self.cc1101.write(MDMCFG2, change)

    def get_sync_word(self):
        high = self.cc1101.read(SYNC1)
        low = self.cc1101.read(SYNC0)
        return to_bits_string(high) + to_bits_string(low)

    def set_sync_word(self, word):
        high = word[:8]
        low = word[8:]
        self.cc1101.write(SYNC1, int(high, 2))
        self.cc1101.write(SYNC0, int(low, 2))

    def get_qualifier_mode(self):
        resp = {
            0: 'NO_PRE_SYNC',
            1: '15_16_SYNC',
            2: '16_16_SYNC',
            3: '30_32_SYNC',
            4: 'NO_PRE_SYNC_CARRIER',
            5: '15_16_SYNC_CARRIER',
            6: '16_16_SYNC_CARRIER',
            7: '30_32_SYNC_CARRIER',
        }
        mode = read_bits(self.cc1101.read(MDMCFG2), 5, 3)
        return resp[mode]

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

    def rx_fifo(self):
        addr = FIFO + 0x80
        print(self.cc1101._spi_read(addr)[0])
        print(self.cc1101._spi_read(addr)[1])

    def send(self, data):
        # load TX buffer
        return self.write(FIFO, data)
