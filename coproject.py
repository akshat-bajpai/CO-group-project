# RISC-V Assembler for a subset of RV32I instructions

import sys

# Register mapping
registers = {
    'zero': '00000', 'ra': '00001', 'sp': '00010', 'gp': '00011', 'tp': '00100',
    't0': '00101', 't1': '00110', 't2': '00111', 's0': '01000', 's1': '01001',
    'a0': '01010', 'a1': '01011', 'a2': '01100', 'a3': '01101', 'a4': '01110',
    'a5': '01111', 'a6': '10000', 'a7': '10001', 's2': '10010', 's3': '10011',
    's4': '10100', 's5': '10101', 's6': '10110', 's7': '10111', 's8': '11000',
    's9': '11001', 's10': '11010', 's11': '11011', 't3': '11100', 't4': '11101',
    't5': '11110', 't6': '11111'
}

# Opcode, funct3, funct7 for instructions
instruction_formats = {
    'R': {'add': ('0110011', '000', '0000000'), 'sub': ('0110011', '000', '0100000'),
          'or': ('0110011', '110', '0000000'), 'srl': ('0110011', '101', '0000000')},

    'I': {'addi': ('0010011', '000'), 'lw': ('0000011', '010'), 'jalr': ('1100111', '000')},

    'S': {'sw': ('0100011', '010')},

    'B': {'beq': ('1100011', '000'), 'bne': ('1100011', '001')},

    'J': {'jal': ('1101111', None)}
}

labels = {}  # Dictionary to store label addresses
binary_code = []  # List to store generated binary instructions

# Read input file
with open("read.txt", "r") as file:
    lines = file.readlines()

# First pass: Identify label positions
pc = 0  # Program Counter (address of instruction)
for line in lines:
    line = line.strip()
    if not line:
        continue  # Skip empty lines
    parts = line.replace(",", " ").split()  # Fix comma handling
    if parts[0][-1] == ":":  # Label detected
        labels[parts[0][:-1]] = pc  # Store label name without ":"
    else:
        pc += 4  # Increment PC for each instruction

# Second pass: Convert assembly to binary
pc = 0
for line in lines:
    line = line.strip()
    if not line:
        continue  # Skip empty lines

    parts = line.replace(",", " ").split()
    if parts[0][-1] == ":":  # If a label is at the beginning of a line
        parts = parts[1:]  # Remove label part

    if not parts:
        continue

    instr = parts[0]

    if instr in instruction_formats['R']:  # R-type
        rd, rs1, rs2 = registers[parts[1]], registers[parts[2]], registers[parts[3]]
        opcode, funct3, funct7 = instruction_formats['R'][instr]
        binary = f"{funct7}{rs2}{rs1}{funct3}{rd}{opcode}"

    elif instr in instruction_formats['I']:  # I-type (addi, lw, jalr)
        rd = registers[parts[1]]
        if instr == "lw":  # lw a4, 30(s3) -> rd = a4, rs1 = s3, imm = 30
            imm, reg = parts[2].split('(')
            rs1 = registers[reg[:-1]]  # Remove closing parenthesis
            imm = int(imm)
        else:
            rs1 = registers[parts[2]]
            imm = int(parts[3])

        opcode, funct3 = instruction_formats['I'][instr]
        imm_bin = format(imm & 0xFFF, '012b')  # Sign extend
        binary = f"{imm_bin}{rs1}{funct3}{rd}{opcode}"

    elif instr in instruction_formats['S']:  # S-type (sw)
        rs2 = registers[parts[1]]
        imm, reg = parts[2].split('(')
        rs1 = registers[reg[:-1]]  # Extract base register
        imm = int(imm)
        opcode, funct3 = instruction_formats['S'][instr]
        imm_bin = format(imm & 0xFFF, '012b')  # Sign extend
        imm_high, imm_low = imm_bin[:7], imm_bin[7:]
        binary = f"{imm_high}{rs2}{rs1}{funct3}{imm_low}{opcode}"

    elif instr in instruction_formats['B']:  # B-type (beq, bne)
        rs1, rs2 = registers[parts[1]], registers[parts[2]]
        offset = labels[parts[3]] - pc if parts[3] in labels else int(parts[3])
        opcode, funct3 = instruction_formats['B'][instr]
        imm_bin = format(offset & 0x1FFF, '013b')  # Sign extend
        imm = imm_bin[0] + imm_bin[2:8] + imm_bin[8:12] + imm_bin[1]
        binary = f"{imm[0]}{imm[2:8]}{rs2}{rs1}{funct3}{imm[8:12]}{imm[1]}{opcode}"

    elif instr in instruction_formats['J']:  # J-type (jal)
        rd = registers[parts[1]]
        offset = labels[parts[2]] - pc if parts[2] in labels else int(parts[2])
        opcode, _ = instruction_formats['J'][instr]
        imm_bin = format(offset & 0xFFFFF, '021b')  # Sign extend
        imm = imm_bin[0] + imm_bin[10:20] + imm_bin[9] + imm_bin[1:9]
        binary = f"{imm}{rd}{opcode}"

    else:
        print(f"Error: Unrecognized instruction - {line}")
        continue  # Skip unrecognized instruction

    binary_code.append(binary)
    pc += 4  # Increment PC

# Write output file
with open("output.txt", "w") as file:
    for binary in binary_code:
        file.write(binary + "\n")

print("Assembly successfully converted to binary and saved in output.txt")
