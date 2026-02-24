def compile_asm(asm_code):
    """
    Simple ASM compiler for the 4-bit (base-4) logic system.
    
    Instruction Format (6 base-4 digits):
    [Instr0] [Instr1] [RNF0] [RNF1] [A] [B]
    
    Types:
    0: Arithmetic (Instr1 selects ADD=0, SUB=1, MUL=2, DIV=3)
    1: Logic      (Instr1 selects MIN=0, MAX=1, MOD=2, NOT=3)
    2: Code       (Instr1 selects LOAD=0, STORE=1, COPY=2, HLT=3)
    
    RNF (Register/None/Flag):
    0: Register
    1: Flag
    2: Immediate (None)
    
    A, B: Address (0-15) or Immediate Value (0-3)
    """
    
    instructions = {
        'ADD':   (0, 0),
        'SUB':   (0, 1),
        'MUL':   (0, 2),
        'DIV':   (0, 3),
        'MIN':   (1, 0),
        'MAX':   (1, 1),
        'MOD':   (1, 2),
        'NOT':   (1, 3),
        'LOAD':  (2, 0),
        'STORE': (2, 1),
        'COPY':  (2, 2),
        'HLT':   (2, 3),
    }

    machine_code = []
    
    for line in asm_code.split('\n'):
        line = line.split('--')[0].strip() # Remove comments
        if not line:
            continue
            
        parts = line.replace(',', ' ').split()
        op = parts[0].upper()
        
        if op not in instructions:
            raise ValueError(f"Unknown instruction: {op}")
            
        instr0, instr1 = instructions[op]
        rnf0, rnf1, a, b = 0, 0, 0, 0
        
        # Parse operands based on instruction type
        if op == 'HLT':
            pass
        elif op == 'LOAD':
            # LOAD R(A) Imm
            rnf0 = 0 # Reg
            rnf1 = 2 # Immediate
            a = int(parts[1][1:]) # R0 -> 0
            b = int(parts[2])     # 1 -> 1
        elif op == 'COPY':
            # COPY R(B) R(A) -> R(B) = R(A)
            rnf0 = 0
            rnf1 = 0
            a = int(parts[2][1:]) # Source
            b = int(parts[1][1:]) # Dest
        elif op == 'STORE':
            # STORE R(A) R(B)
            rnf0 = 0
            rnf1 = 0
            a = int(parts[1][1:])
            b = int(parts[2][1:])
        elif op in ['ADD', 'SUB', 'MUL', 'DIV', 'MIN', 'MAX', 'MOD']:
            # OP R(Dest) R(Src) -> R(Dest) = R(Dest) OP R(Src)
            # Our CPU uses A as Dest and B as Src
            rnf0 = 0
            rnf1 = 0
            a = int(parts[1][1:])
            b = int(parts[2][1:])
        elif op == 'NOT':
            # NOT R(A)
            rnf0 = 0
            rnf1 = 0
            a = int(parts[1][1:])
            b = 0
            
        machine_code.append((instr0, instr1, rnf0, rnf1, a, b))
        
    return machine_code
