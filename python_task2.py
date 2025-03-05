import sys

# Constants for 6502
MEMORY_SIZE = 0x10000  # 64KB memory

# Registers for 6502
class CPU:
    def __init__(self):
        self.pc = 0x0000  # Program Counter
        self.sp = 0xFF    # Stack Pointer
        self.a = 0        # Accumulator
        self.x = 0        # X Register
        self.y = 0        # Y Register
        self.status = 0   # Status Register (Processor Status)
        self.memory = [0] * MEMORY_SIZE  # Memory Array

    def reset(self):
        self.pc = 0x0600  # Example reset address
        self.sp = 0xFF
        self.a = 0
        self.x = 0
        self.y = 0
        self.status = 0x00  # Set the status flags to zero

    def load_program(self, program: bytes, start_address: int = 0x0600):
        for i, byte in enumerate(program):
            self.memory[start_address + i] = byte
        self.pc = start_address

    def fetch(self):
        # Fetch the next byte from memory (opcode)
        return self.memory[self.pc]

    def execute(self):
        opcode = self.fetch()
        self.pc += 1
        if opcode == 0xA9:  # LDA Immediate (Load Accumulator)
            self.lda_immediate()
        elif opcode == 0xA2:  # LDX Immediate (Load X Register)
            self.ldx_immediate()
        # Add other opcodes here...

    def lda_immediate(self):
        # LDA #value - Load the Accumulator with an immediate value
        self.a = self.memory[self.pc]
        self.pc += 1

    def ldx_immediate(self):
        # LDX #value - Load the X Register with an immediate value
        self.x = self.memory[self.pc]
        self.pc += 1

    def print_state(self):
        print(f"PC: {hex(self.pc)} SP: {hex(self.sp)} A: {hex(self.a)} X: {hex(self.x)} Y: {hex(self.y)} Status: {bin(self.status)}")


def load_binary(file_path: str):
    with open(file_path, 'rb') as f:
        return f.read()

def main():
    # Create CPU instance
    cpu = CPU()
    cpu.reset()

    # Load binary file (replace with actual binary file)
    program = load_binary('path_to_your_program.bin')
    cpu.load_program(program)

    # Run the emulator for a few cycles
    for _ in range(10):  # Run for 10 cycles (adjust as needed)
        cpu.execute()
        cpu.print_state()

if __name__ == "__main__":
    main()
