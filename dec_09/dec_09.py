import collections
import sys


def parse_disk_map(string):
    return [int(digit) for digit in string.strip()]


def expand_disk_map(disk_map):
    free_space, file_id, file_blocks = False, 0, []
    for digit in disk_map:
        if free_space:
            file_blocks.extend('.' for _ in range(digit))
        else:
            file_blocks.extend(file_id for _ in range(digit))
            file_id += 1
        free_space = not free_space
    return file_blocks


def swap_elements(my_list, i, j):
    my_list[i], my_list[j] = my_list[j], my_list[i]


def seek_free_space(file_blocks, start_index):
    i = start_index
    while file_blocks[i] != '.':
        i += 1
    return i


def seek_file_block(file_blocks, start_index):
    j = start_index
    while not isinstance(file_blocks[j], int):
        j -= 1
    return j


def move_file_blocks(file_blocks):
    free_space_ptr = seek_free_space(file_blocks, 0)
    file_block_ptr = seek_file_block(file_blocks, len(file_blocks) - 1)
    while free_space_ptr < file_block_ptr:
        swap_elements(file_blocks, free_space_ptr, file_block_ptr)
        free_space_ptr = seek_free_space(file_blocks, free_space_ptr + 1)
        file_block_ptr = seek_file_block(file_blocks, file_block_ptr - 1)


def calculate_filesystem_checksum(file_blocks):
    checksum = 0
    for i, file_id in enumerate(file_blocks):
        if isinstance(file_id, int):
            checksum += file_id * i
    return checksum


def part_1(fname):
    with open(fname, 'r', encoding='ascii') as f:
        disk_map = parse_disk_map(f.read())
    file_blocks = expand_disk_map(disk_map)
    move_file_blocks(file_blocks)
    print('part 1:', calculate_filesystem_checksum(file_blocks))


FreeSpace = collections.namedtuple('FreeSpace', ['size'])
SomeFile = collections.namedtuple('SomeFile', ['size', 'fid'])


def convert_disk_map(disk_map):
    free_space, file_id, disk_objects = False, 0, []
    for digit in disk_map:
        if free_space:
            disk_objects.append(FreeSpace(size=digit))
        else:
            disk_objects.append(SomeFile(size=digit, fid=file_id))
            file_id += 1
        free_space = not free_space
        if disk_objects[-1].size == 0:
            disk_objects.pop()
    return disk_objects


def find_highest_file_id(disk_objects):
    i = len(disk_objects) - 1
    while not isinstance(disk_objects[i], SomeFile):
        i -= 1
    return disk_objects[i].fid


def move_whole_files(disk_objects):
    file_id = find_highest_file_id(disk_objects)
    while file_id >= 0:
        j = len(disk_objects) - 1
        while not (
            isinstance(disk_objects[j], SomeFile)
            and disk_objects[j].fid == file_id
        ):
            j -= 1
        found_space = False
        i = 0
        while i < j:
            if (
                isinstance(disk_objects[i], FreeSpace)
                and disk_objects[i].size >= disk_objects[j].size
            ):
                found_space = True
                break
            i += 1
        if found_space:
            hole_size = disk_objects[i].size
            disk_objects[i] = disk_objects[j]
            disk_objects[j] = FreeSpace(size=disk_objects[j].size)
            if disk_objects[i].size < hole_size:
                extra_size = hole_size - disk_objects[i].size
                disk_objects.insert(i + 1, FreeSpace(size=extra_size))
        file_id -= 1


def calculate_filesystem_checksum_with_objects(disk_objects):
    checksum, i = 0, 0
    for obj in disk_objects:
        if isinstance(obj, FreeSpace):
            i += obj.size
        elif isinstance(obj, SomeFile):
            for _ in range(obj.size):
                checksum += i * obj.fid
                i += 1
        else:
            assert False, repr(obj)
    return checksum


def part_2(fname):
    with open(fname, 'r', encoding='ascii') as f:
        disk_map = parse_disk_map(f.read())
    disk_objects = convert_disk_map(disk_map)
    move_whole_files(disk_objects)
    print('part 2:', calculate_filesystem_checksum_with_objects(disk_objects))


if __name__ == '__main__':
    _, arg_1 = sys.argv
    part_1(fname=arg_1)
    part_2(fname=arg_1)
