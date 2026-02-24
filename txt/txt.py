MIN = min
MAX = max
NOT = lambda inA: 3 - inA
COM = lambda inA, inB: inA - inB if inA > inB else 0
MOD = lambda inA, inB: (inA + inB) % 4
EQ = lambda inA, inB: 3 if inA == inB else 0

"""
0 -> aritmetic
0 0 -> ADD
0 1 -> SUB
0 2 -> MUL
0 3 -> DIV


1 -> logic
1 0 -> MIN
1 1 -> MAX
1 2 -> MOD
1 3 -> NOT

2 -> code
2 0 -> LOAD
2 1 -> STORE
2 2 -> COPY
2 3 -> HLT

3 -> functions
3 0 -> RET
3 1 -> JMP
3 2 -> CALL
3 3 -> JCOND

"""


class ST:
    def __init__(self):
        self.inValue = 0

    def run(self, Val, Set):
        if Set > 0:
            self.inValue = Val

        return self.inValue


class RM1:
    def __init__(self):
        self.inValue = ST()
        self.inLock = ST()

    def run(self, inp, Set):
        LOCK = self.inLock.run(0, 0)

        LOCK = self.inLock.run(COM(MAX(LOCK, Set), MIN(LOCK, Set)), Set)
        OUT = self.inValue.run(inp, Set)

        return OUT, LOCK


class Counter:
    def __init__(self):
        self.reg = ST()

    def run(self, Inc, Load, Value):
        current = self.reg.run(0, 0)

        # Increment logic (mod 4)
        inc_value = MOD(current, MIN(1, Inc))

        # Select between incremented or current
        next_val = MAX(
            MIN(NOT(MIN(1, Load)), inc_value),
            MIN(MIN(1, Load), Value)
        )

        # Store if Inc or Load active
        write_enable = MAX(MIN(1, Inc), MIN(1, Load))
        self.reg.run(next_val, write_enable)

        return next_val


class RAM1:
    def __init__(self):
        self.m0 = RM1()
        self.m1 = RM1()
        self.m2 = RM1()
        self.m3 = RM1()

    def run(self, Adr, Set, Value):
        A, B, C, D = Adr4(Adr, Set)

        O0, _ = self.m0.run(Value, A)
        O1, _ = self.m1.run(Value, B)
        O2, _ = self.m2.run(Value, C)
        O3, _ = self.m3.run(Value, D)

        # Multiplex output
        OUT0 = MIN(O0, EQ(Adr, 0))
        OUT1 = MIN(O1, EQ(Adr, 1))
        OUT2 = MIN(O2, EQ(Adr, 2))
        OUT3 = MIN(O3, EQ(Adr, 3))

        return MAX(MAX(OUT0, OUT1), MAX(OUT2, OUT3))


class RAM2:
    def __init__(self):
        self.r0 = RAM1()
        self.r1 = RAM1()
        self.r2 = RAM1()
        self.r3 = RAM1()

    def run(self, Adr0, Adr1, Set, Value):
        A, B, C, D = Adr4(Adr1, Set)

        O0 = self.r0.run(Adr0, A, Value)
        O1 = self.r1.run(Adr0, B, Value)
        O2 = self.r2.run(Adr0, C, Value)
        O3 = self.r3.run(Adr0, D, Value)

        # Multiplex output
        OUT0 = MIN(O0, EQ(Adr1, 0))
        OUT1 = MIN(O1, EQ(Adr1, 1))
        OUT2 = MIN(O2, EQ(Adr1, 2))
        OUT3 = MIN(O3, EQ(Adr1, 3))

        return MAX(MAX(OUT0, OUT1), MAX(OUT2, OUT3))


def ROM_INSTR(instr0, instr1):
    A, B, C, D = Adr4(instr0, 3)
    A1, B1, C1, D1 = Adr4(instr1, C)

    R = MAX(MAX(MAX(A, B), MAX(A1, B1)), C1)

    Q1 = MIN(R, 1)

    return MAX(Q1, 0), 0


