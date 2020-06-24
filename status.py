from micropython import const

# status registers

PARTNUM = const(0xf0)
VERSION = const(0xf1)
FREQEST = const(0xf2)
LQI = const(0xf3)
RSSI = const(0xf4)
MARCSTATE = const(0xf5)
WORTIME1 = const(0xf6)
WORTIME0 = const(0xf7)
PKTSTATUS = const(0xf8)
VCO_VC_DAC = const(0xf9)
TXBYTES = const(0xfa)
RXBYTES = const(0xfb)
RCCTRL1_STATUS = const(0xfc)
RCCTRL0_STATUS = const(0xfd)