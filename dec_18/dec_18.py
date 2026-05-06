from dataclasses import dataclass, field
from enum import StrEnum
import heapq
import itertools as it
import sys
from typing import Final, Generic, Hashable, Iterator, Self, TypeVar


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

    def has_vertex(self, vertex: V) -> bool:
        return vertex in self.edges_from

    def has_edge(self, from_vertex: V, to_vertex: V) -> bool:
        return (
            from_vertex in self.edges_from
            and to_vertex in self.edges_from[from_vertex]
        )

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


class DijkstraError(Exception):
    pass


def dijkstra_shortest_path(
    graph: Graph[V], source: V, destinations: frozenset[V]
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

    raise DijkstraError("dijkstra terminated without finding shortest path")


@dataclass(frozen=True, kw_only=True, slots=True)
class Point:
    x: int = 0
    y: int = 0

    def move(self, *, dx: int = 0, dy: int = 0) -> Self:
        return self.__class__(x=self.x + dx, y=self.y + dy)

    def neighbors(self) -> list[Self]:
        return [
            self.move(dx=-1), self.move(dx=+1),
            self.move(dy=-1), self.move(dy=+1),
        ]


def parse_byte(string: str) -> Point:
    x, y = map(int, string.strip().split(','))
    return Point(x=x, y=y)


class Status(StrEnum):
    SAFE = '.'
    CORRUPTED = '#'


class MemorySpace:
    __slots__ = ('x_max', 'y_max', 'coords')

    def __init__(self, x_max: int, y_max: int) -> None:
        self.x_max: int = x_max
        self.y_max: int = y_max
        self.coords: dict[Point, Status] = {
            point: Status.SAFE for point in self.points()
        }

    def points(self) -> Iterator[Point]:
        x_range = range(0, self.x_max + 1)
        y_range = range(0, self.y_max + 1)
        return (Point(x=x, y=y) for x, y in it.product(x_range, y_range))

    def get(self, point: Point) -> Status | None:
        try:
            return self.coords[point]
        except KeyError:
            return None

    def set(self, point: Point, status: Status) -> None:
        if point not in self.coords:
            raise KeyError
        self.coords[point] = status

    def as_graph(self) -> Graph[Point]:
        graph: Graph[Point] = Graph()
        for point in self.points():
            if self.get(point) == Status.SAFE:
                graph.add_vertex(point)
        for point in graph.vertices():
            for neighbor in point.neighbors():
                if graph.has_vertex(neighbor):
                    graph.add_edge(point, neighbor, 1)
        return graph


def minimum_steps_to_exit(
    memory_space: MemorySpace, start_point: Point, exit_point: Point
) -> int:
    graph = memory_space.as_graph()
    return dijkstra_shortest_path(graph, start_point, frozenset([exit_point]))


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='utf-8') as f:
        falling_bytes = list(map(parse_byte, f.read().strip().split('\n')))
    if len(falling_bytes) < 100:
        memory_space = MemorySpace(x_max=6, y_max=6)
        first_few_bytes = 12
    else:
        memory_space = MemorySpace(x_max=70, y_max=70)
        first_few_bytes = 1024
    for fallen_byte in falling_bytes[:first_few_bytes]:
        memory_space.set(fallen_byte, Status.CORRUPTED)
    start_point = Point(x=0, y=0)
    exit_point = Point(x=memory_space.x_max, y=memory_space.y_max)
    print(minimum_steps_to_exit(memory_space, start_point, exit_point))


def check_blocking_byte(
    falling_bytes: list[Point], memory_space: MemorySpace, i: int
) -> int:
    mem = MemorySpace(x_max=memory_space.x_max, y_max=memory_space.y_max)
    start_point = Point(x=0, y=0)
    exit_point = Point(x=mem.x_max, y=mem.y_max)
    for fallen_byte in falling_bytes[:i]:
        mem.set(fallen_byte, Status.CORRUPTED)
    try:
        minimum_steps_to_exit(mem, start_point, exit_point)
    except DijkstraError:
        return +1
    mem.set(falling_bytes[i], Status.CORRUPTED)
    try:
        minimum_steps_to_exit(mem, start_point, exit_point)
    except DijkstraError:
        return 0
    return -1


def minimum_blocking_bytes(
    falling_bytes: list[Point], memory_space: MemorySpace
) -> int:
    if len(falling_bytes) < 100:
        lo = 12 + 1
    else:
        lo = 1024 + 1
    hi = len(falling_bytes) - 1

    while lo <= hi:
        mid = (lo + hi) // 2
        f_mid = check_blocking_byte(falling_bytes, memory_space, mid)
        if f_mid < 0:
            lo = mid + 1
        elif f_mid > 0:
            hi = mid - 1
        else:
            return mid

    raise RuntimeError("binary search failed")


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='utf-8') as f:
        falling_bytes = list(map(parse_byte, f.read().strip().split('\n')))
    if len(falling_bytes) < 100:
        memory_space = MemorySpace(x_max=6, y_max=6)
    else:
        memory_space = MemorySpace(x_max=70, y_max=70)
    i = minimum_blocking_bytes(falling_bytes, memory_space)
    print(falling_bytes[i].x, falling_bytes[i].y, sep=',')


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
