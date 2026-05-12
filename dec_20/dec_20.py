from collections.abc import Iterable, Iterator
import functools
import itertools
import sys
from typing import Final, NamedTuple, Self


class Point(NamedTuple):
    r: int
    c: int


def shift_by(point: Point, *, dr: int = 0, dc: int = 0) -> Point:
    return Point(r=point.r + dr, c=point.c + dc)


def adjacents(point: Point) -> Iterator[Point]:
    yield shift_by(point, dr=-1)
    yield shift_by(point, dr=+1)
    yield shift_by(point, dc=-1)
    yield shift_by(point, dc=+1)


START_TILE: Final[str] = 'S'
END_TILE: Final[str] = 'E'
TRACK_TILE: Final[str] = '.'
WALL_TILE: Final[str] = '#'


VALID_TILES: Final[frozenset[str]] = frozenset([
    START_TILE, END_TILE, TRACK_TILE, WALL_TILE,
])
PASSABLE_TILES: Final[frozenset[str]] = frozenset([
    START_TILE, END_TILE, TRACK_TILE
])


class Racetrack:

    def __init__(self, rows: Iterable[Iterable[str]]) -> None:
        self.rows: tuple[tuple[str, ...], ...] = tuple(
            tuple(row) for row in rows
        )
        row_lengths = {len(row) for row in self.rows}
        assert len(row_lengths) == 1

    @classmethod
    def parse(cls, racetrack_string: str) -> Self:
        rows: list[list[str]] = []
        for line in racetrack_string.strip().split('\n'):
            row = list(line.strip())
            assert frozenset(row).issubset(VALID_TILES)
            rows.append(row)
        return cls(rows)

    @property
    def n_rows(self) -> int:
        return len(self.rows)

    @property
    def n_cols(self) -> int:
        return len(self.rows[0])

    def get(self, point: Point) -> str | None:
        if 0 <= point.r < self.n_rows and 0 <= point.c < self.n_cols:
            return self.rows[point.r][point.c]
        return None

    def neighbors(self, point: Point) -> Iterator[Point]:
        for adjacent in adjacents(point):
            if self.get(adjacent) in PASSABLE_TILES:
                yield adjacent

    def locate(self, unique_tile: str) -> Point:
        candidates: set[Point] = set()
        for r, c in itertools.product(range(self.n_rows), range(self.n_cols)):
            point = Point(r, c)
            tile = self.get(point)
            if tile == unique_tile:
                candidates.add(point)
        assert len(candidates) == 1
        return candidates.pop()

    @functools.cached_property
    def start(self) -> Point:
        return self.locate(START_TILE)

    @functools.cached_property
    def end(self) -> Point:
        return self.locate(END_TILE)


HUGE: Final[int] = 2**63 - 1


def compute_times_from(
    origin: Point, racetrack: Racetrack,
) -> dict[Point, int]:
    time_from_origin: dict[Point, int] = {origin: 0}
    frontier: set[Point] = {origin}
    visited: set[Point] = set()

    while frontier:
        current = min(frontier, key=lambda pt: time_from_origin.get(pt, HUGE))
        frontier.remove(current)
        visited.add(current)
        for neighbor in racetrack.neighbors(current):
            new_time = time_from_origin.get(current, HUGE) + 1
            if new_time < time_from_origin.get(neighbor, HUGE):
                time_from_origin[neighbor] = new_time
                if neighbor not in visited:
                    frontier.add(neighbor)

    return time_from_origin


def cheat_diamond_set(center: Point, radius: int) -> set[Point]:
    diamond: set[Point] = set()

    r_min, r_max = center.r - radius, center.r + radius
    for r in range(r_min, r_max + 1):
        diff = abs(center.r - r)
        c_min = center.c - radius + diff
        c_max = center.c + radius - diff
        for c in range(c_min, c_max + 1):
            diamond.add(Point(r=r, c=c))

    diamond.discard(center)
    for point in adjacents(center):
        diamond.discard(point)

    return diamond


def manhattan_distance(point_a: Point, point_b: Point) -> int:
    return abs(point_b.r - point_a.r) + abs(point_b.c - point_a.c)


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        racetrack = Racetrack.parse(f.read())

    time_from_start = compute_times_from(racetrack.start, racetrack)
    time_to_end = compute_times_from(racetrack.end, racetrack)
    time_without_cheats = time_from_start[racetrack.end]

    running_the_example = racetrack.n_rows < 20
    threshold = 2 if running_the_example else 100

    cheat_tally: dict[int, int] = {}
    for cheat_start, cheat_start_time in time_from_start.items():
        diamond_shape = cheat_diamond_set(cheat_start, 2)
        for cheat_end in diamond_shape.intersection(time_to_end.keys()):
            cheat_end_time = time_to_end[cheat_end]
            cheat_time = manhattan_distance(cheat_start, cheat_end)
            race_time = cheat_start_time + cheat_time + cheat_end_time
            time_saved = time_without_cheats - race_time
            if time_saved >= threshold:
                cheat_tally[time_saved] = cheat_tally.get(time_saved, 0) + 1

    if running_the_example:
        print('part 1:')
        for ps in sorted(cheat_tally.keys()):
            print(f'  save {ps} picoseconds: {cheat_tally[ps]} cheat(s)')
    else:
        print('part 1:', sum(cheat_tally.values()))


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        racetrack = Racetrack.parse(f.read())

    time_from_start = compute_times_from(racetrack.start, racetrack)
    time_to_end = compute_times_from(racetrack.end, racetrack)
    time_without_cheats = time_from_start[racetrack.end]

    running_the_example = racetrack.n_rows < 20
    threshold = 50 if running_the_example else 100

    cheat_tally: dict[int, int] = {}
    for cheat_start, cheat_start_time in time_from_start.items():
        diamond_shape = cheat_diamond_set(cheat_start, 20)
        for cheat_end in diamond_shape.intersection(time_to_end.keys()):
            cheat_end_time = time_to_end[cheat_end]
            cheat_time = manhattan_distance(cheat_start, cheat_end)
            race_time = cheat_start_time + cheat_time + cheat_end_time
            time_saved = time_without_cheats - race_time
            if time_saved >= threshold:
                cheat_tally[time_saved] = cheat_tally.get(time_saved, 0) + 1

    if running_the_example:
        print('part 2:')
        for ps in sorted(cheat_tally.keys()):
            print(f'  save {ps} picoseconds: {cheat_tally[ps]} cheat(s)')
    else:
        print('part 2:', sum(cheat_tally.values()))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
