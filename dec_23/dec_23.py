import sys


def parse_connections(string):
    connections = set()
    for line in string.strip().split('\n'):
        computer_1, computer_2 = line.strip().split('-')
        connection = frozenset({computer_1, computer_2})
        connections.add(connection)
    return frozenset(connections)


def get_computers(connections):
    computers = set()
    for connection in connections:
        computer_1, computer_2 = tuple(connection)
        computers.add(computer_1)
        computers.add(computer_2)
    return frozenset(computers)


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        connections = parse_connections(f.read())
    computers = get_computers(connections)
    t_computers = frozenset(
        {computer for computer in computers if computer.startswith('t')}
    )
    computer_triples = set()
    for t_computer in t_computers:
        for connection in connections:
            computer_1, computer_2 = tuple(connection)
            connection_t1 = frozenset({t_computer, computer_1})
            if connection_t1 not in connections:
                continue
            connection_t2 = frozenset({t_computer, computer_2})
            if connection_t2 not in connections:
                continue
            computer_triple = frozenset({t_computer, computer_1, computer_2})
            computer_triples.add(computer_triple)
    print('part 1:', len(computer_triples))


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        connections = parse_connections(f.read())
    computers = get_computers(connections)
    computer_groups = {2: set(connections)}
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
                    connection = frozenset({computer, group_computer})
                    if connection not in connections:
                        connected = False
                        break
                if not connected:
                    continue
                group = frozenset(smaller_group | {computer})
                computer_groups[size].add(group)
    assert len(computer_groups[size - 1]) == 1
    lan_party = computer_groups[size - 1].pop()
    print('part 2:', end=' ')
    print(*sorted(lan_party), sep=',')


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
