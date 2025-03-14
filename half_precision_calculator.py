import sys
import struct

argv = sys.argv

if len(argv) != 3:
    print(f'Usage: {argv[0]} <first operand> <second operand>')
    exit()

ops = list()

for op in argv[1:]:
    try:
        try:
            ops.append(float(op))
        except:
            ops.append(struct.unpack('e', struct.pack('H', int(op, 0)))[0])
    except:
        err = f'{op} is not a float or half-precision floating point'
        raise ValueError(err)

p = ops[0]*ops[1]

p_hex = hex(struct.unpack('H', struct.pack('e', p))[0]).upper()

print(f'{argv[1]} X {argv[2]} = {p} = {p_hex}')
