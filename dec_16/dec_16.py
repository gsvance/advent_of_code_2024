from collections.abc import Hashable
from dataclasses import dataclass, field
from enum import Enum
import heapq
import itertools as it
import sys
from typing import Final, Generic, Iterator, Self, TypeVar


V = TypeVar('V', bound=Hashable)


class Graph(Generic[V]):
    __slots__ = ('edges_from',)

    def __init__(self) -> None:
        self.edges_from: dict[V, dict[V, int]] = {}

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self.edges_from!r}'

    def add_vertex(self, vertex: V) -> None:
        if vertex not in self.edges_from:
            self.edges_from[vertex] = {}

    def add_edge(self, from_vertex: V, to_vertex: V, edge_cost: int) -> None:
        if to_vertex not in self.edges_from:
            raise KeyError(to_vertex)
        self.edges_from[from_vertex][to_vertex] = edge_cost

    def vertices(self) -> Iterator[V]:
        return iter(self.edges_from.keys())

    def neighbors(self, vertex: V) -> Iterator[V]:
        return iter(self.edges_from[vertex].keys())

    def edge_cost(self, from_vertex: V, to_vertex: V) -> int:
        return self.edges_from[from_vertex][to_vertex]


D = TypeVar('D', bound=Hashable)


@dataclass(order=True, kw_only=True, slots=True)
class PriorityItem(Generic[D]):
    priority: int
    data: D = field(compare=False)
    removed: bool = field(default=False, init=False, compare=False)


class PriorityQueue(Generic[D]):
    __slots__ = ('heap', 'entry_finder')

    def __init__(self) -> None:
        self.heap: list[PriorityItem[D]] = []
        self.entry_finder: dict[D, PriorityItem[D]] = {}

    def is_empty(self) -> bool:
        return not bool(self.entry_finder)

    def add_with_priority(self, data: D, *, priority: int) -> None:
        if data in self.entry_finder:
            entry = self.entry_finder.pop(data)
            entry.removed = True
        item = PriorityItem(priority=priority, data=data)
        heapq.heappush(self.heap, item)
        self.entry_finder[data] = item

    def extract_min_priority(self) -> D:
        while self.heap:
            item = heapq.heappop(self.heap)
            if not item.removed:
                del self.entry_finder[item.data]
                return item.data
        raise LookupError('extract min from empty priority queue')


HUGE: Final[int] = 2 ** 64 - 1


def dijkstra_shortest_path(
    graph: Graph[V], source: V, destinations: frozenset[V],
) -> int:
    distance: dict[V, int] = {vertex: HUGE for vertex in graph.vertices()}
    distance[source] = 0
    queue: PriorityQueue[V] = PriorityQueue()
    for vertex, vertex_distance in distance.items():
        queue.add_with_priority(vertex, priority=vertex_distance)
    visited: set[V] = set()

    while not queue.is_empty():

        vertex = queue.extract_min_priority()
        if vertex in destinations and distance[vertex] < HUGE:
            return distance[vertex]
        visited.add(vertex)

        for neighbor in graph.neighbors(vertex):
            if neighbor in visited:
                continue
            new_distance = distance[vertex] + graph.edge_cost(vertex, neighbor)
            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                queue.add_with_priority(neighbor, priority=new_distance)

    raise RuntimeError("dijkstra terminated without finding shortest path")


@dataclass(frozen=True, kw_only=True, slots=True)
class Vector:
    r: int = 0
    c: int = 0

    def __add__(self, other: Self) -> Self:
        return self.__class__(r=self.r + other.r, c=self.c + other.c)

    def rotate_clockwise_90(self) -> Self:
        return self.__class__(r=self.c, c=-self.r)

    def rotate_counterclockwise_90(self) -> Self:
        return self.__class__(r=-self.c, c=self.r)


EAST: Final[Vector] = Vector(c=+1)
SOUTH: Final[Vector] = EAST.rotate_clockwise_90()
WEST: Final[Vector] = SOUTH.rotate_clockwise_90()
NORTH: Final[Vector] = EAST.rotate_counterclockwise_90()

HEADINGS: Final[frozenset] = frozenset([EAST, WEST, SOUTH, NORTH])


class Tile(Enum):
    START = 'S'
    END = 'E'
    WALL = '#'
    EMPTY = '.'


FORWARD_SCORE: Final[int] = 1
ROTATE_SCORE: Final[int] = 1000


