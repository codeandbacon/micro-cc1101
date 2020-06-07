
# responses

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

MODULATION_FORMAT = {
    0: '2FSK',
    1: 'GFSK',
    3: 'ASK',
    4: '4FSK',
    7: 'MSK'
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