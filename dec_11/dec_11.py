import sys


def apply_rules(stone):
    if stone == 0:
        return [1]
    digits = str(stone)
    if len(digits) % 2 == 0:
        m = len(digits) // 2
        return [int(digits[:m]), int(digits[m:])]
    return [stone * 2024]


def transform(stones):
    after_blink = []
    for stone in stones:
        after_blink.extend(apply_rules(stone))
    return after_blink


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        stones = [int(stone) for stone in f.read().strip().split()]
    num_blinks = 25
    for _ in range(num_blinks):
        stones = transform(stones)
    print('part 1:', len(stones))


stones_memo = {}


def compute_num_stones(stones, num_blinks):
    if num_blinks == 0:
        return len(stones)
    num_stones = 0
    for stone in stones:
        try:
            num_stones += stones_memo[stone, num_blinks]
        except KeyError:
            ns = compute_num_stones(transform([stone]), num_blinks - 1)
            stones_memo[stone, num_blinks] = ns
            num_stones += ns
    return num_stones


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        stones = [int(stone) for stone in f.read().strip().split()]
    num_blinks = 75
    print('part 2:', compute_num_stones(stones, num_blinks))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
