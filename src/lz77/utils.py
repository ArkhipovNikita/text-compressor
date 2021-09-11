import struct
from typing import Union

from src.lz77.consts import OFFSET_LEN_BYTES_TAKEN

# Нода для связного списка
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

    def __str__(self):
        return '%s' % self.value


# Hash-таблица выделена в отдельный класс,
# чтобы сохранять индекс, на котором оставился update
class HashTableSearch:
    def __init__(self, prefix_len: int):
        self.prefix_len = prefix_len
        self.prefixes_dict = {}
        self.stopped_idx = 0

    # обновить значения в hash-таблице
    # добавить ключи-значения: подстрока минимального совпадения-индекс начала совпадения
    def update(self, s, end_idx):
        # начать с индекса, на котором остановились
        for i in range(self.stopped_idx, end_idx - self.prefix_len + 2):
            key = s[i:i + self.prefix_len]
            new_node = Node(i)
            old_node = self.prefixes_dict.get(key)
            if old_node:
                new_node.next = old_node
                self.prefixes_dict[key] = new_node
            else:
                self.prefixes_dict[key] = new_node
        else:
            self.stopped_idx = end_idx - self.prefix_len + 2

    def __getitem__(self, item):
        return self.prefixes_dict.get(item)


# указать на индекс для скользящего окна
# не выходит за границы
class Pointer:
    def __init__(self, value, min_value, max_value):
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

    def move(self, delta):
        if self.value + delta > self.max_value:
            self.value = self.max_value
        elif self.value + delta < self.min_value:
            self.value = self.min_value
        else:
            self.value += delta

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __gt__(self, other):
        return self.value > other

    def __eq__(self, other):
        return self.value == other

    def __str__(self):
        return '%s' % self.value


# Скользящее окно
class Window:
    def __init__(self, start: int, end: int, start_limit: int, end_limit: int, max_size: int):
        self.start_p = Pointer(start, start_limit, end_limit)
        self.end_p = Pointer(end, start_limit, end_limit)
        self.start_limit = start_limit
        self.end_limit = end_limit
        self.max_size = max_size
        self.max_possible_size = self.end_limit + 1 if self.max_size > self.end_limit else self.max_size

    @property
    def start(self):
        return self.start_p.value

    @property
    def end(self):
        return self.end_p.value

    @property
    def cur_size(self):
        return self.end - self.start + 1

    def move(self, delta):
        if self.start == self.start_limit:
            if self.cur_size + delta > self.max_possible_size:
                self.end_p.move(delta)
                self.start_p.move(self.cur_size - self.max_possible_size)
            else:
                self.end_p.move(delta)
        elif self.end == self.end_limit:
            if self.cur_size - delta > self.max_possible_size:
                self.start_p.move(delta)
                self.end_p.move(self.max_possible_size - self.cur_size)
            else:
                self.start_p.move(delta)
        else:
            self.start_p.move(delta)
            self.end_p.move(delta)

    def __str__(self):
        return '<%s, %s>' % (self.start_p, self.end_p)


# прочитать offset length
def read_offset_len_from_bytes(s: Union[bytes, bytearray]):
    if len(s) != OFFSET_LEN_BYTES_TAKEN:
        raise ValueError('S must be length of %s bytes' % OFFSET_LEN_BYTES_TAKEN)

    offset, length = struct.unpack('hB', s)

    return offset, length


# получить объекты по offset length
def get_items(result: list, cur_pos: int, offset: int, length: int):
    return result[cur_pos - offset:cur_pos - offset + length]
