from enum import IntEnum
import random
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
        raise RecursionError(f'invalid combo operand: {operand!r}')


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


BIT_VALUES: Final[int] = 2
COMPUTER_BITS: Final[int] = 3
COMPUTER_VALUES: Final[int] = BIT_VALUES ** COMPUTER_BITS

# DIGITS_AT_ONCE: Final[int] = 7


# def determine_register_a_value(
#     computer: ResettableComputer,
#     desired_outputs: list[int],
#     *,
#     higher_digits: list[int] | None = None,
#     most_correct_outputs_so_far: int = 1,
# ) -> int | None:
#     if higher_digits is None:
#         higher_digits = []
#     for i in range(COMPUTER_VALUES ** DIGITS_AT_ONCE):
#         all_digits: list[int] = []
#         all_digits.extend(higher_digits)
#         ii = i
#         for j in range(DIGITS_AT_ONCE - 1, -1, -1):
#             all_digits.append(ii // COMPUTER_VALUES ** j)
#             ii %= COMPUTER_VALUES ** j
#         all_digits.append(0)
#         register_a = sum(
#             d * COMPUTER_VALUES ** i
#             for i, d in enumerate(reversed(all_digits))
#         )
#         computer.reset()
#         computer.register[A] = register_a
#         outputs = computer.run()
#         if len(outputs) > len(desired_outputs):
#             return None
#         if outputs != desired_outputs[-len(outputs):]:
#             continue
#         if len(outputs) <= most_correct_outputs_so_far:
#             continue
#         if len(outputs) == len(desired_outputs):
#             return register_a
#         value = determine_register_a_value(
#             computer, desired_outputs,
#             higher_digits=all_digits[:-1],
#             most_correct_outputs_so_far=len(outputs),
#         )
#         if value is None:
#             continue
#         return value
#     return None


# def part_2(fname: str) -> None:
#     with open(fname, 'r', encoding='ascii') as f:
#         computer = ResettableComputer(f.read())

#     desired_outputs = list(computer.program)
#     register_a_value = determine_register_a_value(computer, desired_outputs)
#     assert register_a_value is not None

#     computer.reset()
#     computer.register[A] = register_a_value
#     outputs = computer.run()
#     assert outputs == desired_outputs

#     print('part 2:', register_a_value)


# class BackwardsComputer(Computer):

#     # def __init__(self, computer_string: str) -> None:
#     #     super().__init__(computer_string)

#     def run_backwards(self, outputs: list[int]) -> None:
#         outputs = [output for output in outputs]
#         ins_ptr = len(self.program) - 2

#         while ins_ptr >= 0:

#             opcode, operand = self.program[ins_ptr:ins_ptr+2]

#             if opcode == Instruction.ADV:
#                 assert operand != COMBO_OPERAND_A
#                 denominator = 2 ** self.combo(operand)
#                 self.register[A] = self.register[A] * denominator
#             elif opcode == Instruction.BXL:
#                 self.register[B] = self.register[B] ^ operand
#             elif opcode == Instruction.BST:
#                 assert operand not in COMBO_OPERAND_LITERALS
#                 if operand == COMBO_OPERAND_A:
#                     self.register[A] = (self.register[A] // 8) * 8
#                     self.register[A] += self.register[B] % 8
#                 elif operand == COMBO_OPERAND_B:
#                     self.register[B] += 0
#                 elif operand == COMBO_OPERAND_C:
#                     self.register[C] = (self.register[C] // 8) * 8
#                     self.register[C] += self.register[B] % 8
#             elif opcode == Instruction.JNZ:
#                 assert self.register[A] == 0
#             elif opcode == Instruction.BXC:
#                 self.register[B] = self.register[B] ^ self.register[C]
#             elif opcode == Instruction.OUT:
#                 if operand in COMBO_OPERAND_LITERALS:
#                     assert operand == outputs.pop()
#                 elif operand == COMBO_OPERAND_A:
#                     self.register[A] = (self.register[A] // 8) * 8
#                     self.register[A] += outputs.pop()
#                 elif operand == COMBO_OPERAND_B:
#                     self.register[B] = (self.register[B] // 8) * 8
#                     self.register[B] += outputs.pop()
#                 elif operand == COMBO_OPERAND_C:
#                     self.register[C] = (self.register[C] // 8) * 8
#                     self.register[C] += outputs.pop()
#             elif opcode == Instruction.BDV:
#                 assert operand not in (COMBO_OPERAND_A, COMBO_OPERAND_B)
#                 denominator = 2 ** self.combo(operand)
#                 self.register[A] = self.register[B] * denominator
#             elif opcode == Instruction.CDV:
#                 assert operand not in (COMBO_OPERAND_A, COMBO_OPERAND_C)
#                 denominator = 2 ** self.combo(operand)
#                 self.register[A] = self.register[C] * denominator
#             else:
#                 raise RuntimeError(f'invalid instruction opcode: {opcode!r}')

#             if ins_ptr == 0 and len(outputs) == 0:
#                 return

#             for i in range(0, len(self.program), 2):
#                 if (
#                     self.program[i] == Instruction.JNZ
#                     and self.program[i+1] == ins_ptr
#                     and (self.register[A] != 0 or len(outputs) > 0)
#                 ):
#                     ins_ptr = i
#                     break

#             ins_ptr -= 2


# def part_2(fname: str) -> None:
#     with open(fname, 'r', encoding='ascii') as f:
#         computer_string = f.read()
#     computer = Computer(computer_string)
#     desired_outputs = list(computer.program)

