import pygame
import random
import time
import sys

# CHIP-8 Emulator Class
class Chip8Emulator:
    def __init__(self):
        # Initialize memory, registers, stack, display, etc.
        self.memory = [0] * 4096  # 4KB of memory
        self.v = [0] * 16  # 16 general-purpose registers (V0-VF)
        self.i = 0  # Index register
        self.pc = 0x200  # Program counter starts at 0x200
        self.stack = []  # Stack to store return addresses
        self.sp = 0  # Stack pointer
        self.delay_timer = 0  # Delay timer
        self.sound_timer = 0  # Sound timer
        self.gfx = [[0] * 64 for _ in range(32)]  # 64x32 pixel display
        self.keys = [0] * 16  # Keypad state (16 keys)

        # Fontset for CHIP-8
        self.fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x20, 0x20,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0x80   # E
        ]
        self.load_fontset()

        # Initialize Pygame for graphical output
        pygame.init()
        self.screen = pygame.display.set_mode((64 * 10, 32 * 10))  # 10x scale for visibility
        pygame.display.set_caption("CHIP-8 Emulator")
        self.clock = pygame.time.Clock()

    def load_fontset(self):
        # Load fontset into memory starting at location 0x50
        for i in range(len(self.fontset)):
            self.memory[0x50 + i] = self.fontset[i]

    def load_program(self, program):
        # Load a program into memory
        for i in range(len(program)):
            self.memory[0x200 + i] = program[i]

    def fetch(self):
        # Fetch the current instruction (2 bytes)
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        self.pc += 2
        return opcode

    def decode_execute(self, opcode):
        # Decode and execute the opcode
        nnn = opcode & 0x0FFF
        nn = opcode & 0x00FF
        n = opcode & 0x000F
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4

        # Handle opcodes based on their first nibble
        if opcode == 0x00E0:  # CLS - Clear screen
            self.gfx = [[0] * 64 for _ in range(32)]
        elif opcode == 0x00EE:  # RET - Return from subroutine
            self.pc = self.stack.pop()
        elif opcode == 0x1NNN:  # JP addr - Jump to address NNN
            self.pc = nnn
        elif opcode == 0x2NNN:  # CALL addr - Call subroutine at NNN
            self.stack.append(self.pc)
            self.pc = nnn
        elif opcode == 0x3XNN:  # SE Vx, byte - Skip next instruction if Vx == NN
            if self.v[x] == nn:
                self.pc += 2
        elif opcode == 0x4XNN:  # SNE Vx, byte - Skip next instruction if Vx != NN
            if self.v[x] != nn:
                self.pc += 2
        elif opcode == 0x5XY0:  # SE Vx, Vy - Skip next instruction if Vx == Vy
            if self.v[x] == self.v[y]:
                self.pc += 2
        elif opcode == 0x6XNN:  # LD Vx, byte - Set Vx = NN
            self.v[x] = nn
        elif opcode == 0x7XNN:  # ADD Vx, byte - Set Vx = Vx + NN
            self.v[x] += nn
        elif opcode == 0x8XY0:  # LD Vx, Vy - Set Vx = Vy
            self.v[x] = self.v[y]
        elif opcode == 0x8XY1:  # OR Vx, Vy - Set Vx = Vx OR Vy
            self.v[x] |= self.v[y]
        elif opcode == 0x8XY2:  # AND Vx, Vy - Set Vx = Vx AND Vy
            self.v[x] &= self.v[y]
        elif opcode == 0x8XY3:  # XOR Vx, Vy - Set Vx = Vx XOR Vy
            self.v[x] ^= self.v[y]
        elif opcode == 0x8XY4:  # ADD Vx, Vy - Set Vx = Vx + Vy (carry flag)
            result = self.v[x] + self.v[y]
            self.v[0xF] = 1 if result > 255 else 0
            self.v[x] = result & 0xFF
        elif opcode == 0x8XY5:  # SUB Vx, Vy - Set Vx = Vx - Vy (borrow flag)
            self.v[0xF] = 1 if self.v[x] > self.v[y] else 0
            self.v[x] -= self.v[y]
        elif opcode == 0x8XY6:  # SHR Vx {, Vy} - Set Vx = Vx SHR 1
            self.v[0xF] = self.v[x] & 0x1
            self.v[x] >>= 1
        elif opcode == 0x8XY7:  # SUBN Vx, Vy - Set Vx = Vy - Vx (borrow flag)
            self.v[0xF] = 1 if self.v[y] > self.v[x] else 0
            self.v[x] = self.v[y] - self.v[x]
        elif opcode == 0x8XYE:  # SHL Vx {, Vy} - Set Vx = Vx SHL 1
            self.v[0xF] = (self.v[x] >> 7) & 0x1
            self.v[x] <<= 1
        elif opcode == 0x9XY0:  # SNE Vx, Vy - Skip next instruction if Vx != Vy
            if self.v[x] != self.v[y]:
                self.pc += 2
        elif opcode == 0xANNN:  # LD I, addr - Set I = NNN
            self.i = nnn
        elif opcode == 0xBNNN:  # JP V0, addr - Jump to address NNN + V0
            self.pc = nnn + self.v[0]
        elif opcode == 0xCXNN:  # RND Vx, byte - Set Vx = random byte AND NN
            self.v[x] = random.randint(0, 255) & nn
        elif opcode == 0xDXYN:  # DRW Vx, Vy, N - Draw sprite at (Vx, Vy)
            self.v[0xF] = 0
            for row in range(n):
                sprite = self.memory[self.i + row]
                for col in range(8):
                    if (sprite & (0x80 >> col)) != 0:
                        if self.gfx[(self.v[y] + row) % 32][(self.v[x] + col) % 64] == 1:
                            self.v[0xF] = 1  # Pixel collision
                        self.gfx[(self.v[y] + row) % 32][(self.v[x] + col) % 64] ^= 1
        elif opcode == 0xEX9E:  # SKP Vx - Skip next instruction if key Vx is pressed
            if self.keys[self.v[x]] != 0:
                self.pc += 2
        elif opcode == 0xEXA1:  # SKNP Vx - Skip next instruction if key Vx is not pressed
            if self.keys[self.v[x]] == 0:
                self.pc += 2
        elif opcode == 0xFX07:  # LD Vx, DT - Set Vx = delay timer
            self.v[x] = self.delay_timer
        elif opcode == 0xFX0A:  # LD Vx, K - Wait for key press, store in Vx
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        for i in range(16):
                            if event.key == pygame.K_1 + i:  # Modify this for your specific keys
                                self.v[x] = i
                                waiting = False
        elif opcode == 0xFX15:  # LD DT, Vx - Set delay timer = Vx
            self.delay_timer = self.v[x]
        elif opcode == 0xFX18:  # LD ST, Vx - Set sound timer = Vx
            self.sound_timer = self.v[x]
        elif opcode == 0xFX1E:  # ADD I, Vx - Set I = I + Vx
            self.i += self.v[x]
        elif opcode == 0xFX29:  # LD F, Vx - Set I = location of sprite for digit Vx
            self.i = self.v[x] * 5
        elif opcode == 0xFX33:  # LD B, Vx - Store BCD representation of Vx in memory
            self.memory[self.i] = self.v[x] // 100
            self.memory[self.i + 1] = (self.v[x] // 10) % 10
            self.memory[self.i + 2] = self.v[x] % 10
        elif opcode == 0xFX55:  # LD [I], V0-Vx - Store registers V0-Vx in memory starting at I
            for i in range(x + 1):
                self.memory[self.i + i] = self.v[i]
        elif opcode == 0xFX65:  # LD V0-Vx, [I] - Read registers V0-Vx from memory starting at I
            for i in range(x + 1):
                self.v[i] = self.memory[self.i + i]

    def update_timers(self):
        # Decrease the timers if they are greater than 0
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def draw_graphics(self):
        # Render the graphics
        for y in range(32):
            for x in range(64):
                color = (255, 255, 255) if self.gfx[y][x] == 1 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, (x * 10, y * 10, 10, 10))
        pygame.display.flip()

    def run(self):
        # Main emulation loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.keys[1] = 1
                    # Handle more keys similarly...

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_1:
                        self.keys[1] = 0
                    # Handle more keys similarly...

            opcode = self.fetch()
            self.decode_execute(opcode)
            self.update_timers()
            self.draw_graphics()
            self.clock.tick(60)  # Emulate at 60Hz


# Running the emulator
if __name__ == "__main__":
    emulator = Chip8Emulator()
    
    # Example: Load a CHIP-8 program (binary file or raw data)
    # Here, we're loading an empty program for demonstration.
    program = [0x00] * 1024  # Example program
    emulator.load_program(program)
    
    emulator.run()
