
# responses

GDO_MODE = {
    0: 'RX_GTE_FIFO',
    1: 'RX_GTE_FIFO_OR_END',
    6: 'SYNC_WORD',
    11: 'SERIAL_CLOCK',
    41: 'CHIP_READY',
    63: 'CLK_XOSC_192'
}

FIFO_THRESHOLDS = {
    0: (61, 4),
    1: (57, 8),
    2: (53, 12),
    3: (49, 16),
    4: (45, 20),
    5: (41, 24),
    6: (37, 28),
    7: (33, 32),
    8: (29, 36),
    9: (25, 40),
    10: (21, 44),
    11: (17, 48),
    12: (13, 52),
    13: (9, 56),
    14: (5, 60),
    15: (1, 64)
}

ADDRESS_CHECK = {
    0: 'NO_ADDR_CHECK',
    1: 'ADDR_CHECK_NO_BROADCAST',
    2: 'ADDR_CHECK_0_BROADCAST',
    3: 'ADDR_CHECK_0_255_BROADCAST'
}

PACKET_FORMAT = {
    0: 'NORMAL',
    1: 'SYNC',
    2: 'RANDOM',
    3: 'ASYNC'
}

DVGA_GAIN = {
    0: 'ALL',
    1: 'NOT_HIGHEST',
    2: 'NOT_2_HIGHEST',
    3: 'NOT_3_HIGHEST'
}

WAIT_TIME = {
    0: 8,
    1: 16,
    2: 24,
    3: 32
}

FILTER_LENGTH = {
    0: 8,
    1: 16,
    2: 32,
    3: 64
}

MAGN_TARGET = {
    0: 24,
    1: 27,
    2: 30,
    3: 33,
    4: 36,
    5: 38,
    6: 40,
    7: 42
}

QUALIFIER_MODE = {
    0: 'NO_PRE_SYNC',
    1: '15_16_SYNC',
    2: '16_16_SYNC',
    3: '30_32_SYNC',
    4: 'NO_PRE_SYNC_CARRIER',
    5: '15_16_SYNC_CARRIER',
    6: '16_16_SYNC_CARRIER',
    7: '30_32_SYNC_CARRIER',
}

CCA_MODE = {
    0: 'ALWAYS',
    1: 'RSSI_BELOW_TH',
    2: 'UNLESS_RX',
    3: 'RSSI_BELOW_TH_UNLESS_RX'
}

OFF_MODE = {
    0: 'IDLE',
    1: 'FSTXON',
    2: 'TX',
    3: 'RX'
}

MODULATION_FORMAT = {
    0: '2FSK',
    1: 'GFSK',
    3: 'ASK',
    4: '4FSK',
    7: 'MSK'
}

AUTOCAL = {
    0: 'NEVER',
    1: 'FROM_IDLE',
    2: 'TO_IDLE',
    3: 'EVERY_4'
}

SATURATION_POINT = {
    0: '0',
    1: 'BW/8',
    2: 'BW/4',
    3: 'BW/2'
}

LOOP_GAIN = {
    0: 'K',
    1: '2K',
    2: '3K',
    3: '4K'
}

PO_TIMEOUT = {
    0: 1,
    1: 16,
    2: 64,
    3: 256
}

CHANNEL_BANDWIDTH = {
    0: 812500,
    1: 650000,
    2: 541667,
    3: 464286,
    4: 406250,
    5: 325000,
    6: 270833,
    7: 232143,
    8: 203125,
    9: 162500,
    10: 135417,
    11: 116071,
    12: 101563,
    13: 81250,
    14: 67708,
    15: 58035
}

MARC_STATES = {
    0: 'SLEEP',
    1: 'IDLE',
    2: 'XOFF',
    3: 'VCOON_MC',
    4: 'REGON_MC',
    5: 'MANCAL',
    6: 'VCOON',
    7: 'REGON',
    8: 'STARTCAL',
    9: 'BWBOOST',
    10: 'FS_LOCK',
    11: 'IFADCON',
    12: 'ENDCAL',
    13: 'RX',
    14: 'EX_END',
    15: 'RX_RST',
    16: 'TXRX_SWITCH',
    17: 'RXFIFO_OVERFLOW',
    19: 'TX',
    20: 'TX_END',
    21: 'RXTX_SWITCH',
    22: 'TXFIFO_UNDERFLOW'
}

PREAMBLE_BITS = {
    0: 2,
    1: 3,
    2: 4,
    3: 6,
    4: 8,
    5: 12,
    6: 16,
    7: 24
}

PACKET_LENGTH_CONF = {
    0: 'FIXED',
    1: 'VARIABLE',
    2: 'INFINITE'
}