import sys
import struct

if len(sys.argv) != 3:
    print(f'Usage: python3 {sys.argv[0]} <input filename> <output filename>')
    exit()

file_in = sys.argv[1]
file_out = sys.argv[2]

reserved = [
        'MOV',
        'ADD',
        'SUB',
        'ADC',
        'SBC',
        'AND',
        'CMP',
        'LSL',
        'LSR',
        'ASR',
        'XSR'
        ]


macro_lock = False
current_macro = ''
macros = {}
lines_out = []

with open(file_in, 'r') as file:
    for line in file.readlines():
        for key in keywords.keys():
            if line.upper().startswith('%MACRO'):
                argv = line.split(' ')
                if macro_lock:
                    raise SyntaxError('can not define macro in macro')
                else:
                    current_macro = argv[1].upper()
                    if current_macro not in reserved:
                        macros[current_macro] = [int(argv[2].strip()), '']
                        macro_lock = True
                    else:
                        raise ValueError(f'{current_macro} is a reserved instruction')
                        exit()

                if len(argv) != 3:
                    raise SyntaxError('macro definition syntax: %macro <macro name> <macro argument count>')
                    exit()

            elif line.upper().startswith('%ENDMACRO'):
                macro_lock = False

            elif macro_lock:
                macros[current_macro][1] += line
            
            elif (line.split(' ')[0].upper() in macros.keys()):
                argv = line[:-1].strip().split(' ')
                for i in range(len(argv)):
                    argv[i] = argv[i].strip(',').strip(' ')
                argc = len(argv) - 1
                macro = argv[0].upper()
                argc_def = macros[macro][0]
                if argc == argc_def:
                    replacement = macros[macro][1]
                    for i in range(1, argc+1):
                        replacement = replacement.replace(f'%{i}', argv[i])
                    lines_out.append(replacement)
                else:
                    raise ValueError(f'{macro} takes {argc_def} arguments, {argc} given')
                    exit()

            else:
                lines_out.append(line)
    file.close()

if macro_lock:
    raise SyntaxError('%endmacro never used')

with open(file_out, 'w') as file:
    file.write(''.join(lines_out))
    file.close()
