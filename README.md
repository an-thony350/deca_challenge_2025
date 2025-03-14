# DECA Challenge 2025

Modified version of the EEP1 CPU with half-precision floating point multiplication support, MOVR instruction and a minimal macro parser implementation in Python macro_parser.py

## The Software

### half_precision_calculator.py

```
Usage: python3 half_precision_calculator.py <first operand> <second operand>
```

This Python script calculates the product of two half-precision floating point numbers either in decimal or hexadecimal format and displays the result in both decimal and hexadecimal format.

### macro_parser.py

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

### eepAssembler

## The Hardware

The standart IEEE 754 defines how scientific notation is implemented in
digital systems. For example, the half-precision binary16 floating point
number is implemented as in

###
Table [17](#tab:binary16){reference-type="ref"
reference="tab:binary16"}.

::: {#tab:binary16}
       sign   exponent                   fraction
  --- ------ ---------- --- --- --- --- ---------- --- --- --- --- --- --- --- --- ---
   N    0        0       1   1   1   1      0       0   0   0   0   0   0   0   0   0

  : N=1 in binary16 representation
:::

This number N is the floating point representation of 1 in binary 16. It
can be converted back to decimal. Let
$s = \text{sign} = \text{N[15]}$,
$e = \text{exponent} = \text{N[14:10]}$,
$f = \text{fraction} = \text{N[9:0]}$ and
$b = 2^{\text{sizeof(e) - 1}} = 2^4 - 1 = 15 = \text{base}$.

$$\left(-1\right)^s 2^{e - b} \left(1 + f\right) = \left(-1\right)^0 2^{\left(15 - 15\right)} \left(1 + 0\right) = \left(-1\right)^0 2^0 = 1$$

Here, $f = \sum_{i=0}^{9} \text{N[i]} 2^{-1-i}$ is the decimal
representation of the fraction. Now let's multiply two floating point
numbers A and B resulting in number C with signs
$s_\text{A}, s_\text{B}, s_\text{C}$; exponents
$e_\text{A}, e_\text{B}, e_\text{C}$; fractions
$f_\text{A}, f_\text{B}, f_\text{C}$.

$$\text{A} \times \text{B} = \left(-1\right)^{s_\text{A} + s_\text{B}} 2^{e_\text{A} + e_\text{B} - 2b} \left(1 + f_\text{A}\right) \left(1 + f_\text{B}\right) = \left(-1\right)^{s_\text{A} + s_\text{B}} 2^{e_\text{A} + e_\text{B} - 2b} \left(1 + f_\text{A} + f_\text{B} + f_\text{A} f_\text{B}\right)\\
    = \left(-1\right)^{s_\text{C}} 2^{e_\text{C} - b} \left(1 + f_\text{C}\right), \text{ then } s_\text{C} = \text{XOR($s_\text{A}, s_\text{B}$)}, e_\text{C} = e_\text{A} + e_\text{B} - b, f_\text{C} = f_\text{A} + f_\text{B} + f_\text{A} f_\text{B}$$

but the fraction part should be between 0 and 1 thus, if
$1 + f_\text{C} \ge 2$ then $1 + f_\text{C}$ is divided by 2 and the
fraction part of this new number $f^\prime_\text{C}$ is rounded to
10-bits to be saved in C. It is normally rounded to the neares 10-bit
number except when the exact result is in between two other numbers,
then the number is rounded so that the LSB is 0 i.e. even. The number is
divided by 2 therefore $e^\prime_\text{C} = e_\text{C} + 1$. Now let's
see the Issie implementation in [the figure below](#floatmul).
The sign bit is calculated with the XOR gate as discurssed earlier, the
exponent is calculated in the EXP sheet and the fraction part is
calculated in FRAC sheet. All of them are put together as OUT.

<a name="floatmul">![FLOATMUL sheet](/media/floatmul.png)</a>

The EXP sheet in [the figure below](#exp){reference-type="ref"
reference="fig:exp"} takes two exponents INA and INB and ADDs them. Also
there is EXPIN which increases the exponent by 1 if it was required to
divide the fraction by 2. Then the bias=15 is subtracted from the sum.
If the result is signed, negative, it can not be expressed in IEEE 754
format and should be rounded to 0. The sign bit which is the MSB is
checked and if it is not set the lower 5 bits of the result is returned
as the new exponent. This implements the equation
$e_\text{C} = e_\text{A} + e_\text{B} + \text{EXPIN} - b$.

<a name="exp">![EXP sheet](/media/exp.png)</a>

The FRAC sheet in [the figure below](#frac) multiplies two 10-bit
fractions to get a 20-bit result in FRACMUL sheet. Then, two 10-bit
fractions are added to get a 11-bit result $f_\text{A} + f_\text{B}$.
Now the sum and multiplication of the fractions are also added together
but since the MSB of the sum of fractions is the coefficient of the term
$2^0$ multiplication result should be aligned by adding a 0 as the
highest bit but instead 1 is added to implement $1 + f_\text{A}
f_\text{B}$ in order to implement both operations in a single stage.
Also the lowest 10 bits of the multiplication are not necessary for this
addition as the sum of fractions does not have these 10 bits. After the
sum and multiplication results are added the lowest 10 bits of the
multiplication results are merged back to be precise. The result of
these operations is
$1 + f_\text{A} + f_\text{B} + f_\text{A} f_\text{B} = 1 + f_\text{C}$.
Previously it was shown that if $1 + f_\text{C} \ge 2$ it should be
divided by two. This condition can be checked by the 21st bit of the
addition which is the coefficient of the term $2^1$. Let's investigate
the rounding for the condition where
$\left(1 + f_\text{C}\right)\text{[21]} = 0$. Firstly, as a 10-bit
fraction is required, lower 10 bits of the fraction are rounded to the
nearest number unless the exact answer is exactly in between two
numbers. This is done by adding b0000000000000111111111 to
$1 + f_\text{C}$ so if it is even $2^{-20}$ closer to the upper
number, it will be rounded to that. Otherwise higher 12 bits will remain
unchanged. If the number is exactly in between two numbers,
b0000000000001111111111 is added so if the 9th bit was set it would
round up the number and if it was not set then it will not be rounded
and since 9th bit is discarded there is no problem in doing that.
Finally the bits from 10 to 19 which make up the fraction are outputted.
If the 21st bit was set then the fraction would be made of the bits from
11 to 20 thus the constants have one more bit set to 1 at the ends and
the lower 11 bits of the number are checked for rounding conditions.

<a name="frac">![FRAC sheet](/media/frac.png)</a>

Now let's investigate the sheet FRACMUL in
[the figure below](#fracmul){reference-type="ref" reference="fig:fracmul"}.
It is very similar to regular multiplication except instead of shifting
B to the left it is shifted to the right as with each bit of A has a
negative exponent. Then B is multiplied with each bit of A and added
together, the result is a 20-bit number which is OUT.

<a name="fracmul">![FRACMUL sheet](/media/fracmul.png)</a>

These three subsheets are the components that make up the FLOATMUL
sheet. This new sheet is then added to the DATAPATH so that it can be
used with instruction MOVC2 to multiply two registers. The problem is
how to put the 16-bit numbers into the registers in the first place. For
example a 16-bit number can be moved into R0 with the program in
[the code below](###moving-0x67e9-into-r0-purely-with-software),

### MOVing 0x67E9 into R0 purely with software

```asm
MOV R0, 0x67
MOV R1, 0xE9
MOV R2, 0xFF
LSR R2, R2, 8
AND R1, R1, R2
LSL R0, R0, 8
ADD R0, R1
```

The R1 is ANDed with 0x00FF as the numbers are sign extended which is a
problem. Also this approach requires 3 registers and 7 lines of code,
instead new hardware could be used. MOVR sheet in
[the figure below](#movr) shifts INA 2 bytes to the left and sets the
lower 2 bytes to the lower 2 bytes of INB. This new hardware is added
to the datapath as MOVC7.

<a name="movr">![MOVR sheet](/media/movr.png)</a>

The code with this new instruction is in
[the code below](###moving-0x67e9-into-r0-with-movr)
Now only 2 registers and 3 lines of code are required.

### MOVing 0x67E9 into R0 with MOVR

```asm
MOV R0, 0x67
MOV R1, 0xE9
MOVC7 R0, R1
```

Still, writing three lines of code for a single task is excessive if
there will be lots of such operation. Most modern assemblers allow
definitions of macros but eepAssembler does not support it (yet) but a
small script can be used to preprocess the code before passing it to the
assembler. For this task, a minimal Python implementation is created. It
is a simplified version of NASM style multiline macro definition with a
syntax similar to NASM. The code with the macro definition is in
the [code block below](###moving-0x67E9-into-r0-with-macro-definition).

### MOVing 0x67E9 into R0 with macro definition 

```asm
%macro MOV16 4
MOV %1, %3
MOV %2, %4
MOVC7 %1, %2
%endmacro
MOV16 R0, R1, 0x67, 0xE9
```

Then the Python script is called, *python3 macro_parser.py $ < $input
file$ > $ $ < $output file$ > $*, and the output file can be assembled
by eepAssembler. The eepAssembler is modified to pass the files through
the macro parser before assembling them making the process seamless. The
final code for MOVing two 16-bit numbers into registers and multiplying
them according to IEEE 754 is in
[the code block below](###multiplying-two-half-precision-floating-point-numbers-0x67e9=2025-and-0x327b=0.2025)
. Finally; it is seen that
$2025 \times 0.2025 = 410$, or in half-precision floating point terms
$\text{0x67E9} \times \text{0x327B} = \text{0x5E68}$.

### multiplying two half-precision floating point numbers 0x67E9=2025 and 0x327B=0.2025

```asm
%macro MOV16 4
MOV %1, %3
MOV %2, %4
MOVC7 %1, %2
%endmacro
MOV16 R0, R1, 0x67, 0xE9
MOV16 R1, R2, 0x32, 0x7B
MOVC2 R0, R1
```
