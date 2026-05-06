import functools
import sys


def parse_orderings(string):
    orderings = set()
    for line in string.strip().split('\n'):
        first, second = line.strip().split('|')
        ordered_pair = (int(first), int(second))
        orderings.add(ordered_pair)
    return orderings


def parse_updates(string):
    updates = []
    for line in string.strip().split('\n'):
        update = [int(p) for p in line.strip().split(',')]
        updates.append(update)
    return updates


def is_sorted(update, orderings):
    for i in range(len(update) - 1):
        page_a, page_b = update[i], update[i + 1]
        if (page_a, page_b) not in orderings:
            return False
    return True


def middle_page_number(update):
    midpoint, remainder = divmod(len(update), 2)
    assert remainder == 1  # len(update) is odd
    return update[midpoint]


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        orderings_section, updates_section = f.read().strip().split('\n\n')
    orderings = parse_orderings(orderings_section)
    updates = parse_updates(updates_section)
    middle_page_numbers = []
    for update in updates:
        if is_sorted(update, orderings):
            middle_page_numbers.append(middle_page_number(update))
    print('part 1:', sum(middle_page_numbers))


class CmpFunc:

    def __init__(self, orderings):
        self.orderings = orderings

    def __call__(self, page_a, page_b):
        if page_a == page_b:
            return 0
        if (page_a, page_b) in self.orderings:
            return -1
        if (page_b, page_a) in self.orderings:
            return +1
        raise ValueError((page_a, page_b))


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        orderings_section, updates_section = f.read().strip().split('\n\n')
    orderings = parse_orderings(orderings_section)
    updates = parse_updates(updates_section)
    incorrect_middle_page_numbers = []
    for update in updates:
        if is_sorted(update, orderings):
            continue
        update.sort(key=functools.cmp_to_key(CmpFunc(orderings)))
        incorrect_middle_page_numbers.append(middle_page_number(update))
    print('part 2:', sum(incorrect_middle_page_numbers))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
