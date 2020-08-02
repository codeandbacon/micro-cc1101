from micropython import const

SINGLE_WRITE = const(0x00)
BURST_WRITE = const(0x40)
SINGLE_READ = const(0x80)
BURST_READ = const(0xc0)
LOW = const(0x00)
HIGH = const(0x01)

# TODO: find a better name for this class
class EspSPI(object):

    def __init__(self, spi, cs, gdo0=None, gdo2=None):
        self.spi = spi
        self.cs = cs
        self.spi.init()
    
    def register_addr_space(self, address):
        if address > 0x2f:
            raise Exception('address is above configuration registers')

    def _spi_read(self, address, length=2):
        self.cs.value(LOW)
        res = self.spi.read(length, address)
        self.cs.value(HIGH)
        return res

    def _spi_write(self, write_buf):
        read_buf = bytearray(len(write_buf))
        self.cs.value(LOW)
        self.spi.write_readinto(write_buf, read_buf)
        self.cs.value(HIGH)
        return read_buf

    def read(self, address, status_byte=False):
        # self.register_addr_space(address)
        res = self._spi_read(address + SINGLE_READ)
        if status_byte:
            return res[1], res[0]
        return res[1]

    def burst_read(self, address, n, status_byte=False):
        # self.register_addr_space(address)
        res = self._spi_read(address + BURST_READ, length=n+1)
        if status_byte:
            return res[1:], res[0]
        return res[1:]

    def write(self, address, byte):
        # self.register_addr_space(address)
        write_buf = bytearray([address, byte])
        return self._spi_write(write_buf)
        
    def burst_write(self, address, databytes):
        # self.register_addr_space(address)
        address += BURST_WRITE
        write_buf = bytearray([address]) + databytes
        return self._spi_write(write_buf)

    def strobe(self, address):
        if address < 0x30 or address > 0x3d:
            raise Exception('not a strobe address')
        return self._spi_read(address)[1]

    def status(self, address):
        if address < 0xf0 or address > 0xfd:
            raise Exception('not a status register address')
        return self._spi_read(address)[1]