@dataclass(frozen=True, kw_only=True, slots=True)
class Reindeer:
    pos: Vector
    head: Vector


class ReindeerMaze:
    __slots__ = ('tiles',)

    def __init__(self, string: str) -> None:
        self.tiles: dict[Vector, Tile] = {}
        for r, line in enumerate(string.strip().split('\n')):
            for c, character in enumerate(line.strip()):
                self.tiles[Vector(r=r, c=c)] = Tile(character)

    def locate(self, tile: Tile) -> Vector:
        candidates = {
            pos for pos, pos_tile in self.tiles.items() if pos_tile == tile
        }
        assert len(candidates) == 1
        return candidates.pop()

    def as_graph(self) -> Graph[Reindeer]:
        maze_graph: Graph[Reindeer] = Graph()
        positions = {
            pos for pos, tile in self.tiles.items() if tile != Tile.WALL
        }

        for pos, head in it.product(positions, HEADINGS):
            reindeer = Reindeer(pos=pos, head=head)
            maze_graph.add_vertex(reindeer)

        for pos, head in it.product(positions, HEADINGS):
            reindeer = Reindeer(pos=pos, head=head)
            if pos + head in positions:
                forward = Reindeer(pos=pos + head, head=head)
                maze_graph.add_edge(reindeer, forward, FORWARD_SCORE)
            clockwise = Reindeer(pos=pos, head=head.rotate_clockwise_90())
            maze_graph.add_edge(reindeer, clockwise, ROTATE_SCORE)
            counterclockwise = Reindeer(
                pos=pos, head=head.rotate_counterclockwise_90()
            )
            maze_graph.add_edge(reindeer, counterclockwise, ROTATE_SCORE)

        return maze_graph


def find_lowest_score(maze: ReindeerMaze) -> int:
    maze_graph = maze.as_graph()
    start_pos = maze.locate(Tile.START)
    reindeer_start = Reindeer(pos=start_pos, head=EAST)
    end_pos = maze.locate(Tile.END)
    reindeer_ends = frozenset(
        Reindeer(pos=end_pos, head=head) for head in HEADINGS
    )
    return dijkstra_shortest_path(maze_graph, reindeer_start, reindeer_ends)


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        maze = ReindeerMaze(f.read())
    print('part 1:', find_lowest_score(maze))


def dijkstra_all_shortest_paths(
    graph: Graph[V], source: V, destinations: frozenset[V],
) -> dict[V, set[V]]:
    shortest_distance = dijkstra_shortest_path(graph, source, destinations)

    previous: dict[V, set[V]] = {vertex: set() for vertex in graph.vertices()}
    distance: dict[V, int] = {vertex: HUGE for vertex in graph.vertices()}
    distance[source] = 0
    queue: PriorityQueue[V] = PriorityQueue()
    for vertex, vertex_distance in distance.items():
        queue.add_with_priority(vertex, priority=vertex_distance)
    visited: set[V] = set()

    while not queue.is_empty():

        vertex = queue.extract_min_priority()
        if distance[vertex] > shortest_distance:
            return previous
        visited.add(vertex)

        for neighbor in graph.neighbors(vertex):
            if neighbor in visited:
                continue
            new_distance = distance[vertex] + graph.edge_cost(vertex, neighbor)
            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                previous[neighbor] = set([vertex])
                queue.add_with_priority(neighbor, priority=new_distance)
            elif new_distance == distance[neighbor]:
                previous[neighbor].add(vertex)

    assert False


def count_best_path_tiles(maze: ReindeerMaze) -> int:
    maze_graph = maze.as_graph()
    start_pos = maze.locate(Tile.START)
    reindeer_start = Reindeer(pos=start_pos, head=EAST)
    end_pos = maze.locate(Tile.END)
    reindeer_ends = frozenset(
        Reindeer(pos=end_pos, head=head) for head in HEADINGS
    )
    all_shortest_paths = dijkstra_all_shortest_paths(
        maze_graph, reindeer_start, reindeer_ends,
    )

    yet_to_consider = set(reindeer_ends)
    best_path_tiles = set([start_pos, end_pos])
    while yet_to_consider:
        reindeer = yet_to_consider.pop()
        best_path_tiles.add(reindeer.pos)
        yet_to_consider.update(all_shortest_paths[reindeer])
    return len(best_path_tiles)


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        maze = ReindeerMaze(f.read())
    print('part 2:', count_best_path_tiles(maze))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
