from status import *

RESP = {
    MARCSTATE: { # 0x35
        (0, 2): None,
        (3, 7): {
            0: 'SLEEP',
            1: 'IDLE',
            2: 'XOFF',
            22: 'TXFIFO_UNDERFLOW'
        }
    },
    TXBYTES: {
        0: 'TXFIFO_UNDERFLOW',
        (1, 7): 'NUM_TXBYTES'
    }

}

def read_resp(code, resp):
    if resp is not str:
        resp = '{:08b}'.format(resp)
    for bits, value in RESP[code].items():
        if type(bits) is tuple:
            r = resp[bits[0]:bits[1]]
            if value is None:
                continue
            elif value is str:
                print('{}: {}'.format(value, r))
            else:
                print(value[int(r, 2)])
        else:
            print('{}: {}'.format(value, resp[bits]))