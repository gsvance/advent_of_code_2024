from functools import cache
import sys


@cache
def is_possible(design: str, towels: tuple[str, ...]) -> bool:
    if design == '':
        return True
    for towel in towels:
        if design.endswith(towel):
            if is_possible(design.removesuffix(towel), towels):
                return True
    return False


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        towels_part, designs_part = f.read().strip().split('\n\n')
    towels = tuple(towel.strip() for towel in towels_part.split(', '))
    designs = [design.strip() for design in designs_part.split('\n')]
    num_possible = sum(1 for design in designs if is_possible(design, towels))
    print('part 1:', num_possible)


@cache
def count_arrangements(design: str, towels: tuple[str, ...]) -> int:
    if design == '':
        return 1
    count = 0
    for towel in towels:
        if design.endswith(towel):
            count += count_arrangements(design.removesuffix(towel), towels)
    return count


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        towels_part, designs_part = f.read().strip().split('\n\n')
    towels = tuple(towel.strip() for towel in towels_part.split(', '))
    designs = [design.strip() for design in designs_part.split('\n')]
    num_arrangements = sum(
        count_arrangements(design, towels) for design in designs
    )
    print('part 2:', num_arrangements)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
