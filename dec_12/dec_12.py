from collections import deque, namedtuple
from fractions import Fraction
import itertools as it
import sys


Point = namedtuple('Point', 'r c')


def move(point, dr=0, dc=0):
    return Point(r=point.r + dr, c=point.c + dc)


def neighbors(point):
    return [
        move(point, dr=+1), move(point, dr=-1),
        move(point, dc=+1), move(point, dc=-1),
    ]


RegionID = namedtuple('RegionID', 'tile point')


class GardenMap:

    def __init__(self, string):
        self.rows = []
        for line in string.strip().split('\n'):
            self.rows.append(line.strip())
        self.n_rows = len(self.rows)
        row_lengths = set(len(row) for row in self.rows)
        assert len(row_lengths) == 1
        self.n_cols = row_lengths.pop()

        self.regions = {}

    def iter_points(self):
        return map(
            Point._make, it.product(range(self.n_rows), range(self.n_cols))
        )

    def get(self, point):
        if not 0 <= point.r < self.n_rows:
            return None
        if not 0 <= point.c < self.n_cols:
            return None
        return self.rows[point.r][point.c]

    def discover_regions(self, sides=False):
        visited = set()
        for region_point in self.iter_points():
            if region_point in visited:
                continue
            region_tile = self.get(region_point)
            region_id = RegionID(tile=region_tile, point=region_point)
            self.regions[region_id] = {'area': 0, 'perimeter': 0}
            if sides:
                self.regions[region_id]['sides'] = SideSet()
            points_to_consider = set([region_point])
            while points_to_consider:
                point = points_to_consider.pop()
                visited.add(point)
                self.regions[region_id]['area'] += 1
                for neighbor in neighbors(point):
                    if self.get(neighbor) != region_tile:
                        self.regions[region_id]['perimeter'] += 1
                        if sides:
                            self.regions[region_id]['sides'].add_side_between(
                                point, neighbor
                            )
                    elif neighbor not in visited:
                        points_to_consider.add(neighbor)

    def total_price(self):
        return sum(
            region['area'] * region['perimeter']
            for region in self.regions.values()
        )

    def discount_price(self):
        return sum(
            region['area'] * len(region['sides'])
            for region in self.regions.values()
        )


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        garden_map = GardenMap(f.read())
    garden_map.discover_regions()
    print('part 1:', garden_map.total_price())


Side = namedtuple('Side', 'a b')


def colinear(side_1, side_2):
    if side_1.a.r == side_1.b.r == side_2.a.r == side_2.b.r:
        return True
    if side_1.a.c == side_1.b.c == side_2.a.c == side_2.b.c:
        return True
    return False


def try_combine_sides(side_1, side_2):
    if not colinear(side_1, side_2):
        return None
    if side_1.a == side_2.b:
        return Side(a=side_2.a, b=side_1.b)
    if side_1.b == side_2.a:
        return Side(a=side_1.a, b=side_2.b)
    return None


HALF = Fraction(1, 2)


class SideSet:

    def __init__(self, x=None):
        if x is None:
            self.sides = deque()
        else:
            self.sides = deque(x)

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self.sides)})'

    def insert_side(self, side):
        i = 0
        while i < len(self.sides):
            com = try_combine_sides(side, self.sides[i])
            if com is not None:
                self.sides.rotate(-i)
                _ = self.sides.popleft()
                self.insert_side(com)
                return
            i += 1
        self.sides.append(side)

    def add_side_between(self, inner_point, outer_point):
        dr = outer_point.r - inner_point.r
        dc = outer_point.c - inner_point.c
        assert abs(dr) + abs(dc) == 1
        if dr != 0:
            r_mid = Fraction(inner_point.r + outer_point.r, 2)
            c_mid = inner_point.c
            a = Point(r=r_mid, c=c_mid - HALF * dr)
            b = Point(r=r_mid, c=c_mid + HALF * dr)
            self.insert_side(Side(a=a, b=b))
        else:  # dc != 0
            c_mid = Fraction(inner_point.c + outer_point.c, 2)
            r_mid = inner_point.r
            a = Point(r=r_mid + HALF * dc, c=c_mid)
            b = Point(r=r_mid - HALF * dc, c=c_mid)
            self.insert_side(Side(a=a, b=b))

    def __len__(self):
        return len(self.sides)


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        garden_map = GardenMap(f.read())
    garden_map.discover_regions(sides=True)
    print('part 2:', garden_map.discount_price())


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
