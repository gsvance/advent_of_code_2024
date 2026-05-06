import sys


def parse_calibration(line):
    test_value, numbers = line.strip().split(': ')
    calibration = {
        'test value': int(test_value),
        'numbers': [int(n) for n in numbers.split()],
    }
    return calibration


def possibly_true(calibration, concat=False):
    num = calibration['numbers'].pop()

    if len(calibration['numbers']) == 0:
        ret = calibration['test value'] == num
        calibration['numbers'].append(num)
        return ret

    if calibration['test value'] - num >= 0:
        calibration['test value'] -= num
        try_add = possibly_true(calibration, concat=concat)
        calibration['test value'] += num
    else:
        try_add = False

    if try_add:
        calibration['numbers'].append(num)
        return True

    if calibration['test value'] % num == 0:
        calibration['test value'] //= num
        try_mul = possibly_true(calibration, concat=concat)
        calibration['test value'] *= num
    else:
        try_mul = False

    if try_mul:
        calibration['numbers'].append(num)
        return True

    if not concat:
        calibration['numbers'].append(num)
        return False

    stv = str(calibration['test value'])
    snum = str(num)

    if stv != snum and stv.endswith(snum):
        calibration['test value'] = int(stv.removesuffix(snum))
        try_concat = possibly_true(calibration, concat=concat)
        calibration['test value'] = int(stv)
    else:
        try_concat = False

    calibration['numbers'].append(num)
    return try_concat


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        calibrations = [parse_calibration(line) for line in f]
    true_calibrations_sum = 0
    for calibration in calibrations:
        if possibly_true(calibration):
            true_calibrations_sum += calibration['test value']
    print('part 1:', true_calibrations_sum)


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        calibrations = [parse_calibration(line) for line in f]
    true_calibrations_concat_sum = 0
    for calibration in calibrations:
        if possibly_true(calibration, concat=True):
            true_calibrations_concat_sum += calibration['test value']
    print('part 2:', true_calibrations_concat_sum)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
