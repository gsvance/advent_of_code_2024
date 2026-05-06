from collections import namedtuple
import sys


TRAILHEAD = 0
SUMMIT = 9
IMPASSABLE = '.'


Point = namedtuple("Point", ["r", "c"])


def move(point, dr=0, dc=0):
    return Point(r=point.r + dr, c=point.c + dc)


def parse_elevation(string):
    return int(string) if string != IMPASSABLE else None


class TopographicMap:

    def __init__(self, string):
        self.rows = []
        for line in string.strip().split('\n'):
            self.rows.append(list(map(parse_elevation, line)))
        self.n_rows = len(self.rows)
        row_lengths = set(len(row) for row in self.rows)
        assert len(row_lengths) == 1
        self.n_cols = row_lengths.pop()

    def get(self, point):
        if not 0 <= point.r < self.n_rows:
            return None
        if not 0 <= point.c < self.n_cols:
            return None
        return self.rows[point.r][point.c]

    def iter_points(self):
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                yield Point(r=r, c=c)

    def iter_trailheads(self):
        for point in self.iter_points():
            if self.get(point) == TRAILHEAD:
                yield point

    def score(self, trailhead):
        hikers, visited = set(), set()
        hikers.add(trailhead)
        while hikers:
            hiker = hikers.pop()
            elevation = self.get(hiker)
            if elevation is None:
                continue
            visited.add(hiker)
            neighbors = [
                move(hiker, dr=+1), move(hiker, dr=-1),
                move(hiker, dc=+1), move(hiker, dc=-1),
            ]
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                next_elevation = self.get(neighbor)
                if next_elevation is None or next_elevation != elevation + 1:
                    continue
                hikers.add(neighbor)
        return sum(1 for point in visited if self.get(point) == SUMMIT)

    def rating(self, trailhead):
        elevation = self.get(trailhead)
        if elevation is None:
            return 0
        if elevation == SUMMIT:
            return 1
        neighbors = [
            move(trailhead, dr=+1), move(trailhead, dr=-1),
            move(trailhead, dc=+1), move(trailhead, dc=-1),
        ]
        rating = 0
        for neighbor in neighbors:
            new_elevation = self.get(neighbor)
            if new_elevation is None or new_elevation != elevation + 1:
                continue
            rating += self.rating(neighbor)
        return rating


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        topographic_map = TopographicMap(f.read())
    sum_of_trailhead_scores = 0
    for trailhead in topographic_map.iter_trailheads():
        sum_of_trailhead_scores += topographic_map.score(trailhead)
    print('part 1:', sum_of_trailhead_scores)


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        topographic_map = TopographicMap(f.read())
    sum_of_trailhead_ratings = 0
    for trailhead in topographic_map.iter_trailheads():
        sum_of_trailhead_ratings += topographic_map.rating(trailhead)
    print('part 2:', sum_of_trailhead_ratings)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
