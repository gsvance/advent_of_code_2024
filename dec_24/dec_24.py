import operator
import sys


GATE = {'AND': operator.and_, 'OR': operator.or_, 'XOR': operator.xor}


def parse_system(string):
    system = {}
    for line in string.strip().split('\n'):
        stripped_line = line.strip()
        if stripped_line == '':
            continue
        if ': ' in stripped_line:
            wire, value_string = stripped_line.split(': ')
            system[wire] = int(value_string)
            continue
        if ' -> ' in stripped_line:
            equation_string, wire = stripped_line.split(' -> ')
            input_1, gate, input_2 = equation_string.split()
            system[wire] = (input_1, GATE[gate], input_2)
            continue
        assert False, repr(stripped_line)
    return system


def simulate(system, wire):
    if isinstance(system[wire], int):
        return
    input_1, gate_operator, input_2 = system[wire]
    simulate(system, input_1)
    simulate(system, input_2)
    result = gate_operator(system[input_1], system[input_2])
    system[wire] = result


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        system_string = f.read()
    system = parse_system(system_string)
    z_wires = [wire for wire in system if wire.startswith('z')]
    z_wires.sort(reverse=True)
    for z_wire in z_wires:
        simulate(system, z_wire)
    bit_string = ''.join(str(system[z_wire]) for z_wire in z_wires)
    print(int(bit_string, base=2))


def part_2(fname):
    pass


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
