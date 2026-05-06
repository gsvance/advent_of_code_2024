from collections import Counter
import sys


def part_1(fname):
    list_1, list_2 = [], []
    with open(fname, 'r', encoding='ascii') as f:
        for line in f:
            i1, i2 = map(int, line.strip().split())
            list_1.append(i1)
            list_2.append(i2)
    list_1.sort()
    list_2.sort()
    total_distance = sum(abs(i1 - i2) for i1, i2 in zip(list_1, list_2))
    print('part 1:', total_distance)


def part_2(fname):
    left_list, right_list = [], []
    with open(fname, 'r', encoding='ascii') as f:
        for line in f:
            left, right = map(int, line.strip().split())
            left_list.append(left)
            right_list.append(right)
    right_counts = Counter(right_list)
    similarity_score = sum(left * right_counts[left] for left in left_list)
    print('part 2:', similarity_score)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
