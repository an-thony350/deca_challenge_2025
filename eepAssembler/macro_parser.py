import sys
import struct

if len(sys.argv) != 3:
    print(f'Usage: python3 {sys.argv[0]} <input file> <output file>')
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
i = 0

with open(file_in, 'r') as file:
    lines = file.readlines()
    while i < len(lines):
        line = lines[i].strip()
        if line.upper().startswith('%MACRO'):
            argv = line.split(' ')
            if len(argv) != 3:
                raise SyntaxError('Error in file \'{file_in}\' line {line}\nmacro definition syntax: %macro <macro name> <macro argument count>')
                exit()

            if macro_lock:
                raise SyntaxError('Error in file \'{file_in}\' line {line}\ncan not define macro in macro')

            else:
                current_macro = argv[1].upper()
                if current_macro not in reserved:
                    macros[current_macro] = [int(argv[2].strip()), '']
                    lines[i] = ''
                    macro_lock = True
                else:
                    raise ValueError(f'Error in file \'{file_in}\' line {line}\n{current_macro} is a reserved instruction')
                    exit()

        elif line.upper().startswith('%ENDMACRO'):
            lines[i] = ''
            macro_lock = False

        elif macro_lock:
            lines[i] = ''
            macros[current_macro][1] += line + "\n"

        elif (line.strip().split(' ')[0].upper() in macros.keys()):
            argv = line.split(' ')
            for j in range(len(argv)):
                argv[j] = argv[j].strip(',').strip(' ')
            argc = len(argv) - 1
            macro = argv[0].upper()
            argc_def = macros[macro][0]
            if argc == argc_def:
                replacement = macros[macro][1]
                for j in range(1, argc+1):
                    replacement = replacement.replace(f'%{j}', argv[j])
                replacement = replacement.strip().split('\n')
                for j in range(len(replacement)):
                    replacement[j] += '\n'
                lines = lines[:i] + replacement + lines[i+1:]
                i-=1

            else:
                raise ValueError(f'Error in file \'{file_in}\' line {line}\n{macro} takes {argc_def} arguments, {argc} given')

        i+=1

    if macro_lock:
        raise SyntaxError('Error in file \'{file_in}\' line {line}\n%endmacro never used')
        exit()

    with open(file_out, 'w') as file_o:
        file_o.write(''.join(lines))
        file_o.close()

    file.close()