class RAM3:
    def __init__(self):
        self.r0 = RAM2()
        self.r1 = RAM2()
        self.r2 = RAM2()
        self.r3 = RAM2()
        self.C = COUNTER3()

    def _run(self, Adr0, Adr1, Adr2, Set, Value):
        A, B, C, D = Adr4(Adr2, Set)

        O0 = self.r0.run(Adr0, Adr1, A, Value)
        O1 = self.r1.run(Adr0, Adr1, B, Value)
        O2 = self.r2.run(Adr0, Adr1, C, Value)
        O3 = self.r3.run(Adr0, Adr1, D, Value)

        # Multiplex output
        OUT0 = MIN(O0, EQ(Adr2, 0))
        OUT1 = MIN(O1, EQ(Adr2, 1))
        OUT2 = MIN(O2, EQ(Adr2, 2))
        OUT3 = MIN(O3, EQ(Adr2, 3))

        return MAX(MAX(OUT0, OUT1), MAX(OUT2, OUT3))

    def advGet(self, st0, st1, st2, ADR0, ADR1, ADR2):
        val = self._run(ADR0, ADR1, ADR2, 0, 0)

        ADR01, ADR11, ADR21 = self.C.run(st0, st1, st2)

        return val, ADR01, ADR11, ADR21

    def run(self, AD0, AD1, AD2, Set, Var):
        self._run(AD0, AD1, AD2, Set, Var)

        if Set > 0:
            return

        ADR0, ADR1, ADR2 = self.C.run(0, 0, 0)

        instr1, A1, AA1, AAA1 = self.advGet(1, 0, 0, ADR0, ADR1, ADR2)
        instr2, A2, AA2, AAA2 = self.advGet(1, 0, 0, A1, AA1, AAA1)

        nx1, nx0 = ROM_INSTR(instr1, instr2)

        TEMP_LIST_TO_BE_REMOVED = [instr1, instr2]

        for _ in range(nx0 + (4 * nx1)):
            val, A2, AA2, AAA2 = self.advGet(1, 0, 0, A2, AA2, AAA2)
            TEMP_LIST_TO_BE_REMOVED.append(val)

        while len(TEMP_LIST_TO_BE_REMOVED) < 6:
            TEMP_LIST_TO_BE_REMOVED.append(0)

        return tuple(TEMP_LIST_TO_BE_REMOVED[:6])



def Adr4(Adr, Set):
    A = MIN(EQ(0, Adr), Set)
    B = MIN(EQ(1, Adr), Set)
    C = MIN(EQ(2, Adr), Set)
    D = MIN(EQ(3, Adr), Set)

    return A, B, C, D


def Adr16(Adr0, Adr1, Set):
    A, B, C, D = Adr4(Adr0, Set)

    A1, B1, C1, D1 = Adr4(Adr1, A)
    A2, B2, C2, D2 = Adr4(Adr1, B)
    A3, B3, C3, D3 = Adr4(Adr1, C)
    A4, B4, C4, D4 = Adr4(Adr1, D)

    return A1, B1, C1, D1, A2, B2, C2, D2, A3, B3, C3, D3, A4, B4, C4, D4


class RG16:
    def __init__(self):
        self.inST01 = ST()
        self.inST02 = ST()
        self.inST03 = ST()
        self.inST04 = ST()
        self.inST05 = ST()
        self.inST06 = ST()
        self.inST07 = ST()
        self.inST08 = ST()
        self.inST09 = ST()
        self.inST10 = ST()
        self.inST11 = ST()
        self.inST12 = ST()
        self.inST13 = ST()
        self.inST14 = ST()
        self.inST15 = ST()
        self.inST16 = ST()

    def run(self, Adr0, Adr1, Set, Value):
        A1, B1, C1, D1, A2, B2, C2, D2, A3, B3, C3, D3, A4, B4, C4, D4 = Adr16(Adr0, Adr1, 3)

        PreOut01 = MIN(self.inST01.run(Value, MIN(A1, Set)), A1)
        PreOut02 = MIN(self.inST02.run(Value, MIN(B1, Set)), B1)
        PreOut03 = MIN(self.inST03.run(Value, MIN(C1, Set)), C1)
        PreOut04 = MIN(self.inST04.run(Value, MIN(D1, Set)), D1)
        PreOut05 = MIN(self.inST05.run(Value, MIN(A2, Set)), A2)
        PreOut06 = MIN(self.inST06.run(Value, MIN(B2, Set)), B2)
        PreOut07 = MIN(self.inST07.run(Value, MIN(C2, Set)), C2)
        PreOut08 = MIN(self.inST08.run(Value, MIN(D2, Set)), D2)
        PreOut09 = MIN(self.inST09.run(Value, MIN(A3, Set)), A3)
        PreOut10 = MIN(self.inST10.run(Value, MIN(B3, Set)), B3)
        PreOut11 = MIN(self.inST11.run(Value, MIN(C3, Set)), C3)
        PreOut12 = MIN(self.inST12.run(Value, MIN(D3, Set)), D3)
        PreOut13 = MIN(self.inST13.run(Value, MIN(A4, Set)), A4)
        PreOut14 = MIN(self.inST14.run(Value, MIN(B4, Set)), B4)
        PreOut15 = MIN(self.inST15.run(Value, MIN(C4, Set)), C4)
        PreOut16 = MIN(self.inST16.run(Value, MIN(D4, Set)), D4)

        M1 = MAX(PreOut01, PreOut02)
        M2 = MAX(PreOut03, PreOut04)
        M3 = MAX(PreOut05, PreOut06)
        M4 = MAX(PreOut07, PreOut08)
        M5 = MAX(PreOut09, PreOut10)
        M6 = MAX(PreOut11, PreOut12)
        M7 = MAX(PreOut13, PreOut14)
        M8 = MAX(PreOut15, PreOut16)

        MM1 = MAX(M1, M2)
        MM2 = MAX(M3, M4)
        MM3 = MAX(M5, M6)
        MM4 = MAX(M7, M8)

        MMM1 = MAX(MM1, MM2)
        MMM2 = MAX(MM3, MM4)

        return MAX(MMM1, MMM2)


