import pygame
import time
import pickle

class CHIP8:
    def __init__(self):
        self.memory = [0] * 4096  # 4K memory
        self.V = [0] * 16  # 16 general-purpose registers
        self.I = 0  # Index register
        self.PC = 0x200  # Program counter starts at 0x200
        self.SP = 0  # Stack pointer
        self.stack = [0] * 16  # Stack with 16 levels
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * 16  # Keypad with 16 keys
        self.display = [[0] * 64 for _ in range(32)]  # 64x32 display
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
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # B
            0xF0, 0x80, 0xF0, 0x80, 0x80,  # C
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
        ]
        self.load_fonts()

    def load_fonts(self):
        # Load fontset into memory starting at address 0x50
        for i in range(0, len(self.fontset)):
            self.memory[0x50 + i] = self.fontset[i]

    def load_program(self, program):
        # Load the program into memory starting at 0x200
        for i in range(len(program)):
            self.memory[0x200 + i] = program[i]

    def handle_input(self):
        # Handle input using pygame
        keys = pygame.key.get_pressed()
        self.keypad = [
            keys[pygame.K_1], keys[pygame.K_2], keys[pygame.K_3], keys[pygame.K_4],
            keys[pygame.K_q], keys[pygame.K_w], keys[pygame.K_e], keys[pygame.K_r],
            keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d], keys[pygame.K_f],
            keys[pygame.K_z], keys[pygame.K_x], keys[pygame.K_c], keys[pygame.K_v]
        ]

    def emulate_cycle(self):
        # Fetch
        opcode = self.memory[self.PC] << 8 | self.memory[self.PC + 1]
        self.PC += 2  # Increment the program counter by 2 to get to the next opcode

        # Decode & Execute
        if opcode == 0x00E0:  # CLS (Clear screen)
            self.display = [[0] * 64 for _ in range(32)]  # Clear the display
        elif opcode == 0x00EE:  # RET (Return from subroutine)
            self.SP -= 1  # Pop the return address from the stack
            self.PC = self.stack[self.SP]
        # Additional opcode cases should be added here

    def draw_graphics(self):
        # Create a pygame window
        screen = pygame.display.set_mode((640, 320))  # 10px per pixel
        for row in range(32):
            for col in range(64):
                if self.display[row][col] == 1:
                    pygame.draw.rect(screen, (255, 255, 255), (col * 10, row * 10, 10, 10))
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (col * 10, row * 10, 10, 10))
        pygame.display.update()

    def run(self):
        # Main loop to run the CHIP-8 emulator
        running = True
        while running:
            self.emulate_cycle()  # Fetch, decode, execute cycle
            self.handle_input()  # Handle user input

            # Update timers
            if self.delay_timer > 0:
                self.delay_timer -= 1
            if self.sound_timer > 0:
                self.sound_timer -= 1

            # Draw to screen using pygame
            self.draw_graphics()  # Render the screen

            # Sleep to control frame rate
            time.sleep(1 / 60)  # Emulate a 60Hz cycle rate

    def save_state(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.__dict__, f)

    def load_state(self, filename):
        with open(filename, 'rb') as f:
            self.__dict__ = pickle.load(f)
