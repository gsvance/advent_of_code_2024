from collections.abc import Hashable, Iterable
from dataclasses import dataclass
import functools
import itertools
import sys
from typing import Final, Generic, overload, Self, TypeVar


@dataclass(frozen=True, kw_only=True, slots=True)
class Vector:
    x: int
    y: int

    def __add__(self, vector: Self) -> Self:
        return self.__class__(x=self.x + vector.x, y=self.y + vector.y)

    def __rmul__(self, scalar: int) -> Self:
        return self.__class__(x=self.x * scalar, y=self.y * scalar)

    def __sub__(self, vector: Self) -> Self:
        return self + -1 * vector


A = TypeVar('A', bound=Hashable)
B = TypeVar('B', bound=Hashable)


@dataclass(init=False, repr=False, frozen=True, match_args=False, slots=True)
class FrozenPairs(Generic[A, B]):
    pairs: frozenset[tuple[A, B]]

    def __init__(self, pairs: Iterable[tuple[A, B]]) -> None:
        unique_objects: set[A | B] = set()
        set_of_pairs: set[tuple[A, B]] = set()
        for a, b in pairs:
            assert a not in unique_objects
            unique_objects.add(a)
            assert b not in unique_objects
            unique_objects.add(b)
            set_of_pairs.add((a, b))
        object.__setattr__(self, 'pairs', frozenset(set_of_pairs))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({list(self.pairs)!r})'

    @overload
    def __getitem__(self, key: A) -> B:
        ...

    @overload
    def __getitem__(self, key: B) -> A:
        ...

    def __getitem__(self, key):
        for a, b in self.pairs:
            if a == key:
                return b
            if b == key:
                return a
        raise KeyError(key)

    def __contains__(self, item: A | B) -> bool:
        for a, b in self.pairs:
            if a == item or b == item:
                return True
        return False


DIRECTIONS: Final[FrozenPairs[str, Vector]] = FrozenPairs([
    ('>', Vector(x=+1, y=0)),
    ('<', Vector(x=-1, y=0)),
    ('^', Vector(x=0, y=+1)),
    ('v', Vector(x=0, y=-1)),
])


class Keypad(FrozenPairs[str, Vector]):

    def causes_panic(
        self, start: Vector, end: Vector, steps: list[Vector],
    ) -> bool:
        assert start in self and end in self
        position = start
        for step in steps:
            position += step
            if position not in self:
                return True
        assert position == end
        return False

    @functools.cache
    def find_best_route(self, start_key: str, end_key: str) -> str:
        start, end = self[start_key], self[end_key]
        difference = end - start
        steps: list[Vector] = []

        # NOTE: it is important to keep these if statements in this particular
        # order. If we *don't* try to prioritize '<' (and possibly also 'v'),
        # then we don't get the most efficient sequences of key presses.
        if difference.x < 0:
            steps += [DIRECTIONS['<']] * (-1 * difference.x)
        if difference.y < 0:
            steps += [DIRECTIONS['v']] * (-1 * difference.y)
        if difference.y > 0:
            steps += [DIRECTIONS['^']] * difference.y
        if difference.x > 0:
            steps += [DIRECTIONS['>']] * difference.x

        if self.causes_panic(start, end, steps):
            steps = list(reversed(steps))
            assert not self.causes_panic(start, end, steps)

        return ''.join(DIRECTIONS[step] for step in steps)


NUMERIC_KEYPAD: Final[Keypad] = Keypad([
    ('A', Vector(x=0, y=0)),
    ('0', Vector(x=-1, y=0)),
    ('3', Vector(x=0, y=1)),
    ('2', Vector(x=-1, y=1)),
    ('1', Vector(x=-2, y=1)),
    ('6', Vector(x=0, y=2)),
    ('5', Vector(x=-1, y=2)),
    ('4', Vector(x=-2, y=2)),
    ('9', Vector(x=0, y=3)),
    ('8', Vector(x=-1, y=3)),
    ('7', Vector(x=-2, y=3)),
])


DIRECTIONAL_KEYPAD: Final[Keypad] = Keypad([
    ('A', Vector(x=0, y=0)),
    ('^', Vector(x=-1, y=0)),
    ('>', Vector(x=0, y=-1)),
    ('v', Vector(x=-1, y=-1)),
    ('<', Vector(x=-2, y=-1)),
])


def directional_key_sequence(code: str, keypad: Keypad) -> str:
    sequence: list[str] = []
    for start_key, end_key in itertools.pairwise('A' + code):
        best_route = keypad.find_best_route(start_key, end_key)
        sequence.extend((best_route, 'A'))
    return ''.join(sequence)


def split_after_A(sequence: str) -> tuple[str, str]:
    if sequence == '':
        return '', ''
    first_A = sequence.index('A')
    return sequence[:first_A+1], sequence[first_A+1:]


@functools.cache
def shortest_sequence_length(
    code: str,
    directional_keypad_robots: int,
    prepend_numeric_keypad: bool = True,
) -> int:
    if prepend_numeric_keypad:
        sequence = directional_key_sequence(code, NUMERIC_KEYPAD)
    else:
        sequence = code

    extra_len = 0

    for robot in range(1, directional_keypad_robots + 1):
        sequence = directional_key_sequence(sequence, DIRECTIONAL_KEYPAD)
        while len(sequence) > 10:
            prefix, sequence = split_after_A(sequence)
            extra_len += shortest_sequence_length(
                prefix, directional_keypad_robots - robot,
                prepend_numeric_keypad=False,
            )

    return len(sequence) + extra_len


def complexity(code: str, directional_keypad_robots: int = 2) -> int:
    length_part = shortest_sequence_length(code, directional_keypad_robots)
    numeric_part = int(code.lstrip('0').rstrip('A'))
    return length_part * numeric_part


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        codes = f.read().strip().split()
    complexities = [complexity(code) for code in codes]
    print('part 1:', sum(complexities))


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        codes = f.read().strip().split()
    complexities = [complexity(code, 25) for code in codes]
    print('part 2:', sum(complexities))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
