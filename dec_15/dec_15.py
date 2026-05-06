from dataclasses import dataclass
import sys
from typing import Final, Self


@dataclass(frozen=True, kw_only=True, slots=True)
class Vector:
    r: int = 0
    c: int = 0

    def __add__(self, other: Self) -> Self:
        return self.__class__(r=self.r + other.r, c=self.c + other.c)

    @property
    def gps(self) -> int:
        return self.r * 100 + self.c


MOVE_UP: Final[str] = '^'
MOVE_DOWN: Final[str] = 'v'
MOVE_LEFT: Final[str] = '<'
MOVE_RIGHT: Final[str] = '>'

MOVE_VECTOR: Final[dict[str, Vector]] = {
    MOVE_UP: Vector(r=-1), MOVE_DOWN: Vector(r=+1),
    MOVE_LEFT: Vector(c=-1), MOVE_RIGHT: Vector(c=+1),
}


def parse_moves(string: str) -> list[Vector]:
    moves: list[Vector] = []
    for character in string:
        try:
            moves.append(MOVE_VECTOR[character])
        except KeyError:
            pass
    return moves


ROBOT: Final[str] = '@'
BOX: Final[str] = 'O'
WALL: Final[str] = '#'
EMPTY: Final[str] = '.'

BOX_LEFT: Final[str] = '['
BOX_RIGHT: Final[str] = ']'

RESIZED: Final[dict[str, tuple[str, str]]] = {
    WALL: (WALL, WALL), BOX: (BOX_LEFT, BOX_RIGHT),
    EMPTY: (EMPTY, EMPTY), ROBOT: (ROBOT, EMPTY),
}


class Warehouse:

    def __init__(self, string: str) -> None:
        self.tiles: dict[Vector, str] = {}
        for r, line in enumerate(string.strip().split('\n')):
            for c, tile in enumerate(line.strip()):
                pos = Vector(r=r, c=c)
                self.tiles[pos] = tile
        self._robot_pos: Vector | None = None

    @property
    def robot(self) -> Vector:
        if self._robot_pos is not None:
            return self._robot_pos
        candidates = set(
            pos for pos, tile in self.tiles.items() if tile == ROBOT
        )
        assert len(candidates) == 1
        self._robot_pos = candidates.pop()
        return self._robot_pos

    def can_push(self, pos: Vector, move: Vector) -> bool:
        tile = self.tiles[pos]
        if tile in (ROBOT, BOX):
            return self.can_push(pos + move, move)
        if tile == BOX_LEFT:
            if move in (MOVE_VECTOR[MOVE_LEFT], MOVE_VECTOR[MOVE_RIGHT]):
                return self.can_push(pos + move, move)
            pos_r = pos + MOVE_VECTOR[MOVE_RIGHT]
            return (
                self.can_push(pos + move, move)
                and self.can_push(pos_r + move, move)
            )
        if tile == BOX_RIGHT:
            if move in (MOVE_VECTOR[MOVE_LEFT], MOVE_VECTOR[MOVE_RIGHT]):
                return self.can_push(pos + move, move)
            pos_l = pos + MOVE_VECTOR[MOVE_LEFT]
            return (
                self.can_push(pos + move, move)
                and self.can_push(pos_l + move, move)
            )
        if tile == WALL:
            return False
        if tile == EMPTY:
            return True
        assert False

    def _swap(self, pos_1: Vector, pos_2: Vector) -> None:
        self.tiles[pos_1], self.tiles[pos_2] = (
            self.tiles[pos_2], self.tiles[pos_1]
        )

    def push(self, pos: Vector, move: Vector, *, check=True) -> None:
        if check and not self.can_push(pos, move):
            return
        tile = self.tiles[pos]
        if tile == ROBOT:
            self.push(pos + move, move, check=False)
            self._swap(pos, pos + move)
            self._robot_pos = pos + move
            return
        if tile == BOX:
            self.push(pos + move, move, check=False)
            self._swap(pos, pos + move)
            return
        if tile == BOX_LEFT:
            if move in (MOVE_VECTOR[MOVE_LEFT], MOVE_VECTOR[MOVE_RIGHT]):
                self.push(pos + move, move, check=False)
                self._swap(pos, pos + move)
                return
            pos_r = pos + MOVE_VECTOR[MOVE_RIGHT]
            self.push(pos + move, move, check=False)
            self.push(pos_r + move, move, check=False)
            self._swap(pos, pos + move)
            self._swap(pos_r, pos_r + move)
            return
        if tile == BOX_RIGHT:
            if move in (MOVE_VECTOR[MOVE_LEFT], MOVE_VECTOR[MOVE_RIGHT]):
                self.push(pos + move, move, check=False)
                self._swap(pos, pos + move)
                return
            pos_l = pos + MOVE_VECTOR[MOVE_LEFT]
            self.push(pos + move, move, check=False)
            self.push(pos_l + move, move, check=False)
            self._swap(pos, pos + move)
            self._swap(pos_l, pos_l + move)
            return
        if tile == EMPTY:
            return
        assert False

    def box_gps_sum(self) -> int:
        return sum(
            pos.gps for pos, tile in self.tiles.items()
            if tile in (BOX, BOX_LEFT)
        )

    def resize(self) -> None:
        new_tiles: dict[Vector, str] = {}
        for pos, tile in self.tiles.items():
            new_pos_1 = Vector(r=pos.r, c=2 * pos.c)
            new_pos_2 = new_pos_1 + MOVE_VECTOR[MOVE_RIGHT]
            new_tiles[new_pos_1], new_tiles[new_pos_2] = RESIZED[tile]
        self.tiles = new_tiles


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        map_string, moves_string = f.read().strip().split('\n\n')
    moves = parse_moves(moves_string)
    warehouse = Warehouse(map_string)
    for move in moves:
        warehouse.push(warehouse.robot, move)
    print('part 1:', warehouse.box_gps_sum())


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        map_string, moves_string = f.read().strip().split('\n\n')
    moves = parse_moves(moves_string)
    warehouse = Warehouse(map_string)
    warehouse.resize()
    for move in moves:
        warehouse.push(warehouse.robot, move)
    print('part 2:', warehouse.box_gps_sum())


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
