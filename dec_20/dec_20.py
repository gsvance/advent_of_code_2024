from collections import namedtuple
import sys


Point = namedtuple('Point', 'r c')


def move(point, *, dr=0, dc=0):
    return Point(r=point.r + dr, c=point.c + dc)


def neighbors(point):
    return (
        move(point, dr=-1), move(point, dr=+1),
        move(point, dc=-1), move(point, dc=+1),
    )


START = 'S'
END = 'E'
TRACK = '.'
WALL = '#'


class Racetrack:

    def __init__(self, string):
        self.rows = [list(line) for line in string.strip().split('\n')]
        self.n_rows = len(self.rows)
        row_lengths = set(len(row) for row in self.rows)
        assert len(row_lengths) == 1
        self.n_cols = row_lengths.pop()

        self.single_path = {}

    def get(self, point):
        if not (0 <= point.r < self.n_rows and 0 <= point.c < self.n_cols):
            return None
        return self.rows[point.r][point.c]

    def points(self):
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                yield Point(r=r, c=c)

    def locate(self, unique_tile):
        candidates = set()
        for point in self.points():
            if self.get(point) == unique_tile:
                candidates.add(point)
        assert len(candidates) == 1
        return candidates.pop()

    def chart_single_path(self):
        start = self.locate(START)
        end = self.locate(END)
        self.single_path[start] = 0
        current = start
        while current != end:
            future = set()
            for neighbor in neighbors(current):
                if neighbor in self.single_path:
                    continue
                if self.get(neighbor) not in (TRACK, END):
                    continue
                future.add(neighbor)
            assert len(future) == 1
            time = self.single_path[current]
            current = future.pop()
            self.single_path[current] = time + 1

    def count_cheats(self):
        tally = {}
        for point in self.points():
            if self.get(point) != WALL:
                continue
            up_down = (move(point, dr=-1), move(point, dr=+1))
            left_right = (move(point, dc=-1), move(point, dc=+1))
            for point_1, point_2 in (up_down, left_right):
                if point_1 not in self.single_path:
                    continue
                if point_2 not in self.single_path:
                    continue
                time_1 = self.single_path[point_1]
                time_2 = self.single_path[point_2]
                time_saved = abs(time_1 - time_2) - 2
                if time_saved <= 0:
                    continue
                try:
                    tally[time_saved] += 1
                except KeyError:
                    tally[time_saved] = 1
        return tally


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        racetrack = Racetrack(f.read())
    racetrack.chart_single_path()
    cheat_tally = racetrack.count_cheats()
    if racetrack.n_rows < 20:
        print(cheat_tally)
    else:
        print(sum(tally for time, tally in cheat_tally.items() if time >= 100))


def part_2(fname):
    pass


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