def HF_ADDER(A, B):
    C = MIN(1, MAX(COM(A, NOT(B)), COM(B, NOT(A))))

    Y = MOD(A, B)

    return C, Y


def HF_SUBTRACT(A, B):
    result = MOD(MOD(A, NOT(B)), 1)
    return MIN(1, COM(B, A)), result


def HF_DIVIDE(A, B):
    P1 = B
    P2 = MOD(B, B)
    P3 = MOD(P2, B)

    GE0 = 1
    GE1 = MIN(1, NOT(MIN(1, COM(P1, A))))
    GE2 = MIN(1, NOT(MIN(1, COM(P2, A))))
    GE3 = MIN(1, NOT(MIN(1, COM(P3, A))))

    Q0 = MIN(GE0, 0)
    Q1 = MIN(GE1, 1)
    Q2 = MIN(GE2, 2)
    Q3 = MIN(GE3, 3)

    quotient = MAX(MAX(Q0, Q1), MAX(Q2, Q3))

    _, remainder = HF_SUBTRACT(A, MOD(B, quotient))

    return remainder, quotient


def HF_MULTIPLY(A, B):
    def MUL_CARRY(A, B):
        highA = MIN(1, COM(A, 1))  # A >= 2
        highB = MIN(1, COM(B, 1))  # B >= 2
        return MIN(highA, highB)
    # Generate partial sums
    A1 = A
    A2 = MOD(A, A)
    A3 = MOD(A2, A)

    # Decode B
    B0 = MIN(1, EQ(B, 0))
    B1 = MIN(1, EQ(B, 1))
    B2 = MIN(1, EQ(B, 2))
    B3 = MIN(1, EQ(B, 3))

    # Select result
    P0 = MIN(B0, 0)
    P1 = MIN(B1, A1)
    P2 = MIN(B2, A2)
    P3 = MIN(B3, A3)

    result = MAX(MAX(P0, P1), MAX(P2, P3))

    return MUL_CARRY(A, B), result


def M_ALU(InA, InB, Instr0, Instr1, FLAG_REG: RG16, regA=0):
    Aa, Bb, Cc, Dd = Adr4(Instr0, 3)
    A, B, C, D = Adr4(Instr1, Aa)
    A1, B1, C1, D1 = Adr4(Instr1, Bb)

    Cout, OUT1 = HF_ADDER(InA, InB)
    Borrow, OUT2 = HF_SUBTRACT(InA, InB)
    X1, OUT3 = HF_MULTIPLY(InA, InB)
    X2, OUT4 = HF_DIVIDE(InA, InB)

    O1, O2, O3, O4 = MIN(A, OUT1), MIN(B, OUT2), MIN(C, OUT3), MIN(D, OUT4)

    FLAG = MAX(MAX(MIN(A, Cout), MIN(B, Borrow)), MAX(MIN(C, X1), MIN(D, X2)))
    # Store flag at (regA, 0) so CPU can find it
    FLAG_REG.run(regA, 0, Aa, FLAG)

    O1st = MAX(MAX(O1, O2), MAX(O3, O4))

    OUT5, OUT6, OUT7, OUT8 = MIN(InA, InB), MAX(InA, InB), MOD(InA, InB), NOT(MAX(InA, InB))

    O5, O6, O7, O8 = MIN(A1, OUT5), MIN(B1, OUT6), MIN(C1, OUT7), MIN(D1, OUT8)
    O2nd = MAX(MAX(O5, O6), MAX(O7, O8))

    return FLAG, MAX(O1st, O2nd)


