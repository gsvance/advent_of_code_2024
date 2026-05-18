import math
import numpy as np
import sys


def int_log2(x):
    y = round(math.log2(x))
    assert isinstance(y, int) and 2 ** y == x
    return np.int64(y)


LG_32 = int_log2(32)
LG_64 = int_log2(64)
LG_2048 = int_log2(2048)
LG_16777216 = int_log2(16777216)

ONE = np.int64(1)
PRUNE_CONST = (ONE << LG_16777216) - ONE


def mix(secret, value):
    return secret ^ value


def prune(secret):
    return secret & PRUNE_CONST


def evolve(secret):
    secret = prune(mix(secret, secret << LG_64))
    secret = prune(mix(secret, secret >> LG_32))
    secret = prune(mix(secret, secret << LG_2048))
    return secret


def part_1(fname):
    secrets = np.loadtxt(fname, dtype=np.int64, encoding='ascii')
    num_steps = 2000
    for _ in range(num_steps):
        secrets = evolve(secrets)
    print('part 1:', int(secrets.sum()))


def price(secret):
    return secret % 10


def part_2(fname):
    initial_secrets = np.loadtxt(fname, dtype=np.int64, encoding='ascii')
    num_steps = 2000
    num_diffs = 4
    secrets = np.empty((initial_secrets.size, num_steps + 1), dtype=np.int64)
    secrets[:, 0] = initial_secrets
    for i in range(num_steps):
        secrets[:, i+1] = evolve(secrets[:, i])
    prices = price(secrets)
    diffs = np.diff(prices)
    bananas_by_diffs = {}
    for buyer in range(initial_secrets.size):
        bought = set()
        for x in range(num_diffs, num_steps + 1):
            my_price = int(prices[buyer, x])
            my_diffs = tuple(map(int, diffs[buyer, x-num_diffs:x]))
            if my_diffs in bought:
                continue
            try:
                bananas_by_diffs[my_diffs] += my_price
            except KeyError:
                bananas_by_diffs[my_diffs] = my_price
            bought.add(my_diffs)
    print('part 2:', max(bananas_by_diffs.values()))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
