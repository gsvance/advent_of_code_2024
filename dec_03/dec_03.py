import re
import sys


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        memory = f.read()
    mul_instruction = re.compile(
        r'mul\((\d+),(\d+)\)', re.ASCII | re.MULTILINE,
    )
    multiplications_sum = 0
    for match in mul_instruction.finditer(memory):
        x = int(match.group(1))
        y = int(match.group(2))
        multiplications_sum += x * y
    print('part 1:', multiplications_sum)


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        memory = f.read()
    instruction = re.compile(
        r"mul\((\d+),(\d+)\)|do\(\)|don't\(\)", re.ASCII | re.MULTILINE
    )
    enabled_multiplications_sum = 0
    enabled = True
    for match in instruction.finditer(memory):
        if match.group(0) == "do()":
            enabled = True
        elif match.group(0) == "don't()":
            enabled = False
        elif enabled:
            x = int(match.group(1))
            y = int(match.group(2))
            enabled_multiplications_sum += x * y
    print('part 2:', enabled_multiplications_sum)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