class COUNTER:
    def __init__(self):
        self.inValue = ST()

    def run(self, ADD):
        val = self.inValue.run(0, 0)
        NEXT, NEW = HF_ADDER(val, ADD)

        return NEXT, self.inValue.run(NEW, 3)


class COUNTER3:
    def __init__(self):
        self.c1 = COUNTER()
        self.c2 = COUNTER()
        self.c3 = COUNTER()

    def run(self, add0, add1, add2):
        carry1, val1 = self.c1.run(add0)
        carry2, val2 = self.c2.run(MAX(carry1, add1))
        carry3, val3 = self.c3.run(MAX(carry2, add2))

        return val1, val2, val3


class CPU:
    def __init__(self, varReg: RG16, flagReg: RG16):
        self.var_reg = varReg
        self.flg_reg = flagReg

    def run(self, instr0, instr1, RNF0=0, RNF1=0, A=0, B=0):
        Aa, Bb, Cc, Dd = Adr4(instr0, 3)

        V1 = MAX(MAX(MIN(EQ(RNF0, 0), self.var_reg.run(A, 0, 0, 0)),
                 MIN(EQ(RNF0, 1), self.flg_reg.run(A, 0, 0, 0))),
                 MIN(EQ(RNF0, 2), A))

        V2 = MAX(MAX(MIN(EQ(RNF1, 0), self.var_reg.run(B, 0, 0, 0)),
                     MIN(EQ(RNF1, 1), self.flg_reg.run(B, 0, 0, 0))),
                 MIN(EQ(RNF1, 2), B))

        _, VAL0 = M_ALU(V1, V2, instr0, instr1, self.flg_reg, regA=A)

        self.var_reg.run(A, 0, MAX(Aa, Bb), VAL0)

        A1, B1, C1, D1 = Adr4(instr1, Cc)

        # LOAD or STORE: R(A) = V2
        self.var_reg.run(A, 0, MAX(A1, B1), V2)
        # COPY: R(B) = V1
        self.var_reg.run(B, 0, C1, V1)
        # HLT
        self.flg_reg.run(3, 3, D1, 3)

        #  A2, B2, C2, D2 = Adr4(instr1, D) -> functions


from compiler import compile_asm

def PC():
    with open("code.asm", "r") as f:
        asm_program = f.read()

    machine_code = compile_asm(asm_program)
    
    _RAM = RAM3()
    
    # Load machine code into RAM
    # Each instruction takes 6 slots in RAM (mapped by instruction pointer)
    for i, instr in enumerate(machine_code):
        # Flatten instruction (6 digits) and store in RAM
        # Our RAM is 3D: Adr0, Adr1, Adr2
        for j, val in enumerate(instr):
            # Calculate linear address j + i*6
            addr = i * 6 + j
            # Convert linear address to 3D address (4x4x4)
            a0 = addr % 4
            a1 = (addr // 4) % 4
            a2 = (addr // 16) % 4
            _RAM.run(a0, a1, a2, 3, val)

    _VAR_REG = RG16()
    _FLAG_REG = RG16()

    _CPU = CPU(_VAR_REG, _FLAG_REG)

    while _FLAG_REG.run(3, 3, 0, 0) == 0:
        RET = _RAM.run(0, 0, 0, 0, 0)
        _CPU.run(*RET)

    print("VAR_REG:")
    for Y in range(4):
        for X in range(4):
            print(_VAR_REG.run(X, Y, 0, 0))

        print(" ")

    print("FLAG_REG:")
    for Y in range(4):
        for X in range(4):
            print(_FLAG_REG.run(X, Y, 0, 0))

        print(" ")



def main():
    PC()


if __name__ == '__main__':
    main()


"""
0 -> var reg (R0, R1, R2, ...)
1 -> flag reg (ZERO, CARRY, ...)
2 -> real number (0, 1, 2, ...)

0 0 -> ADD
0 1 -> SUB
0 2 -> MUL
0 3 -> DIV

1 0 -> MIN
1 1 -> MAX
1 2 -> MOD
1 3 -> NOT

2 0 -> LOAD
2 1 -> STORE
2 2 -> COPY
2 3 -> HLT

3 0 -> CALL
3 1 -> JMP
3 2 -> JCMP
3 3 -> RET
"""
