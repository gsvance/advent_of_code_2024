from dataclasses import dataclass
import itertools
import operator
import random
import sys
from typing import Callable, Final, Iterator, Self


GATE_FUNCTIONS: Final[dict[str, Callable[[int, int], int]]] = {
    'AND': operator.and_, 'OR': operator.or_, 'XOR': operator.xor,
}


@dataclass(init=False, match_args=False, slots=True)
class Gate:
    left_wire: str
    right_wire: str
    function: Callable[[int, int], int]
    value: int | None = None

    @classmethod
    def parse(cls, gate_string: str) -> Self:
        left_string, function_string, right_string = gate_string.split()
        left_wire = left_string.strip()
        right_wire = right_string.strip()
        function = GATE_FUNCTIONS[function_string.strip()]

        return cls(left_wire, right_wire, function)

    def __init__(
        self,
        left_wire: str,
        right_wire: str,
        function: Callable[[int, int], int],
    ) -> None:
        self.left_wire = left_wire
        self.right_wire = right_wire
        self.function = function

        self.value = None


def parse_gate_line(gate_line: str) -> tuple[str, Gate]:
    gate_string, wire_string = gate_line.strip().split(' -> ')
    wire = wire_string.strip()
    gate = Gate.parse(gate_string.strip())
    return wire, gate


def parse_value_line(value_line: str) -> tuple[str, int]:
    wire_string, value_string = value_line.strip().split(': ')
    wire = wire_string.strip()
    value = int(value_string.strip())
    return wire, value


class SystemLoopError(Exception):
    pass


class System:

    @classmethod
    def parse(cls, system_string: str) -> Self:
        values_section, gates_section = system_string.strip().split('\n\n')

        values: dict[str, int] = {}
        for value_line in values_section.strip().split('\n'):
            wire, value = parse_value_line(value_line)
            values[wire] = value

        gates: dict[str, Gate] = {}
        for gate_line in gates_section.strip().split('\n'):
            wire, gate = parse_gate_line(gate_line)
            gates[wire] = gate

        return cls(values, gates)

    def __init__(self, values: dict[str, int], gates: dict[str, Gate]) -> None:
        self.values: dict[str, int] = values
        self.gates: dict[str, Gate] = gates

        self.already_simulating: set[str] = set()

    def iter_wires(self) -> Iterator[str]:
        yield from self.values.keys()
        yield from self.gates.keys()

    def get_value(self, wire: str) -> int:
        try:
            return self.values[wire]
        except KeyError:
            value = self.gates[wire].value
            assert value is not None
            return value

    def simulate(self, wires: list[str] | None = None) -> None:
        if wires is not None:
            simulate_these_wires = wires
        else:
            simulate_these_wires = list(self.gates.keys())

        for this_wire in simulate_these_wires:

            if this_wire in self.values:
                continue
            gate = self.gates[this_wire]
            if gate.value is not None:
                continue

            if this_wire in self.already_simulating:
                self.already_simulating.clear()
                raise SystemLoopError('simulated system has a loop!')
            self.already_simulating.add(this_wire)
            self.simulate([gate.left_wire, gate.right_wire])
            self.already_simulating.remove(this_wire)

            left_value = self.get_value(gate.left_wire)
            right_value = self.get_value(gate.right_wire)
            gate.value = gate.function(left_value, right_value)

    def find_wires(self, letter: str) -> list[str]:
        wires = [wire for wire in self.iter_wires() if wire.startswith(letter)]
        wires.sort(reverse=True)
        return wires

    def extract_number(self, letter: str) -> int:
        wires = self.find_wires(letter)
        number = 0
        for wire in wires:
            bit = self.get_value(wire)
            number = (number << 1) | bit
        return number


def part_1(fname: str) -> None:
    with open(fname, 'r', encoding='ascii') as f:
        system = System.parse(f.read())
    system.simulate()
    z = system.extract_number('z')
    print('part 1:', z)


class AdvancedSystem(System):

    def __init__(self, values: dict[str, int], gates: dict[str, Gate]) -> None:
        super().__init__(values, gates)

        self.saved_values: dict[str, int] = self.values.copy()
        self.wire_swaps: set[tuple[str, str]] = set()
        self.found_wires: dict[str, list[str]] = {}

    def reset_values(self) -> None:
        self.values.update(self.saved_values)
        for gate in self.gates.values():
            gate.value = None

    def swap_wires(self, wire_1: str, wire_2: str) -> None:
        assert wire_1 != wire_2
        for wire_pair in self.wire_swaps:
            assert (
                (wire_1 in wire_pair and wire_2 in wire_pair)
                or not (wire_1 in wire_pair or wire_2 in wire_pair)
            )

        self.gates[wire_1], self.gates[wire_2] = (
            self.gates[wire_2], self.gates[wire_1]
        )

        wire_pair = (wire_1, wire_2) if wire_1 < wire_2 else (wire_2, wire_1)
        if wire_pair in self.wire_swaps:
            self.wire_swaps.remove(wire_pair)
        else:
            self.wire_swaps.add(wire_pair)

    def find_wires(self, letter: str) -> list[str]:
        try:
            return self.found_wires[letter]
        except KeyError:
            wires = super().find_wires(letter)
            self.found_wires[letter] = wires
            return wires

    def insert_number(self, letter: str, number: int) -> None:
        wires = self.find_wires(letter)
        mask = 1 << len(wires)
        assert 0 <= number < mask
        for wire in wires:
            mask = mask >> 1
            assert wire in self.values
            self.values[wire] = int(number & mask != 0)

    def iter_value_wires(self) -> Iterator[str]:
        yield from self.values.keys()

    def iter_gate_wires(self) -> Iterator[str]:
        yield from self.gates.keys()

    def iter_valued_gates(self) -> Iterator[str]:
        for wire, gate in self.gates.items():
            if gate.value is not None:
                yield wire

    def iter_swapped_wires(self) -> Iterator[str]:
        yield from itertools.chain.from_iterable(self.wire_swaps)


