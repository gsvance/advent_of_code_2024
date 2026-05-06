from dataclasses import dataclass
import functools as ft
import itertools as it
import sys
from typing import Final, Generic, Literal, overload, Self, TypeAlias, TypeVar


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


A = TypeVar('A')
B = TypeVar('B')


@dataclass(init=False, repr=False, frozen=True, match_args=False, slots=True)
class FrozenPairs(Generic[A, B]):
    pairs: frozenset[tuple[A, B]]

    def __init__(self, d: dict[A, B]) -> None:
        unique: set[A | B] = set()
        for a, b in d.items():
            assert a not in unique
            unique.add(a)
            assert b not in unique
            unique.add(b)
        object.__setattr__(self, 'pairs', frozenset(d.items()))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({dict(self.pairs)!r})'

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


DIRECTIONS: Final[FrozenPairs[str, Vector]] = FrozenPairs({
    '>': Vector(x=+1, y=0),
    '<': Vector(x=-1, y=0),
    '^': Vector(x=0, y=+1),
    'v': Vector(x=0, y=-1),
})


Keypad: TypeAlias = FrozenPairs[str, Vector]


NUMERIC_KEYPAD: Final[Keypad] = Keypad({
    'A': Vector(x=0, y=0),
    '0': Vector(x=-1, y=0),
    '3': Vector(x=0, y=1),
    '2': Vector(x=-1, y=1),
    '1': Vector(x=-2, y=1),
    '6': Vector(x=0, y=2),
    '5': Vector(x=-1, y=2),
    '4': Vector(x=-2, y=2),
    '9': Vector(x=0, y=3),
    '8': Vector(x=-1, y=3),
    '7': Vector(x=-2, y=3),
})


DIRECTIONAL_KEYPAD: Final[Keypad] = Keypad({
    'A': Vector(x=0, y=0),
    '^': Vector(x=-1, y=0),
    '>': Vector(x=0, y=-1),
    'v': Vector(x=-1, y=-1),
    '<': Vector(x=-2, y=-1),
})


@ft.cache
def find_routes_between_keys(
    start_key: str,
    end_key: str,
    keypad_name: Literal['numeric', 'directional'],
) -> frozenset[tuple[Vector, ...]]:
    match keypad_name:
        case 'numeric':
            keypad = NUMERIC_KEYPAD
        case 'directional':
            keypad = DIRECTIONAL_KEYPAD
        case _:
            raise ValueError(f'invalid keypad name: {keypad_name!r}')

    diff = keypad[end_key] - keypad[start_key]

    steps: list[Vector] = []
    if diff.x > 0:
        steps.extend([Vector(x=+1, y=0)] * diff.x)
    elif diff.x < 0:
        steps.extend([Vector(x=-1, y=0)] * -(diff.x))
    if diff.y > 0:
        steps.extend([Vector(x=0, y=+1)] * diff.y)
    elif diff.y < 0:
        steps.extend([Vector(x=0, y=-1)] * -(diff.y))

    routes = frozenset(it.permutations(steps))
    return routes


def causes_panic(
    route_steps: tuple[Vector, ...],
    keypad_name: Literal['numeric', 'directional'],
) -> bool:
    match keypad_name:
        case 'numeric':
            keypad = NUMERIC_KEYPAD
        case 'directional':
            keypad = DIRECTIONAL_KEYPAD
        case _:
            raise ValueError(f'invalid keypad name: {keypad_name!r}')

    position = keypad['A']
    assert position in keypad
    for step in route_steps:
        position += step
        if position not in keypad:
            return True
    return False


def route_as_code(route_steps: tuple[Vector, ...]) -> str:
    return ''.join(DIRECTIONS[s] for s in route_steps)


def route_as_steps(route_code: str) -> tuple[Vector, ...]:
    return tuple(DIRECTIONS[c] for c in route_code)


def find_shortest_sequences(
    codes: set[str],
    keypad_name: Literal['numeric', 'directional'],
) -> set[str]:
    sequences: set[str] = set()

    for code in codes:

        routes_between_keys: list[set[str]] = []
        for start_key, end_key in it.pairwise('A' + code):
            route_steps = find_routes_between_keys(
                start_key, end_key, keypad_name,
            )
            route_codes = {route_as_code(rs) + 'A' for rs in route_steps}
            routes_between_keys.append(route_codes)

        full_routes = {''.join(p) for p in it.product(*routes_between_keys)}
        for route_code in full_routes:
            route_steps = route_as_steps(route_code.replace('A', ''))
            if not causes_panic(route_steps, keypad_name):
                sequences.add(route_code)

    min_length = min(len(s) for s in sequences)
    sequences = {s for s in sequences if len(s) == min_length}
    return sequences


def shortest_sequence_length(code: str) -> int:
    sequences = find_shortest_sequences({code}, 'numeric')
    sequences = find_shortest_sequences(sequences, 'directional')
    sequences = find_shortest_sequences(sequences, 'directional')

    sequence_lengths = set(len(s) for s in sequences)
    assert len(sequence_lengths) == 1
    return sequence_lengths.pop()


def complexity(code: str) -> int:
    length_part = shortest_sequence_length(code)
    numeric_part = int(''.join(c for c in code if c.isdigit()))
    print(code, length_part, numeric_part)
    return length_part * numeric_part


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        codes = f.read().strip().split()
    complexities = [complexity(code) for code in codes]
    print('part 1:', sum(complexities))


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        pass
    print('part 2:', '')


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
