import sys


MY_WORD = 'XMAS'

DIRECTIONS = {
    (dr, dc) for dr in (-1, 0, +1) for dc in (-1, 0, +1) if (dr, dc) != (0, 0)
}

X_DIRECTIONS = {(dr, dc) for dr in (-1, +1) for dc in (-1, +1)}


class WordSearch:

    def __init__(self, string):
        self.rows = []
        for line in string.strip().split('\n'):
            self.rows.append(line.strip())
        self.n_rows = len(self.rows)
        row_lengths = set(len(row) for row in self.rows)
        assert len(row_lengths) == 1
        self.n_cols = row_lengths.pop()

    def __getitem__(self, rc):
        r, c = rc
        if not (0 <= r < self.n_rows and 0 <= c < self.n_cols):
            raise IndexError(repr(rc))
        return self.rows[r][c]

    def get(self, r, c):
        try:
            return self[r, c]
        except IndexError:
            return None

    def check_word(self, rc, direction, word):
        r, c = rc
        dr, dc = direction
        for i in range(1, len(word)):
            ri = r + i * dr
            ci = c + i * dc
            if self.get(ri, ci) != word[i]:
                return False
        return True

    def count_occurrences(self, word):
        count = 0
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if self[r, c] != word[0]:
                    continue
                count += sum(
                    int(self.check_word((r, c), direction, word))
                    for direction in DIRECTIONS
                )
        return count

    def check_word_x(self, rc, word, m):
        r, c = rc
        indices = [i for i in range(len(word)) if i != m]
        num_found = 0
        for dr, dc in X_DIRECTIONS:
            found = True
            for i in indices:
                ri = r - m * dr + i * dr
                ci = c - m * dc + i * dc
                if self.get(ri, ci) != word[i]:
                    found = False
                    break
            if found:
                num_found += 1
        return num_found == 2

    def count_xs(self, word):
        assert len(word) % 2 == 1
        m = len(word) // 2
        count = 0
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if self[r, c] != word[m]:
                    continue
                count += int(self.check_word_x((r, c), word, m))
        return count


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        word_search = WordSearch(f.read())
    occurrences = word_search.count_occurrences(MY_WORD)
    print('part 1:', occurrences)


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        word_search = WordSearch(f.read())
    num_xs = word_search.count_xs(MY_WORD.removeprefix('X'))
    print('part 2:', num_xs)


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
