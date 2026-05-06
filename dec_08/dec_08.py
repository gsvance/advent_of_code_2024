import sys


class AntennaMap:

    def __init__(self, string):
        self.antennas = {}
        self.n_rows = 0
        row_lengths = set()
        for r, line in enumerate(string.strip().split('\n')):
            stripped_line = line.strip()
            for c, freq in enumerate(stripped_line):
                if not (freq.isalpha() or freq.isdigit()):
                    continue
                try:
                    self.antennas[freq].append((r, c))
                except KeyError:
                    self.antennas[freq] = [(r, c)]
            self.n_rows += 1
            row_lengths.add(len(stripped_line))
        assert len(row_lengths) == 1
        self.n_cols = row_lengths.pop()

    def outside_map(self, r, c):
        return r < 0 or c < 0 or r >= self.n_rows or c >= self.n_cols

    def find_antinodes(self):
        antinodes = set()
        for positions in self.antennas.values():
            for i, (ri, ci) in enumerate(positions):
                for j, (rj, cj) in enumerate(positions):
                    if i == j:
                        continue
                    dr, dc = rj - ri, cj - ci
                    ra, ca = ri - dr, ci - dc
                    if self.outside_map(ra, ca):
                        continue
                    antinodes.add((ra, ca))
        return antinodes

    def find_antinodes_with_resonance(self):
        antinodes_with_resonance = set()
        for positions in self.antennas.values():
            for i, (ri, ci) in enumerate(positions):
                for j, (rj, cj) in enumerate(positions):
                    if i == j:
                        continue
                    dr, dc = rj - ri, cj - ci
                    k = 0
                    ra, ca = ri - k * dr, ci - k * dc
                    while not self.outside_map(ra, ca):
                        antinodes_with_resonance.add((ra, ca))
                        k += 1
                        ra, ca = ri - k * dr, ci - k * dc
        return antinodes_with_resonance


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        antenna_map = AntennaMap(f.read())
    antinodes = antenna_map.find_antinodes()
    print('part 1:', len(antinodes))


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        antenna_map = AntennaMap(f.read())
    antinodes_with_resonance = antenna_map.find_antinodes_with_resonance()
    print('part 2:', len(antinodes_with_resonance))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