#     backwards_computer = BackwardsComputer(computer_string)
#     backwards_computer.register[A] = 0
#     backwards_computer.register[B] = 0
#     backwards_computer.register[C] = 0
#     backwards_computer.run_backwards(desired_outputs)
#     register_a = backwards_computer.register[A]

#     computer.register[A] = register_a
#     outputs = computer.run()
#     assert outputs == desired_outputs
#     print('part 2:', register_a)


def integer_from_bits(bits: list[int]) -> int:
    integer = 0
    for bit in bits:
        integer = integer * BIT_VALUES + bit
    return integer


def bits_from_integer(
    integer: int, *, num_bits: int | None = None,
) -> list[int]:
    if integer == 0:
        if num_bits is None:
            return [0]
        return [0] * num_bits

    reversed_bits: list[int] = []
    while integer > 0:
        reversed_bits.append(integer % BIT_VALUES)
        integer //= BIT_VALUES

    if num_bits is None or len(reversed_bits) == num_bits:
        return reversed_bits[::-1]
    if num_bits < len(reversed_bits):
        raise RuntimeError('too many bits!')
    return [0] * (num_bits - len(reversed_bits)) + reversed_bits[::-1]


def determine_num_bits(
    computer: ResettableComputer, desired_outputs: list[int],
) -> int:
    bits: list[int] = []
    outputs: list[int] = []
    while len(outputs) <= len(desired_outputs):
        bits.append(1)
        computer.reset()
        computer.register[A] = integer_from_bits(bits)
        outputs = computer.run()
    return len(bits)


def generate_initial_population(
    population_size: int, num_bits: int,
) -> list[int]:
    population: list[int] = []
    for _ in range(population_size):
        bits = random.choices(range(BIT_VALUES), k=num_bits)
        population.append(integer_from_bits(bits))
    return population


BAD: Final[int] = -999


def score_fitness(
    individual: int, computer: ResettableComputer, desired_outputs: list[int],
) -> int:
    computer.reset()
    computer.register[A] = individual
    outputs = computer.run()

    desired_bits: list[int] = []
    for desired_output in desired_outputs:
        desired_bits.extend(
            bits_from_integer(desired_output, num_bits=COMPUTER_BITS)
        )
    output_bits: list[int] = []
    for output in outputs:
        output_bits.extend(bits_from_integer(output, num_bits=COMPUTER_BITS))

    score = 0

    len_diff = len(output_bits) - len(desired_bits)
    if len_diff < 0:
        output_bits = [BAD] * abs(len_diff) + output_bits
    elif len_diff > 0:
        score -= abs(len_diff)
        output_bits = output_bits[abs(len_diff):]

    zipped_bits = zip(output_bits, desired_bits, strict=True)
    for output_bit, desired_bit in zipped_bits:
        score += int(output_bit == desired_bit)

    return max(score, 1)


def best_individual(population: list[int], fitness_scores: list[int]) -> int:
    best: int | None = None
    best_score: int | None = None
    for individual, score in zip(population, fitness_scores, strict=True):
        if best_score is None or score > best_score:
            best = individual
            best_score = score
    assert best is not None
    return best


def crossover_and_mutate(
    mother: int,
    father: int,
    num_bits: int,
    mutation_rate: float,
) -> int:
    mother_bits = bits_from_integer(mother, num_bits=num_bits)
    father_bits = bits_from_integer(father, num_bits=num_bits)
    zipped_bits = zip(mother_bits, father_bits, strict=True)
    offspring_bits: list[int] = []
    for mother_bit, father_bit in zipped_bits:
        if random.random() < mutation_rate:
            offspring_bit = random.choice([mother_bit, father_bit])
        else:
            offspring_bit = random.choice(range(BIT_VALUES))
        offspring_bits.append(offspring_bit)
    return integer_from_bits(offspring_bits)


def reproduce(
    population: list[int],
    fitness_scores: list[int],
    num_bits: int,
    mutation_rate: float,
) -> list[int]:
    new_population: list[int] = []
    for _ in range(len(population)):
        mother, father = random.choices(population, fitness_scores, k=2)
        offspring = crossover_and_mutate(
            mother, father, num_bits, mutation_rate,
        )
        new_population.append(offspring)
    return new_population


POPULATION_SIZE: Final[int] = 3_000
MUTATION_RATE: Final[float] = 0.005


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        computer = ResettableComputer(f.read())
    desired_outputs = list(computer.program)

    num_bits = determine_num_bits(computer, desired_outputs)
    population = generate_initial_population(POPULATION_SIZE, num_bits)
    fitness_scores = [
        score_fitness(individual, computer, desired_outputs)
        for individual in population
    ]
    goal_fitness_score = len(desired_outputs) * COMPUTER_BITS

    generation = 0
    while max(fitness_scores) < goal_fitness_score:
        print(
            generation,
            (
                bin(best_individual(population, fitness_scores))
                .removeprefix('0b')
            ),
            sep='\t',
        )
        population = reproduce(
            population, fitness_scores, num_bits, MUTATION_RATE,
        )
        fitness_scores = [
            score_fitness(individual, computer, desired_outputs)
            for individual in population
        ]
        generation += 1
    print(
        generation,
        bin(best_individual(population, fitness_scores)).removeprefix('0b'),
        sep='\t',
    )

    register_a = best_individual(population, fitness_scores)
    computer.reset()
    computer.register[A] = register_a
    outputs = computer.run()
    assert outputs == desired_outputs
    print('part 2:', register_a)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
