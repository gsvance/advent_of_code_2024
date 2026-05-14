from enum import IntEnum
import re
import sys
from typing import Final


REGISTER_REGEX: Final[re.Pattern[str]] = re.compile(
    r'Register ([A-Z]): (\d+)', re.MULTILINE | re.ASCII,
)
PROGRAM_REGEX: Final[re.Pattern[str]] = re.compile(
    r'Program: ([\d,]+)', re.MULTILINE | re.ASCII,
)


A: Final[str] = 'A'
B: Final[str] = 'B'
C: Final[str] = 'C'
REGISTER_NAMES: Final[frozenset[str]] = frozenset([A, B, C])


class Instruction(IntEnum):
    ADV = 0
    BXL = 1
    BST = 2
    JNZ = 3
    BXC = 4
    OUT = 5
    BDV = 6
    CDV = 7


COMBO_OPERAND_LITERALS: Final[frozenset[int]] = frozenset([0, 1, 2, 3])
COMBO_OPERAND_A: Final[int] = 4
COMBO_OPERAND_B: Final[int] = 5
COMBO_OPERAND_C: Final[int] = 6


class Computer:

    def __init__(self, computer_string: str) -> None:
        registers_string, program_string = (
            computer_string.strip().split('\n\n')
        )

        self.register: dict[str, int] = {}
        for register_match in REGISTER_REGEX.finditer(registers_string):
            register_name = str(register_match.group(1))
            register_value = int(register_match.group(2))
            self.register[register_name] = register_value
        assert frozenset(self.register.keys()) == REGISTER_NAMES

        program_match = PROGRAM_REGEX.search(program_string)
        assert program_match is not None
        self.program: tuple[int, ...] = tuple(
            map(int, str(program_match.group(1)).split(','))
        )
        assert len(self.program) % 2 == 0

    def run(self) -> list[int]:
        outputs: list[int] = []
        ins_ptr = 0

        while ins_ptr < len(self.program):

            opcode, operand = self.program[ins_ptr:ins_ptr+2]

            if opcode == Instruction.ADV:
                denominator = 2 ** self.combo(operand)
                self.register[A] = self.register[A] // denominator
            elif opcode == Instruction.BXL:
                self.register[B] = self.register[B] ^ operand
            elif opcode == Instruction.BST:
                self.register[B] = self.combo(operand) % 8
            elif opcode == Instruction.JNZ:
                if self.register[A] != 0:
                    ins_ptr = operand - 2
            elif opcode == Instruction.BXC:
                self.register[B] = self.register[B] ^ self.register[C]
            elif opcode == Instruction.OUT:
                outputs.append(self.combo(operand) % 8)
            elif opcode == Instruction.BDV:
                denominator = 2 ** self.combo(operand)
                self.register[B] = self.register[A] // denominator
            elif opcode == Instruction.CDV:
                denominator = 2 ** self.combo(operand)
                self.register[C] = self.register[A] // denominator
            else:
                raise RuntimeError(f'invalid instruction opcode: {opcode!r}')

            ins_ptr += 2

        return outputs

    def combo(self, operand: int) -> int:
        if operand in COMBO_OPERAND_LITERALS:
            return operand
        if operand == COMBO_OPERAND_A:
            return self.register[A]
        if operand == COMBO_OPERAND_B:
            return self.register[B]
        if operand == COMBO_OPERAND_C:
            return self.register[C]
        raise RuntimeError(f'invalid combo operand: {operand!r}')


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        computer = Computer(f.read())
    outputs = computer.run()
    print('part 1:', ','.join(map(str, outputs)))


class ResettableComputer(Computer):

    def __init__(self, computer_string: str) -> None:
        super().__init__(computer_string)
        self.register_init: dict[str, int] = self.register.copy()

    def reset(self) -> None:
        for register_name, register_value in self.register_init.items():
            self.register[register_name] = register_value


def count_matching_outputs(
    desired_outputs: list[int], outputs: list[int],
) -> int:
    if len(outputs) > len(desired_outputs):
        return 0
    matches = 0
    for i in range(1, len(outputs) + 1):
        if outputs[-i] != desired_outputs[-i]:
            return matches
        matches += 1
    return matches


BLOCK_SIZE: Final[int] = 2


def recursively_find_register_a(
    computer: ResettableComputer,
    desired_outputs: list[int],
    higher_digits: int = 0,
    block_index: int = 0,
    best_so_far: int = 0,
) -> int | None:
    for lower_digits in range(8 ** BLOCK_SIZE):
        register_a = (higher_digits << (3 * BLOCK_SIZE)) | lower_digits

        computer.reset()
        computer.register[A] = register_a
        outputs = computer.run()

        score = count_matching_outputs(desired_outputs, outputs)
        if score == len(desired_outputs):
            return register_a
        if score > best_so_far:
            register_a = recursively_find_register_a(
                computer, desired_outputs, register_a, block_index + 1, score,
            )
            if register_a is not None:
                return register_a

    return None


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        computer = ResettableComputer(f.read())
    desired_outputs = list(computer.program)
    register_a = recursively_find_register_a(computer, desired_outputs)
    assert register_a is not None
    print('part 2:', register_a)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
