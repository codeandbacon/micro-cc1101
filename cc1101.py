import sys
from machine import Pin, SPI
from status import *
from configuration import *
from strobes import *
from time import sleep
from esp_spi import EspSPI
from response import *

BITS_F = '{0:08b}'

FIFO = 0x3f

def reverse(codes):
    return reverse(codes)

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
        return read_bits(self.cc1101.read(IOCFG2), 1, 1)

    def get_gdo2_conf(self):
        res = read_bits(self.cc1101.read(IOCFG2), 2, 6)
        return GDO_MODE[res]

    def set_gdo2_conf(self, mode):
        codes = reverse(GDO_MODE)
        current = read_bits(self.cc1101.read(IOCFG2))
        change = change_bits(current, codes[mode], 2, 6)
        self.cc1101.write(IOCFG2, change)

    def set_gdo0_conf(self, mode):
        codes = reverse(GDO_MODE)
        current = read_bits(self.cc1101.read(IOCFG0))
        change = change_bits(current, codes[mode], 2, 6)
        self.cc1101.write(IOCFG0, change)

    # 0x03, RX TX thresholds

    def get_fifo_thresholds(self):
        res = read_bits(self.cc1101.read(FIFOTHR), 4, 4)
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
        pass

    def get_crc_autoflush(self):
        return read_bits(self.cc1101.read(PKTCTRL1), 4, 1)

    def set_crc_autoflush(self, autoflush):
        current = read_bits(self.cc1101.read(PKTCTRL1))
        change = change_bits(current, autoflush, 4, 1)
        self.cc1101.write(PKTCTRL1, change)

    def get_append_status(self):
        return read_bits(self.cc1101.read(PKTCTRL1), 5, 1)

    def set_append_status(self, status):
        current = read_bits(self.cc1101.read(PKTCTRL1))
        change = change_bits(current, status, 5, 1)
        self.cc1101.write(PKTCTRL1, change)

    def get_address_check(self):
        res = read_bits(self.cc1101.read(PKTCTRL1), 6, 2)
        return ADDRESS_CHECK[res]

    def set_address_check(self, check):
        codes = reverse(ADDRESS_CHECK)
        current = read_bits(self.cc1101.read(PKTCTRL1))
        change = change_bits(current, codes[check], 6, 2)
        self.cc1101.write(PKTCTRL1, change)

    def get_data_whitening(self):
        return read_bits(self.cc1101.read(PKTCTRL0), 1, 1)

    def set_data_whitening(self, whitening):
        current = read_bits(self.cc1101.read(PKTCTRL0))
        change = change_bits(current, whitening, 1, 1)
        self.cc1101.write(PKTCTRL0, change)

    def get_packet_format(self):
        return PACKET_FORMAT[read_bits(self.cc1101.read(PKTCTRL0), 2, 2)]

    def set_packet_format(self, pkt_format):
        codes = reverse(PACKET_FORMAT)
        current = read_bits(self.cc1101.read(PKTCTRL0))
        change = change_bits(current, codes[pkt_format], 2, 2)
        self.cc1101.write(PKTCTRL0, change)

    def get_crc_calc(self):
        return read_bits(self.cc1101.read(PKTCTRL0), 5, 1)        

    def set_crc_calc(self, crc):
        current = read_bits(self.cc1101.read(PKTCTRL0))
        change = change_bits(current, crc, 5, 1)
        self.cc1101.write(PKTCTRL0, change)

    def get_packet_length_conf(self):
        res = read_bits(self.cc1101.read(PKTCTRL0), 6, 2)
        return PACKET_LENGTH_CONF[res]

    def set_packet_length_conf(self, pkt_len):
        codes = reverse(PACKET_LENGTH_CONF)
        current = read_bits(self.cc1101.read(PKTCTRL0))
        change = change_bits(current, codes[pkt_len], 6, 2)
        self.cc1101.write(PKTCTRL0, change)

    # 0x09, device address

    def get_device_address(self):
        return read_bits(self.cc1101.read(ADDR))

    # 0x0a, channel number

    def get_channel_number(self):
        return read_bits(self.cc1101.read(CHANNR))

    # 0x0b, 0x0c, frequency synthesizer control

    def get_intermediate_frequency(self):
        freq_if = read_bits(self.cc1101.read(FSCTRL1), 3, 5)
        return (self.FREQ_XOSC/1024)*freq_if

    def set_intermediate_frequency(self, freq):
        freq_if = int((freq/self.FREQ_XOSC)*1024)
        current = read_bits(self.cc1101.read(FSCTRL1))
        change = change_bits(current, freq_if, 3, 5)
        self.cc1101.write(FSCTRL1, change)

    def get_frequency_offset(self):
        return read_bits(self.cc1101.read(FSCTRL0))

    def set_frequency_offset(self, offset):
        self.cc1101.write(FSCTRL0, offset)

    # 0x0d, 0x0e, 0x0f, frequency controol word

    def get_freq(self):
        resp = self.cc1101.burst_read(FREQ2, 3)
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
        current = read_bits(self.cc1101.read(MDMCFG4))
        change = change_bits(current, codes[width], 0, 4)
        self.cc1101.write(MDMCFG4, change)    

    def get_data_rate(self):
        exp = int(to_bits_string(self.cc1101.read(MDMCFG4))[4:], 2)
        mantissa = int(to_bits_string(self.cc1101.read(MDMCFG3)), 2)
        return (((256+mantissa)*(2**exp))/2**28)*self.FREQ_XOSC

    def set_data_rate(self, rate):
        pass

    def get_dc_blocking_filter(self):
        return read_bits(self.cc1101.read(MDMCFG2), 0, 1)

    def set_dc_blocking_filter(self, enable):
        current = self.cc1101.read(MDMCFG2)
        change = change_bits(current, enable, 0, 1)
        self.cc1101.write(MDMCFG2, change)

    def get_modulation_format(self):
        res = read_bits(self.cc1101.read(MDMCFG2), 1, 3)
        return MODULATION_FORMAT[res]

    def set_modulation_format(self, modulation):

        codes = reverse(MODULATION_FORMAT)
        current = read_bits(self.cc1101.read(MDMCFG2))
        change = change_bits(current, codes[modulation], 1, 3)
        self.cc1101.write(MDMCFG2, change)

    def get_manchester_enc(self):
        return read_bits(self.cc1101.read(MDMCFG2), 4, 1)

    def set_manchester_enc(self, enable):
        current = self.cc1101.read(MDMCFG2)
        change = change_bits(current, enable, 4, 1)
        self.cc1101.write(MDMCFG2, change)

    def get_qualifier_mode(self):
        mode = read_bits(self.cc1101.read(MDMCFG2), 5, 3)
        return QUALIFIER_MODE[mode]

    def set_qualifier_mode(self, mode):
        codes = reverse(QUALIFIER_MODE)
        current = read_bits(self.cc1101.read(MDMCFG2))
        change = change_bits(current, codes[mode], 5, 3)
        self.cc1101.write(MDMCFG2, change)

    def get_preamble_bits(self):
        res = read_bits(self.cc1101.read(MDMCFG1), 1, 3)
        return PREAMBLE_BITS[res]

    def set_preamble_bits(self, num):
        codes = reverse(PREAMBLE_BITS)
        current = read_bits(self.cc1101.read(MDMCFG1))
        change = change_bits(current, codes[num], 1, 3)
        self.cc1101.write(MDMCFG1, change)

    def get_forward_error_correction(self):
        return read_bits(self.cc1101.read(MDMCFG1), 0, 1)

    def set_forward_error_correction(self, fec):
        self.set_bits(MDMCFG1, fec, 0, 1)

    def get_channel_spacing(self):
        exp = read_bits(self.cc1101.read(MDMCFG1), 6, 2)
        mantissa = read_bits(self.cc1101.read(MDMCFG0))
        return (self.FREQ_XOSC/2**18)*(256+mantissa)*(2**exp)

    # 0x15, modem deviation setting

    def get_deviation(self):
        bits_resp = '{0:08b}'.format(self.cc1101.read(DEVIATN))
        exp = int(bits_resp[1:4], 2)
        mantissa = int(bits_resp[5:], 2)
        return (self.FREQ_XOSC/2**17)*(8+mantissa)*(2**exp)

    # 0x16, 0x17, 0x18, main radio control state machine configuration

    def get_rx_rssi(self):
        return read_bits(self.cc1101.read(MCSM2), 3, 1)

    def get_rx_qual(self):
        return read_bits(self.cc1101.read(MCSM2), 4, 1)

    def get_rx_time(self):
        return read_bits(self.cc1101.read(MCSM2), 5, 3)

    def get_cca_mode(self):
        cca = read_bits(self.cc1101.read(MCSM1), 2, 2)
        return CCA_MODE[cca]

    def get_rxoff_mode(self):
        val = read_bits(self.cc1101.read(MCSM1), 4, 2)
        return OFF_MODE[val]

    def set_rxoff_mode(self, mode):
        codes = reverse(OFF_MODE)
        current = read_bits(self.cc1101.read(MCSM1))
        change = change_bits(current, codes[mode], 4, 2)
        self.cc1101.write(MCSM1, change)

    def get_txoff_mode(self):
        val = read_bits(self.cc1101.read(MCSM1), 6, 2)
        return OFF_MODE[val]

    def get_fs_autocal(self):
        val = read_bits(self.cc1101.read(MCSM0), 2, 2)
        return AUTOCAL[val]

    def set_fs_autocal(self, cal):
        codes = reverse(AUTOCAL)
        current = read_bits(self.cc1101.read(MCSM0))
        change = change_bits(current, codes[cal], 2, 2)
        self.cc1101.write(MCSM0, change)

    def get_po_timeout(self):
        val = read_bits(self.cc1101.read(MCSM0), 4, 2)
        return PO_TIMEOUT[val]

    def set_po_timeout(self, timeout):
        codes = reverse(PO_TIMEOUT)
        current = read_bits(self.cc1101.read(MCSM0))
        change = change_bits(current, codes[timeout], 4, 2)
        self.cc1101.write(MCSM0, change)

    def get_pin_ctrl_en(self):
        return read_bits(self.cc1101.read(MCSM0), 6, 1)

    def get_xosc_force_on(self):
        return read_bits(self.cc1101.read(MCSM0), 7, 1)

    # 0x19, frequency offset compensation configuration

    def get_foc_bs_cs_gate(self):
        return read_bits(self.cc1101.read(FOCCFG), 2, 1)

    def get_frequency_compensation(self):
        return read_bits(self.cc1101.read(FOCCFG), 3, 2)

    def set_frequency_compensation(self, gain):
        codes = reverse(LOOP_GAIN)
        self.set_bits(FOCCFG, codes[gain], 3, 2)

    def get_foc_post_k(self):
        return read_bits(self.cc1101.read(FOCCFG), 5, 1)

    def get_foc_limit(self):
        return read_bits(self.cc1101.read(FOCCFG), 6, 2)

    def set_foc_limit(self, saturation):
        codes = reverse(SATURATION_POINT)
        self.set_bits(FOCCFG, codes[saturation], 6, 2)

    # 0x1a, bit synchronization configuration

    def set_bs_pre_k(self, gain):
        codes = reverse(LOOP_GAIN)
        self.set_bits(BSCFG, codes[gain], 0, 2)

    def set_bs_pre_kp(self, gain):
        codes = reverse(LOOP_GAIN)
        self.set_bits(BSCFG, codes[gain], 2, 2)

    # 0x1b, 0x1c, 0x1d, AGC control

    def get_max_dvga_gain(self):
        return read_bits(self.cc1101.read(AGCCTRL2), 0, 2)

    def set_max_dvga_gain(self, gain):
        codes = reverse(DVGA_GAIN)
        self.set_bits(AGCCTRL2, codes[gain], 0, 2)

    def get_max_lna_gain(self):
        return read_bits(self.cc1101.read(AGCCTRL2), 2, 3)

    def get_magn_target(self):
        return read_bits(self.cc1101.read(AGCCTRL2), 5, 3)

    def set_magn_target(self, target):
        codes = reverse(MAGN_TARGET)
        self.set_bits(AGCCTRL2, codes[target], 5, 3)

    def get_agc_lna_priority(self):
        return read_bits(self.cc1101.read(AGCCTRL1), 1, 1)

    def set_agc_lna_priority(self, strat):
        self.set_bits(AGCCTRL1, strat, 1, 1)

    def get_carrier_sense_rel_thr(self):
        return read_bits(self.cc1101.read(AGCCTRL1), 2, 2)         

    def get_carrier_sense_abs_thr(self):
        return read_bits(self.cc1101.read(AGCCTRL1), 4, 4)         

    def get_hyst_level(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 0, 2)         

    def get_wait_time(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 2, 2)

    def set_wait_time(self, wait):
        codes = reverse(WAIT_TIME)
        self.set_bits(AGCCTRL0, codes[wait], 2, 2)

    def get_agc_freeze(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 4, 2)

    def get_filter_length(self):
        return read_bits(self.cc1101.read(AGCCTRL0), 6, 2)

    def set_filter_length(self, length):
        codes = reverse(FILTER_LENGTH)
        self.set_bits(AGCCTRL0, codes[length], 6, 2)

    # 0x1e, 0x1f, byte event0 timeout

    # 0x20, wake on radio control

    # 0x21, 0x22, front end rx configuration

    # 0x23, 0x24, 0x25, 0x26, frequency synthesizer calibration

    # 0x27, 0x28, rc oscillator configuration

    def reset(self):
        return self.cc1101.strobe(SRES)

    def get_marc_state(self):
        state = read_bits(self.cc1101.status(MARCSTATE), 3, 5)
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
