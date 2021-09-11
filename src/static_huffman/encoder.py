import heapq
from src.static_huffman.utils import Node, HuffmanLeaf
from src.utils import increment_bin_n, int2bytes_in_int, bits2bytes, pad_code


def canonize_codes(codes: list):
    """
    :param codes:       список кодов хаффмана
    :return             канонизированный список кодов
    """
    result = {}
    prev_code = '0' * codes[0][1]
    result[codes[0][0]] = prev_code

    for i in range(1, len(codes)):
        new_code = increment_bin_n(prev_code)
        new_code += '0' * (codes[i][1] - len(new_code))
        result[codes[i][0]] = new_code
        prev_code = new_code

    return result


class StaticHuffmanEncoder:
    def __init__(self, items: dict):
        self.root = None
        self.nodes = []
        self.codes = {}

        for ch, freq in items.items():
            heapq.heappush(self.nodes, HuffmanLeaf(freq, ch))

        self.__build_tree()
        self.__assign_codes()
        self.__canonize_codes()

    def __build_tree(self):
        while True:
            if len(self.nodes) == 1:
                self.root = heapq.heappop(self.nodes)
                break

            node1, node2 = heapq.heappop(self.nodes), heapq.heappop(self.nodes)
            new_prob = node1.value + node2.value
            new_node = Node(new_prob, node1, node2)

            heapq.heappush(self.nodes, new_node)

    def __assign_codes(self):
        if not self.root.has_children:
            self.codes[self.root.word] = 1
        else:
            stack = [(self.root, 0)]

            while len(stack) != 0:
                node, cur_code = stack.pop()

                if not node:
                    continue

                if not node.has_children:
                    self.codes[node.word] = cur_code

                stack.append((node.left, cur_code + 1))
                stack.append((node.right, cur_code + 1))

    def __canonize_codes(self):
        codes = list(map(lambda x: (x[0], x[1]), self.codes.items()))
        codes.sort(key=lambda x: (x[1], x[0]))

        self.codes = canonize_codes(codes)

    def encode_header(self):
        result = bytearray()

        # первые два байта отвечают за кол-во листьев
        result.extend(int2bytes_in_int(len(self.codes), 2, 'big'))

        for ch, code in self.codes.items():
            # result.append(ch)
            result.extend(ch.encode('utf-8'))
            code_len = len(code)

            # сделать переменное число байт либо 2
            if code_len > 255:
                raise ValueError('Length of huffman code is too big')

            result.append(code_len)

        return result

    def encode_c(self, c):
        return self.codes[c]

    def encode_text(self, text):
        result = []
        for c in text:
            result.append(self.encode_c(c))

        return result

    def compress(self, s: str):
        result = []

        result.extend(self.encode_header())
        encoded_text = bits2bytes(pad_code(''.join(self.encode_text(s))))

        result.extend(encoded_text)

        return result

    # compress files
    # def compress(self, path_in, path_out):
    #     f_in = open(path_in, 'rb')
    #     f_out = open(path_out, 'wb')
    #
    #     f_out.write(self.__encode_header())
    #
    #     block = f_in.read(READ_BLOCK_SIZE)
    #     while block:
    #         f_out.write(self.__encode_text(block))
    #         block = f_in.read(READ_BLOCK_SIZE)
    #
    #     f_in.close()
    #     f_out.close()
