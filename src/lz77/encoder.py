import struct

from src.lz77.utils import Window, HashTableSearch


class LZ77Encoder:
    def __init__(self,
                 max_offset=MAX_OFFSET,                     # максимальный отступ
                 max_match_len=MAX_MATCH_LEN,               # максимальная длина совпадения
                 min_match_len=MIN_MATCH_LEN,               # минимальная длина совпадения
                 search_buf_size=SEARCH_BUF_SIZE,           # размер словаря
                 lookahead_buf_size=LOOKAHEAD_BUF_SIZE):    # размер буфера
        self.max_offset = max_offset
        self.max_match_len = max_match_len
        self.min_match_len = min_match_len
        self.search_buf_size = search_buf_size
        self.lookahead_buf_size = lookahead_buf_size

    # поиск совпадения
    # проверяется hash-таблица на наличие минимального совпадения
    # если есть, то ищется более длинное совдание
    def __find_match(self, s, prefixes_dict, search_buf_win: Window, lookahead_buf_win: Window):
        """
        :param s:                   строка, в которой производится поиск
        :param prefixes_dict:       словарь, где:
                                        ключ - подстрока длиной минимального совдаения,
                                        значение - отсортированный от ногово к старому
                                        cвязный список идексов
        :param search_buf_win:      скользящее окно словаря (в его рамках происходит поиск)
        :param lookahead_buf_win:   скользящее окно буфера
        :return:                    совпадение с максимально возможной длиной совпадения
                                    и минимальным отступом
        """
        # если размер словаря или буфера меньше, чем размер минимального совпадения,
        # то совпадения точного нет
        if search_buf_win.cur_size < self.min_match_len or \
                lookahead_buf_win.cur_size < self.min_match_len:
            return 0, 0

        # ключ - подстрока длиной минимального совпадения
        key = s[lookahead_buf_win.start:lookahead_buf_win.start + self.min_match_len]
        node = prefixes_dict[key]
        # если ключа нет, то совпадения нет
        if not node:
            return 0, 0

        matches = []
        # макисмальный размер совпадения равен max_match_len или размеру текущего словаря
        max_possible_match = search_buf_win.cur_size if self.max_match_len > search_buf_win.cur_size \
            else self.max_match_len

        # поиск индекса в s с наибольшим совпадением
        while node:
            # если значение ноды (индекс) меньше, чем начало окна словаря, или отступ больше допустимого
            # для индекса, то удалить все последующие ноды и закончить поиск
            if node.value < search_buf_win.start_p or lookahead_buf_win.start - node.value > self.max_offset:
                node.next = None
                break

            # изначально длина совпадения равна min_match_len, так как она гарантированно
            # содержится в prefixes_dict
            match_len, delta = self.min_match_len, 0
            while match_len < max_possible_match:
                # текущий индекс в lookahead_buf_win
                matching_idx_lab = lookahead_buf_win.start + self.min_match_len + delta
                # текущий индекс в search_buf_win
                matching_idx_sb = node.value + self.min_match_len + delta
                # если индексы выходят за границы или значения не совпадают, то закончить поиск
                if matching_idx_sb > search_buf_win.end or matching_idx_lab > lookahead_buf_win.end or s[
                    matching_idx_sb] != s[matching_idx_lab]:
                    break
                match_len += 1
                delta += 1

            # если совпадение больше OFFSET_LEN_BYTES_TAKEN, то добавить
            # эта проверка необходима, так как длина и отступ занимают 3 байта
            if len(bytes(s[node.value: node.value + match_len], 'utf-8')) > OFFSET_LEN_BYTES_TAKEN:
                matches.append((lookahead_buf_win.start - node.value, match_len))

            node = node.next

        if len(matches) == 0:
            return 0, 0

        # res = min(matches, key=lambda x: (x[0], -x[1]))
        res = max(matches, key=lambda x: (x[1], -x[0]))
        print(res)

        return res

    def __pack2bytes(self, items):
        markers = []
        item_codes = []
        result = bytearray()

        for item in items:
            if not isinstance(item, tuple):
                markers.append('1')
                item_codes.append(item.encode('utf-8'))
                # item_codes.append(int.to_bytes(item, 1, 'big'))
            else:
                markers.append('0')
                item_codes.append(struct.pack('hB', item[0], item[1]))

        # padding
        markers_len = len(markers)
        if markers_len % 8 != 0:
            add_count = (8 - (markers_len % 8))
            markers.extend(['1'] * add_count)
            markers_len += add_count

        for i in range(0, markers_len, 8):
            result.extend(int(''.join(markers[i: i + 8]), 2).to_bytes(1, 'big'))
            for item_code in item_codes[i: i + 8]:
                result.extend(item_code)

        return result

    def encode_text(self, s: str):
        """
        :param s:           входящая строка
        :return             список, в котором совпадения представлены таплами (offset, length)
        """
        result = []
        # первые min_match_len объектом будут записаны в оригинале
        result.extend(s[:self.min_match_len])
        pos = self.min_match_len
        s_len = len(s)
        # hash-таблица для поиска совпадений
        prefixes_dict = HashTableSearch(self.min_match_len)

        # скользящие окна словаря и буфера
        search_buf_win = Window(0, self.min_match_len - 1, 0, s_len - 1, self.search_buf_size)
        lookahead_buf_win = Window(self.min_match_len,
                                   s_len - 1 if self.lookahead_buf_size > s_len else self.lookahead_buf_size - 1,
                                   0,
                                   s_len - 1,
                                   self.lookahead_buf_size)

        while pos < s_len:
            # обновить значения в hash-таблице
            # добавить ключи-значения: подстрока минимального совпадения-индекс начала совпадения
            prefixes_dict.update(s, search_buf_win.end_p)
            # поиск совпадения
            offset, length = self.__find_match(s, prefixes_dict, search_buf_win, lookahead_buf_win)

            # если совпадение есть, то добавить ссылку на него (offset, length)
            if length:
                result.append((offset, length))
                delta = length
            # иначе добавить оригинальный объект
            else:
                result.append(s[pos])
                delta = 1

            # сдвинуть окна и текущую позицию в  s
            search_buf_win.move(delta)
            lookahead_buf_win.move(delta)
            pos += delta

        return result
