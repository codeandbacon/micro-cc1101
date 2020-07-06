from micropython import const

# command strobes

SRES = const(0x30)
SFSTXON = const(0x31)
SXOFF = const(0x32)
SCAL = const(0x33)
SRX = const(0x34)
STX = const(0x35)
SIDLE = const(0x36)
SWOR = const(0x38)
SPWD = const(0x39)
SFRX = const(0x3a)
SFTX = const(0x3b)
SWORRST = const(0x3c)
SNOP = const(0x3d)

# PA table and FIFO

PATABLE = const(0x3e)
FIFO = const(0x3f)