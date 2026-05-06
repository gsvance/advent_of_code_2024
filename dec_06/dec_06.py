import enum
import sys


UNOBSTRUCTED = '.'
OBSTRUCTION = '#'


class Direction(enum.StrEnum):
    UP = '^'
    RIGHT = '>'
    DOWN = 'v'
    LEFT = '<'

    def rotate(self):
        directions = list(self.__class__)
        i = directions.index(self)
        return directions[(i + 1) % len(directions)]

    @property
    def dr(self):
        if self == self.__class__.UP:
            return -1
        if self == self.__class__.DOWN:
            return +1
        return 0

    @property
    def dc(self):
        if self == self.__class__.LEFT:
            return -1
        if self == self.__class__.RIGHT:
            return +1
        return 0


class Guard:

    def __init__(self, r, c, char, area):
        self.r, self.c = r, c
        self.facing = Direction(char)
        self.area = area
        self.visited = set()
        self.memories = set()

    @property
    def dr(self):
        return self.facing.dr

    @property
    def dc(self):
        return self.facing.dc

    def visit(self):
        if self.area.within_bounds(self.r, self.c):
            self.visited.add((self.r, self.c))
            return True
        return False

    def step(self):
        next_r, next_c = self.r + self.dr, self.c + self.dc
        if self.area.get(next_r, next_c) == OBSTRUCTION:
            self.facing = self.facing.rotate()
        else:
            self.r, self.c = next_r, next_c

    def patrol(self):
        while self.visit():
            self.step()

    def remember(self):
        if (self.r, self.c, self.dr, self.dc) not in self.memories:
            self.memories.add((self.r, self.c, self.dr, self.dc))
            return True
        return False

    def patrol_loops(self):
        vis = self.visit()
        rem = self.remember()
        while vis and rem:
            self.step()
            vis = self.visit()
            rem = self.remember()
        if not rem:
            return True
        return False


class MappedArea:

    def __init__(self, string):
        self.rows = []
        for line in string.strip().split('\n'):
            self.rows.append(list(line.strip()))
        self.n_rows = len(self.rows)
        row_lengths = set(len(row) for row in self.rows)
        assert len(row_lengths) == 1
        self.n_cols = row_lengths.pop()

    def within_bounds(self, r, c):
        return 0 <= r < self.n_rows and 0 <= c < self.n_cols

    def __getitem__(self, rc):
        r, c = rc
        if not self.within_bounds(r, c):
            raise IndexError(repr(rc))
        return self.rows[r][c]

    def get(self, r, c):
        try:
            return self[r, c]
        except IndexError:
            return None

    def __setitem__(self, rc, char):
        r, c = rc
        if not self.within_bounds(r, c):
            raise IndexError(repr(rc))
        self.rows[r][c] = char

    def locate_guard(self):
        guard_positions = []
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if self[r, c] not in (UNOBSTRUCTED, OBSTRUCTION):
                    guard_positions.append((r, c))
        assert len(guard_positions) == 1
        r, c = guard_positions.pop()
        char = self[r, c]
        self[r, c] = UNOBSTRUCTED
        return Guard(r, c, char, self)

    def duplicate(self):
        dup = self.__class__(UNOBSTRUCTED)
        dup.rows = [row.copy() for row in self.rows]
        dup.n_rows, dup.n_cols = self.n_rows, self.n_cols
        return dup


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        mapped_area = MappedArea(f.read())
    guard = mapped_area.locate_guard()
    guard.patrol()
    print('part 1:', len(guard.visited))


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        mapped_area = MappedArea(f.read())
    default_area = mapped_area.duplicate()
    default_guard = default_area.locate_guard()
    default_guard.patrol()
    guards_looped = 0
    for r, c in default_guard.visited:
        if mapped_area[r, c] != UNOBSTRUCTED:
            continue
        loop_area = mapped_area.duplicate()
        loop_area[r, c] = OBSTRUCTION
        guard = loop_area.locate_guard()
        if guard.patrol_loops():
            guards_looped += 1
    print('part 2:', guards_looped)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
