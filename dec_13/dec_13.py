from collections import namedtuple
from fractions import Fraction
import sys


Vector = namedtuple('Vector', ['x', 'y'])


class Matrix(namedtuple('Matrix', ['a', 'b', 'c', 'd'])):
    __slots__ = ()

    @property
    def det(self):
        return self.a * self.d - self.b * self.c

    @property
    def inv(self):
        return self.__class__(
            a=Fraction(self.d, self.det), b=Fraction(-self.b, self.det),
            c=Fraction(-self.c, self.det), d=Fraction(self.a, self.det),
        )

    def __mul__(self, vector):
        return Vector(
            x=self.a * vector.x + self.b * vector.y,
            y=self.c * vector.x + self.d * vector.y,
        )


BUTTON_A = 'Button A'
BUTTON_B = 'Button B'
PRIZE = 'Prize'


def parse_machine(string):
    machine = {}
    for line in string.strip().split('\n'):
        name, vector_string = line.strip().split(': ')
        x_string, y_string = vector_string.strip().split(', ')
        x = int(x_string.lstrip('X='))
        y = int(y_string.lstrip('Y='))
        machine[name] = Vector(x=x, y=y)
    assert set(machine.keys()) == {BUTTON_A, BUTTON_B, PRIZE}
    return machine


MIN_PRESSES = 0
MAX_PRESSES = 100


def win_prize(machine, restrict_max_presses=True):
    vector_a = machine[BUTTON_A]
    vector_b = machine[BUTTON_B]
    matrix = Matrix(
        a=vector_a.x, b=vector_b.x,
        c=vector_a.y, d=vector_b.y,
    )
    vector_p = machine[PRIZE]
    vector_s = matrix.inv * vector_p
    if vector_s.x.denominator != 1 or vector_s.y.denominator != 1:
        return None
    if vector_s.x < MIN_PRESSES or vector_s.y < MIN_PRESSES:
        return None
    if vector_s.x > MAX_PRESSES or vector_s.y > MAX_PRESSES:
        if restrict_max_presses:
            return None
    solution = {
        BUTTON_A: vector_s.x.numerator, BUTTON_B: vector_s.y.numerator,
    }
    return solution


BUTTON_COSTS = {BUTTON_A: 3, BUTTON_B: 1}


def count_tokens(solution):
    tokens = 0
    for button, cost in BUTTON_COSTS.items():
        tokens += cost * solution[button]
    return tokens


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        machines = list(map(parse_machine, f.read().strip().split('\n\n')))
    tokens_spent = 0
    for machine in machines:
        solution = win_prize(machine)
        if solution is not None:
            tokens_spent += count_tokens(solution)
    print('part 1:', tokens_spent)


ERROR = 10_000_000_000_000


def fix_conversion_error(machine):
    vector_p = machine[PRIZE]
    machine[PRIZE] = Vector(x=vector_p.x + ERROR, y=vector_p.y + ERROR)


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        machines = list(map(parse_machine, f.read().strip().split('\n\n')))
    tokens_spent = 0
    for machine in machines:
        fix_conversion_error(machine)
        solution = win_prize(machine, restrict_max_presses=False)
        if solution is not None:
            tokens_spent += count_tokens(solution)
    print('part 2:', tokens_spent)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
