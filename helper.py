
BITS_F = '{0:08b}'

def reverse(codes):
    return dict([(v, k) for k, v in codes.items()])

def to_bits_string(value):
    return str.format(BITS_F, value)

def read_bits(value, start=0, length=8):
    return int(to_bits_string(value)[start:start+length], 2)