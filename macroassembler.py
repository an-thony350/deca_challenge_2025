import sys
import struct

file_in = sys.argv[1]
file_out = sys.argv[2]

def float_to_hex(n):
    bits = struct.pack('e', float(n))
    return hex(struct.unpack('H', bits)[0])

def floatmov(r1, r2, n):
    n_hex = float_to_hex(n).upper()
    numhex = list()
    numhex.append(n_hex[2:4])
    numhex.append(n_hex[4:])
    return (f'MOV {r1}, 0x{numhex[0]}\n'
            f'MOV {r2}, 0x{numhex[1]}\n'
            f'LSL {r1}, {r1}, 8\n'
            f'MOVC7 {r1}, {r2}\n')

keywords = {
        'FLOATMOV': floatmov
        }

lines_out = []

with open(file_in, 'r') as file:
    for line in file.readlines():
        for key in keywords.keys():
            if line.upper().startswith(key):
                lines_out.append(keywords[key](line.split()[1].strip(","), line.split()[2].strip(","), line.split()[3].strip(",")))
            else:
                lines_out.append(line)
    file.close()

with open(file_out, 'w') as file:
    file.write("".join(lines_out))
    file.close()
