import sys


def is_safe(report):
    n_levels = len(report)
    diffs = set(report[i + 1] - report[i] for i in range(n_levels - 1))
    return diffs <= {1, 2, 3} or diffs <= {-1, -2, -3}


def part_1(fname):
    reports = []
    with open(fname, 'r', encoding='ascii') as f:
        for report_line in f:
            report = [int(level) for level in report_line.strip().split()]
            reports.append(report)
    print('part 1:', sum(is_safe(report) for report in reports))


def is_safe_with_dampener(report):
    if is_safe(report):
        return True
    for i in range(len(report)):
        before = report[:i]
        after = report[i+1:]
        if is_safe(before + after):
            return True
    return False


def part_2(fname):
    reports = []
    with open(fname, 'r', encoding='ascii') as f:
        for report_line in f:
            report = [int(level) for level in report_line.strip().split()]
            reports.append(report)
    print('part 2:', sum(is_safe_with_dampener(report) for report in reports))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
