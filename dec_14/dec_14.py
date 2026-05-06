from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import sys
from typing import Final, Self


@dataclass(frozen=True, kw_only=True, slots=True)
class Vector:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return self.__class__(x=self.x + other.x, y=self.y + other.y)

    def __rmul__(self, other: int) -> Self:
        return self.__class__(x=other * self.x, y=other * self.y)

    def __mod__(self, other: Self) -> Self:
        return self.__class__(x=self.x % other.x, y=self.y % other.y)

    def __floordiv__(self, other: int) -> Self:
        return self.__class__(x=self.x // other, y=self.y // other)


@dataclass(eq=False, kw_only=True, slots=True)
class Robot:
    p: Vector
    v: Vector

    @classmethod
    def parse(cls, string: str) -> Self:
        p_string, v_string = string.strip().split()
        p_x, p_y = map(int, p_string.lstrip('p=').split(','))
        v_x, v_y = map(int, v_string.lstrip('v=').split(','))
        return cls(p=Vector(x=p_x, y=p_y), v=Vector(x=v_x, y=v_y))

    def move(self, num_seconds: int, space: Vector) -> None:
        self.p = (self.p + num_seconds * self.v) % space

    def quadrant(self, space: Vector) -> int | None:
        mid = space // 2

        if self.p.y < mid.y:
            if self.p.x < mid.x:
                return 1
            if self.p.x > mid.x:
                return 2

        if self.p.y > mid.y:
            if self.p.x < mid.x:
                return 3
            if self.p.x > mid.x:
                return 4

        return None


def safety_factor(robots: list[Robot], space: Vector) -> int:
    quadrants: dict[int | None, int] = {1: 0, 2: 0, 3: 0, 4: 0, None: 0}
    for robot in robots:
        quadrants[robot.quadrant(space)] += 1
    factor = 1
    for quadrant, tally in quadrants.items():
        if quadrant is not None:
            factor *= tally
    return factor


SPACE_VECTORS: Final[dict[str, Vector]] = {
    'example_1': Vector(x=11, y=7), 'input': Vector(x=101, y=103),
}

NUM_SECONDS: Final[int] = 100


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        robots = list(map(Robot.parse, f.read().strip().split('\n')))
    space = SPACE_VECTORS[Path(fname).stem]
    for robot in robots:
        robot.move(NUM_SECONDS, space)
    print('part 1:', safety_factor(robots, space))


@dataclass(frozen=True, kw_only=True, slots=True)
class LinearFunction:
    m: Fraction
    b: Fraction

    @classmethod
    def from_points(cls, point_1: Vector, point_2: Vector) -> Self:
        rise = point_2.y - point_1.y
        run = point_2.x - point_1.x
        slope = Fraction(rise, run)
        y_intercept = point_1.y - slope * point_1.x
        return cls(m=slope, b=y_intercept)

    def __call__(self, x: int) -> Fraction:
        return self.m * x + self.b


def tree_rating(robots: list[Robot], space: Vector) -> int:
    mid = space // 2
    left_triangle_side = LinearFunction.from_points(
        Vector(x=mid.x, y=0), Vector(x=0, y=space.y - 1)
    )
    right_triangle_side = LinearFunction.from_points(
        Vector(x=mid.x, y=0), Vector(x=space.x - 1, y=space.y - 1)
    )

    sectors: dict[int | None, int] = {1: 0, 2: 0, 3: 0, 4: 0, None: 0}
    for robot in robots:
        if robot.p.x < mid.x:
            y_line = left_triangle_side(robot.p.x)
            if robot.p.y < y_line:
                sectors[1] += 1
                continue
            if robot.p.y > y_line:
                sectors[2] += 1
                continue
        if robot.p.x > mid.x:
            y_line = right_triangle_side(robot.p.x)
            if robot.p.y < y_line:
                sectors[4] += 1
                continue
            if robot.p.y > y_line:
                sectors[3] += 1
                continue
        sectors[None] += 1

    return sectors[2] + sectors[3]


TREE_FILE: Final[Path] = Path(__file__).parent / 'tree.txt'


def draw_tree(robots: list[Robot], space: Vector) -> None:
    rows: list[list[int]] = []
    for _ in range(space.y):
        rows.append([0] * space.x)
    for robot in robots:
        r, c = robot.p.y, robot.p.x
        rows[r][c] += 1
    with TREE_FILE.open('w', encoding='ascii') as f:
        for row in rows:
            for tally in row:
                if tally == 0:
                    f.write('.')
                else:
                    assert len(str(tally)) == 1
                    f.write(str(tally))
            f.write('\n')


def part_2(fname: str) -> None:
    if Path(fname).stem == 'example_1':
        print('part 2:', '---')
        return
    with open(fname, 'r', encoding='ascii') as f:
        robots = list(map(Robot.parse, f.read().strip().split('\n')))
    space = SPACE_VECTORS[Path(fname).stem]
    num_seconds = 0
    while True:
        num_seconds += 1
        for robot in robots:
            robot.move(1, space)
        rating = tree_rating(robots, space)
        if rating > 0.75 * len(robots):
            break
    draw_tree(robots, space)
    print('part 2:', num_seconds)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
