# DECA Challenge 2025

Modified version of the EEP1 CPU with half-precision floating point multiplication support, MOVR instruction and a minimal macro parser implementation in Python macro_parser.py

## half_precision_calculator.py

```
Usage: python3 half_precision_calculator.py <first operand> <second operand>
```

This Python script calculates the product of two half-precision floating point numbers either in decimal or hexadecimal format and displays the result in both decimal and hexadecimal format.

## macro_parser.py

```
Usage: python3 macro_parser.py <input file> <output file>
```

This Python script searches for macro definitions and parses them in `input file` then writes the parsed file to `output file`. The syntax is NASM like.

```asm
%macro MOV2 3
MOV %2, %3
MOV %1, %2
%endmacro
```

The macro definition starts with `%macro` and continues with the name of the macro `MOV2` and the number of arguments required for this macro which is `3` in this case and nth argument is accessed with `%n`. Arguments can be anything but it will assemble only if it is valid assembly code. In this example value or register in `%3` is MOVed into register `%2` and the value in register `%2`, is moved into register `%1`. Let's call `MOVV R1, R2, 16`, the parsed program would be:

```asm
MOV R2, 16
MOV R1, R2
```

## eepAssembler
