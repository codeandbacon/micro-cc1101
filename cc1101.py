import sys
import math
from machine import Pin, SPI
from status import *
from configuration import *
from strobes import *
from time import sleep
from esp_spi import EspSPI
from response import *

BITS_F = '{0:08b}'

def reverse(codes):
    return dict([(v, k) for k, v in codes.items()])

def to_bits_string(value):
    return str.format(BITS_F, value)

def read_bits(value, start=0, length=8):
    return int(to_bits_string(value)[start:start+length], 2)

# TODO: re-think class names
class CC1101(object):

    def __init__(self, spi, cs, gdo0=None, gdo2=None, endian='big', xosc=26000000):
        
        self.cc1101 = EspSPI(spi, cs, gdo0=gdo0, gdo2=gdo2)
        self.FREQ_XOSC = xosc
        self.endian = endian

    # 0x00, 0x01, 0x02, output pin configuration

    def set_bits(self, register, change, start=0, length=8):
        current = read_bits(self.cc1101.read(register))
        mask = str.format(BITS_F, 255)
        mask = mask[0:start] + '0'*length + mask[start+length:8]
        change_mask = str.format(BITS_F, 0)
        bits_change = str.format(BITS_F, change)[8-length:8]
        change_mask = change_mask[0:start] + bits_change + change_mask[start+length:8]
        change = current & int(mask, 2) | int(change_mask, 2)
        self.cc1101.write(register, change)

    def get_gdo2_inverted_output(self):
        return read_bits(self.cc1101.read(IOCFG2), 0x01, 0x01)

    def get_gdo2_conf(self):
        res = read_bits(self.cc1101.read(IOCFG2), 0x02, 0x06)
        return GDO_MODE[res]

    def set_gdo2_conf(self, mode):
        codes = reverse(GDO_MODE)
        self.set_bits(IOCFG2, codes[mode], 0x02, 0x06)

    def get_gdo0_conf(self):
        res = read_bits(self.cc1101.read(IOCFG0), 0x02, 0x06)
        return GDO_MODE[res]

    def set_gdo0_conf(self, mode):
        codes = reverse(GDO_MODE)
        self.set_bits(IOCFG0, codes[mode], 0x02, 0x06)

    # 0x03, RX TX thresholds

    def get_fifo_thresholds(self):
        res = read_bits(self.cc1101.read(FIFOTHR), 0x04, 0x04)
        return FIFO_THRESHOLDS[res]

    # 0x04, 0x05, sync word

    def get_sync_word(self):
        high = self.cc1101.read(SYNC1)
        low = self.cc1101.read(SYNC0)
        return to_bits_string(high) + to_bits_string(low)

    def set_sync_word(self, word):
        high = word[:8]
        low = word[8:]
        self.cc1101.write(SYNC1, int(high, 2))
        self.cc1101.write(SYNC0, int(low, 2))

    # 0x06, packet length

    def get_packet_len(self):
        return read_bits(self.cc1101.read(PKTLEN))

    def set_packet_len(self, length):
        self.cc1101.write(PKTLEN, length)

    # 0x07, 0x08, packet automation control

    def get_pqt(self):
        return read_bits(self.cc1101.read(PKTCTRL1), 0x00, 0x02)        

    def set_pqt(self, pqt):
        self.set_bits(PKTCTRL1, pqt, 0x00, 0x02)        

    def get_crc_autoflush(self):
        return read_bits(self.cc1101.read(PKTCTRL1), 0x04, 0x01)

    def set_crc_autoflush(self, autoflush):
        self.set_bits(PKTCTRL1, autoflush, 0x04, 0x01)

    def get_append_status(self):
        return read_bits(self.cc1101.read(PKTCTRL1), 0x05, 0x01)

    def set_append_status(self, status):
        self.set_bits(PKTCTRL1, status, 0x05, 0x01)

    def get_address_check(self):
        res = read_bits(self.cc1101.read(PKTCTRL1), 0x06, 0x02)
        return ADDRESS_CHECK[res]

    def set_address_check(self, check):
        codes = reverse(ADDRESS_CHECK)
        self.set_bits(PKTCTRL1, codes[check], 0x06, 0x02)

    def get_data_whitening(self):
        return read_bits(self.cc1101.read(PKTCTRL0), 0x01, 0x01)

    def set_data_whitening(self, whitening):
        self.set_bits(PKTCTRL0, whitening, 0x01, 0x01)

    def get_packet_format(self):
        return PACKET_FORMAT[read_bits(self.cc1101.read(PKTCTRL0), 0x02, 0x02)]

    def set_packet_format(self, pkt_format):
        codes = reverse(PACKET_FORMAT)
        self.set_bits(PKTCTRL0, codes[pkt_format], 0x02, 0x02)

    def get_crc_calc(self):
        return read_bits(self.cc1101.read(PKTCTRL0), 0x05, 0x01)        

    def set_crc_calc(self, crc):
        self.set_bits(PKTCTRL0, crc, 0x05, 0x01)

    def get_packet_length_conf(self):
        res = read_bits(self.cc1101.read(PKTCTRL0), 0x06, 0x02)
        return PACKET_LENGTH_CONF[res]

    def set_packet_length_conf(self, pkt_len):
        codes = reverse(PACKET_LENGTH_CONF)
        self.set_bits(PKTCTRL0, codes[pkt_len], 0x06, 0x02)

    # 0x09, device address

    def get_device_address(self):
        return read_bits(self.cc1101.read(ADDR))

    def set_device_address(self, address):
        self.set_bits(ADDR, address)

    # 0x0a, channel number

    def get_chan(self):
        return read_bits(self.cc1101.read(CHANNR))

    def set_chan(self, channel):
        self.set_bits(CHANNR, channel)

    # 0x0b, 0x0c, frequency synthesizer control

    def get_intermediate_frequency(self):
        freq_if = read_bits(self.cc1101.read(FSCTRL1), 0x03, 0x05)
        return (self.FREQ_XOSC/1024)*freq_if

    def set_intermediate_frequency(self, freq):
        freq_if = int((freq/self.FREQ_XOSC)*1024)
        self.set_bits(FSCTRL1, freq_if, 0x03, 0x05)

    def get_frequency_offset(self):
        return read_bits(self.cc1101.read(FSCTRL0))

    def set_frequency_offset(self, offset):
        self.cc1101.write(FSCTRL0, offset)

    # 0x0d, 0x0e, 0x0f, frequency controol word

    def get_freq(self):
        resp = self.cc1101.burst_read(FREQ2, 0x03)
        freq = int.from_bytes(resp, self.endian)
        return (self.FREQ_XOSC/2**16)*freq

    def set_freq(self, frequency):
        f = int((frequency/self.FREQ_XOSC) * 2**16)
        self.cc1101.burst_write(FREQ2, f.to_bytes(3, self.endian))
    
    # 0x10, 0x11, 0x12, 0x13, 0x14, modem configuration

    def get_channel_bandwidth(self):
        current = read_bits(self.cc1101.read(MDMCFG4), 0, 4)
        return CHANNEL_BANDWIDTH[current]
        
    def set_channel_bandwidth(self, width):
        codes = reverse(CHANNEL_BANDWIDTH)
        self.set_bits(MDMCFG4, codes[width], 0, 4)

    def get_data_rate(self):
        exp = int(to_bits_string(self.cc1101.read(MDMCFG4))[4:], 2)
        mantissa = int(to_bits_string(self.cc1101.read(MDMCFG3)), 2)
        return (((256+mantissa)*(2**exp))/2**28)*self.FREQ_XOSC

    def set_data_rate(self, rate):
        drate_e = round(math.log(((rate*(2**20))/self.FREQ_XOSC), 2))
        drate_m = round(((rate*(2**28))/(self.FREQ_XOSC*(2**drate_e))) - 256)
        if drate_m < 0:
            drate_m = 0
        if drate_m > 255:
            drate_m = 0
            drate_e += 1
        self.set_bits(MDMCFG4, drate_e, 0x04, 0x04)
        self.set_bits(MDMCFG3, drate_m)

    def get_dc_blocking_filter(self):
        return read_bits(self.cc1101.read(MDMCFG2), 0x00, 0x01)

    def set_dc_blocking_filter(self, enable):
        self.set_bits(MDMCFG2, enable, 0x00, 0x01)

    def get_modulation_format(self):
        res = read_bits(self.cc1101.read(MDMCFG2), 0x01, 0x03)
        return MODULATION_FORMAT[res]

    def set_modulation_format(self, modulation):
        codes = reverse(MODULATION_FORMAT)
        self.set_bits(MDMCFG2, codes[modulation], 0x01, 0x03)

    def get_manchester_enc(self):
        return read_bits(self.cc1101.read(MDMCFG2), 0x04, 0x01)

    def set_manchester_enc(self, enable):
        self.set_bits(MDMCFG2, enable, 0x04, 0x01)

    def get_qualifier_mode(self):
        mode = read_bits(self.cc1101.read(MDMCFG2), 0x05, 0x03)
        return QUALIFIER_MODE[mode]

    def set_qualifier_mode(self, mode):
        codes = reverse(QUALIFIER_MODE)
        self.set_bits(MDMCFG2, codes[mode], 0x05, 0x03)

    def get_preamble_bits(self):
        res = read_bits(self.cc1101.read(MDMCFG1), 0x01, 0x03)
        return PREAMBLE_BITS[res]

    def set_preamble_bits(self, num):
        codes = reverse(PREAMBLE_BITS)
        self.set_bits(MDMCFG1, codes[num], 0x01, 0x03)

    def get_forward_error_correction(self):
        return read_bits(self.cc1101.read(MDMCFG1), 0x00, 0x01)

    def set_forward_error_correction(self, fec):
        self.set_bits(MDMCFG1, fec, 0x00, 0x01)

    def get_channel_spacing(self):
        exp = read_bits(self.cc1101.read(MDMCFG1), 0x06, 0x02)
        mantissa = read_bits(self.cc1101.read(MDMCFG0))
        return (self.FREQ_XOSC/2**18)*(256+mantissa)*(2**exp)

    # 0x15, modem deviation setting

    def get_deviation(self):
        bits_resp = '{0:08b}'.format(self.cc1101.read(DEVIATN))
        exp = int(bits_resp[1:4], 2)
        mantissa = int(bits_resp[5:], 2)
        return (self.FREQ_XOSC/2**17)*(8+mantissa)*(2**exp)

    def set_deviation(self, deviation):
        e = math.floor(math.log(deviation/1586, 2))
        m = (deviation/((self.FREQ_XOSC/2**17)*(2**e)))-8
        self.set_bits(DEVIATN, int((e*16)+m))

    # 0x16, 0x17, 0x18, main radio control state machine configuration

    def get_rx_rssi(self):
        return read_bits(self.cc1101.read(MCSM2), 0x03, 0x01)

    def get_rx_qual(self):
        return read_bits(self.cc1101.read(MCSM2), 0x04, 0x01)

    def get_rx_time(self):
        return read_bits(self.cc1101.read(MCSM2), 0x05, 0x03)

    def get_cca_mode(self):
        cca = read_bits(self.cc1101.read(MCSM1), 0x02, 0x02)
        return CCA_MODE[cca]

    def get_rxoff_mode(self):
        val = read_bits(self.cc1101.read(MCSM1), 0x04, 0x02)
        return OFF_MODE[val]

    def set_rxoff_mode(self, mode):
        codes = reverse(OFF_MODE)
        self.set_bits(MCSM1, codes[mode], 0x04, 0x02)

    def get_txoff_mode(self):
        val = read_bits(self.cc1101.read(MCSM1), 0x06, 0x02)
        return OFF_MODE[val]

    def get_fs_autocal(self):
        val = read_bits(self.cc1101.read(MCSM0), 0x02, 0x02)
        return AUTOCAL[val]

    def set_fs_autocal(self, cal):
        codes = reverse(AUTOCAL)
        self.set_bits(MCSM0, codes[cal], 0x02, 0x02)

    def get_po_timeout(self):
        val = read_bits(self.cc1101.read(MCSM0), 0x04, 0x02)
        return PO_TIMEOUT[val]

    def set_po_timeout(self, timeout):
        codes = reverse(PO_TIMEOUT)
        self.set_bits(MCSM0, codes[timeout], 0x04, 0x02)

    def get_pin_ctrl_en(self):
        return read_bits(self.cc1101.read(MCSM0), 0x06, 0x01)

    def get_xosc_force_on(self):
        return read_bits(self.cc1101.read(MCSM0), 0x07, 0x01)

    # 0x19, frequency offset compensation configuration

    def get_foc_bs_cs_gate(self):
        return read_bits(self.cc1101.read(FOCCFG), 0x02, 0x01)

    def get_frequency_compensation(self):
        return read_bits(self.cc1101.read(FOCCFG), 0x03, 0x02)

    def set_frequency_compensation(self, gain):
        codes = reverse(LOOP_GAIN)
        self.set_bits(FOCCFG, codes[gain], 0x03, 0x02)

    def get_foc_post_k(self):
        return read_bits(self.cc1101.read(FOCCFG), 0x05, 0x01)

    def get_foc_limit(self):
        return read_bits(self.cc1101.read(FOCCFG), 0x06, 0x02)

    def set_foc_limit(self, saturation):
        codes = reverse(SATURATION_POINT)
        self.set_bits(FOCCFG, codes[saturation], 0x06, 0x02)

    # 0x1a, bit synchronization configuration

    def set_bs_pre_k(self, gain):
        codes = reverse(LOOP_GAIN)
        self.set_bits(BSCFG, codes[gain], 0x00, 0x02)

    def set_bs_pre_kp(self, gain):
        codes = reverse(LOOP_GAIN)
        self.set_bits(BSCFG, codes[gain], 0x02, 0x02)

    # 0x1b, 0x1c, 0x1d, AGC control

    def get_max_dvga_gain(self):
        return read_bits(self.cc1101.read(AGCCTRL2), 0x00, 0x02)

    def set_max_dvga_gain(self, gain):
        codes = reverse(DVGA_GAIN)
        self.set_bits(AGCCTRL2, codes[gain], 0x00, 0x02)

    def get_max_lna_gain(self):
        return read_bits(self.cc1101.read(AGCCTRL2), 0x02, 0x03)

    def get_magn_target(self):
        return read_bits(self.cc1101.read(AGCCTRL2), 0x05, 0x03)

    def set_magn_target(self, target):
        codes = reverse(MAGN_TARGET)
        self.set_bits(AGCCTRL2, codes[target], 0x05, 0x03)

    def get_agc_lna_priority(self):
        return read_bits(self.cc1101.read(AGCCTRL1), 0x01, 0x01)

    def set_agc_lna_priority(self, strat):
        self.set_bits(AGCCTRL1, strat, 0x01, 0x01)

    def get_carrier_sense_rel_thr(self):
        return read_bits(self.cc1101.read(AGCCTRL1), 0x02, 0x02)         

    def get_carrier_sense_abs_thr(self):
        return read_bits(self.cc1101.read(AGCCTRL1), 0x04, 0x04)         

    def get_hyst_level(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 0x00, 0x02)         

    def get_wait_time(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 0x02, 0x02)

    def set_wait_time(self, wait):
        codes = reverse(WAIT_TIME)
        self.set_bits(AGCCTRL0, codes[wait], 0x02, 0x02)

    def get_agc_freeze(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 0x04, 0x02)

    def get_filter_length(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 0x06, 0x02)

    def set_filter_length(self, length):
        codes = reverse(FILTER_LENGTH)
        self.set_bits(AGCCTRL0, codes[length], 0x06, 0x02)

    # 0x1e, 0x1f, byte event0 timeout

    # 0x20, wake on radio control

    # 0x21, 0x22, front end rx configuration

    # 0x23, 0x24, 0x25, 0x26, frequency synthesizer calibration

    # 0x27, 0x28, rc oscillator configuration

    def reset(self):
        return self.cc1101.strobe(SRES)

    def get_marc_state(self):
        state = read_bits(self.cc1101.status(MARCSTATE), 0x03, 0x05)
        return MARC_STATES[state]

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

    def rx_fifo(self, length=1):
        if length > 1:
            addr = FIFO + 0xc0
        else:
            addr = FIFO + 0x80
        rx_data = self.cc1101._spi_read(addr, length + 1)
        return rx_data[1:]

    def rx_bytes(self):
        return self.cc1101.status(RXBYTES)

    # def send(self, data):
    #     # load TX buffer
    #     return self.write(FIFO, data)
