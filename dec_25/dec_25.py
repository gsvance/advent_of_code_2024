import sys
from typing import Final


FILLED: Final[str] = '#'
EMPTY: Final[str] = '.'


N_ROWS: Final[int] = 7
N_COLS: Final[int] = 5


class Schematic:

    def __init__(self, string: str) -> None:
        self.rows: list[list[str]] = []
        for line in string.strip().split('\n'):
            self.rows.append(list(line.strip()))
        assert len(self.rows) == N_ROWS
        row_lengths = set(len(row) for row in self.rows)
        assert row_lengths == {N_COLS}

    def get(self, r: int, c: int) -> str | None:
        if r not in range(N_ROWS) or c not in range(N_COLS):
            return None
        return self.rows[r][c]


class Lock(Schematic):

    def __init__(self, string: str) -> None:
        super().__init__(string)
        assert self.rows[0] == [FILLED] * N_COLS
        assert self.rows[-1] == [EMPTY] * N_COLS
        self.heights = [0] * N_COLS
        for c in range(N_COLS):
            r = 1
            while self.get(r, c) == FILLED:
                self.heights[c] += 1
                r += 1


class Key(Schematic):

    def __init__(self, string: str) -> None:
        super().__init__(string)
        assert self.rows[0] == [EMPTY] * N_COLS
        assert self.rows[-1] == [FILLED] * N_COLS
        self.heights = [0] * N_COLS
        for c in range(N_COLS):
            r = N_ROWS - 2
            while self.get(r, c) == FILLED:
                self.heights[c] += 1
                r -= 1


def parse_schematic(string: str) -> Lock | Key:
    if string[0] == FILLED:
        return Lock(string)
    if string[0] == EMPTY:
        return Key(string)
    assert False, repr(string)


def fit_together(lock: Lock, key: Key) -> bool:
    for c in range(N_COLS):
        if lock.heights[c] + key.heights[c] + 2 > N_ROWS:
            return False
    return True


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        schematics_string = f.read()
    schematics = [
        parse_schematic(section)
        for section in schematics_string.strip().split('\n\n')
    ]
    num_fitting_pairs = 0
    for lock in schematics:
        if not isinstance(lock, Lock):
            continue
        for key in schematics:
            if not isinstance(key, Key):
                continue
            num_fitting_pairs += int(fit_together(lock, key))
    print(num_fitting_pairs)


def part_2(fname: str) -> None:
    pass


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
