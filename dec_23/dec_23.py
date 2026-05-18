from collections.abc import Iterator
from dataclasses import dataclass
import sys
from typing import Self


@dataclass(init=False, repr=False, frozen=True, match_args=False, slots=True)
class Connection:
    computers: tuple[str, str]

    @classmethod
    def parse(cls, connection_string: str) -> Self:
        computer_1, computer_2 = connection_string.strip().split('-')
        return cls(computer_1, computer_2)

    def __init__(self, computer_1: str, computer_2: str) -> None:
        if computer_1 <= computer_2:
            object.__setattr__(self, 'computers', (computer_1, computer_2))
        else:
            object.__setattr__(self, 'computers', (computer_2, computer_1))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self.computers!r}'

    def __iter__(self) -> Iterator[str]:
        yield from self.computers


def parse_connections(string: str) -> frozenset[Connection]:
    connections: set[Connection] = set()
    for line in string.strip().split('\n'):
        connection = Connection.parse(line)
        connections.add(connection)
    return frozenset(connections)


def get_computers(connections: frozenset[Connection]) -> frozenset[str]:
    computers: set[str] = set()
    for connection in connections:
        computers.update(connection)
    return frozenset(computers)


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        connections = parse_connections(f.read())
    computers = get_computers(connections)
    t_computers = frozenset(
        computer for computer in computers if computer.startswith('t')
    )
    computer_triples: set[frozenset[str]] = set()
    for t_computer in t_computers:
        for connection in connections:
            computer_1, computer_2 = connection
            connection_t1 = Connection(t_computer, computer_1)
            if connection_t1 not in connections:
                continue
            connection_t2 = Connection(t_computer, computer_2)
            if connection_t2 not in connections:
                continue
            computer_triple = frozenset((t_computer, computer_1, computer_2))
            computer_triples.add(computer_triple)
    print('part 1:', len(computer_triples))


def part_2(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        connections = parse_connections(f.read())
    computers = get_computers(connections)
    computer_groups: dict[int, set[frozenset[str]]] = {
        2: {frozenset(connection) for connection in connections},
    }
    size = 2
    while len(computer_groups[size]) > 0:
        size += 1
        computer_groups[size] = set()
        for computer in computers:
            for smaller_group in computer_groups[size - 1]:
                if computer in smaller_group:
                    continue
                connected = True
                for group_computer in smaller_group:
                    connection = Connection(computer, group_computer)
                    if connection not in connections:
                        connected = False
                        break
                if not connected:
                    continue
                group = smaller_group | frozenset([computer])
                computer_groups[size].add(group)
    assert len(computer_groups[size - 1]) == 1
    lan_party = computer_groups[size - 1].pop()
    print('part 2:', end=' ')
    print(*sorted(lan_party), sep=',')


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