def get_random_binary(number_of_bits: int) -> int:
    return random.randrange(1 << number_of_bits)


def count_all_matching_bits(int_1: int, int_2: int, max_bits: int) -> int:
    count = 0
    for _ in range(max_bits):
        count += int((int_1 & 1) == (int_2 & 1))
        int_1 >>= 1
        int_2 >>= 1
    return count


RANDOMIZED_SAMPLES: Final[int] = 100


def categorize_gate_wires(
    system: AdvancedSystem, intended_operator: Callable[[int, int], int],
) -> dict[str, list[str]]:
    bits_in_x = len(system.find_wires('x'))
    bits_in_y = len(system.find_wires('y'))
    z_wires = system.find_wires('z')

    categorized_wires: dict[str, set[str]] = {
        'value': set(system.iter_value_wires()),
        'swapped': set(system.iter_swapped_wires()),
        'later': (
            set(system.iter_gate_wires()) - set(system.iter_swapped_wires())
        ),
        'suspect': set(),
        'fine': set(),
    }

    for bits in range(1, len(z_wires) + 1):
        gates_with_values: set[str] | None = None
        failed = False
        for _ in range(RANDOMIZED_SAMPLES):

            x = get_random_binary(bits_in_x)
            y = get_random_binary(bits_in_y)
            system.reset_values()
            system.insert_number('x', x)
            system.insert_number('y', y)
            if gates_with_values is None:
                system.simulate(z_wires[-bits:])
                gates_with_values = set(system.iter_valued_gates())
            system.simulate()
            z = system.extract_number('z')

            matching_bits = count_all_matching_bits(
                z, intended_operator(x, y), bits
            )
            if matching_bits < bits:
                failed = True
                break

        assert gates_with_values is not None
        if not failed:
            categorized_wires['later'].difference_update(gates_with_values)
            categorized_wires['fine'].update(gates_with_values)
            categorized_wires['fine'].difference_update(
                categorized_wires['swapped']
            )
        else:
            categorized_wires['later'].difference_update(gates_with_values)
            categorized_wires['suspect'].update(gates_with_values)
            categorized_wires['suspect'].difference_update(
                categorized_wires['fine']
            )
            categorized_wires['suspect'].difference_update(
                categorized_wires['swapped']
            )
            break

    return {
        category: list(wires) for category, wires in categorized_wires.items()
    }


def sample_wire_swaps(
    system: AdvancedSystem,
    intended_operator: Callable[[int, int], int],
    suspect_wires: list[str],
    later_wires: list[str],
) -> dict[tuple[str, str], int]:
    bits_in_x = len(system.find_wires('x'))
    bits_in_y = len(system.find_wires('y'))
    bits_in_z = len(system.find_wires('z'))

    incorrect_bits: dict[tuple[str, str], int] = {}

    for wire_1, wire_2 in itertools.product(suspect_wires, later_wires):
        incorrect_bits[wire_1, wire_2] = 0
        system.swap_wires(wire_1, wire_2)

        for _ in range(RANDOMIZED_SAMPLES):

            x = get_random_binary(bits_in_x)
            y = get_random_binary(bits_in_y)
            system.reset_values()
            system.insert_number('x', x)
            system.insert_number('y', y)

            try:
                system.simulate()
            except SystemLoopError:
                incorrect_bits[wire_1, wire_2] += bits_in_z
            else:
                z = system.extract_number('z')
                matching_bits = count_all_matching_bits(
                    z, intended_operator(x, y), bits_in_z,
                )
                incorrect_bits[wire_1, wire_2] += bits_in_z - matching_bits

        system.swap_wires(wire_1, wire_2)

    return incorrect_bits


def choose_next_swap(
    system: AdvancedSystem, intended_operator: Callable[[int, int], int],
) -> tuple[str, str]:
    categorized_wires = categorize_gate_wires(system, intended_operator)
    incorrect_bits = sample_wire_swaps(
        system, intended_operator,
        categorized_wires['suspect'], categorized_wires['later'],
    )
    wire_1, wire_2 = min(
        incorrect_bits.keys(), key=lambda wires: incorrect_bits[wires]
    )
    return wire_1, wire_2


def part_2(fname: str) -> None:
    if 'example_1' in fname or 'example_2' in fname:
        print('part 2:', '---')
        return
    if 'example_3' in fname:
        intended_operator: Callable[[int, int], int] = operator.and_
        number_of_swaps = 2
    elif 'input' in fname:
        intended_operator: Callable[[int, int], int] = operator.add
        number_of_swaps = 4
    else:
        assert False, f'part 2 failed to handle filename: {fname!r}'

    with open(fname, 'r', encoding='ascii') as f:
        system = AdvancedSystem.parse(f.read())

    swapped_wires: list[str] = []

    for _ in range(number_of_swaps):
        wire_1, wire_2 = choose_next_swap(system, intended_operator)
        system.swap_wires(wire_1, wire_2)
        swapped_wires.extend([wire_1, wire_2])

    swapped_wires.sort()

    print('part 2:', ','.join(swapped_wires))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
