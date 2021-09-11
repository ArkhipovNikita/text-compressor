from src.static_huffman.encoder import canonize_codes
from src.static_huffman.utils import HuffmanLeaf, Node
from src.utils import many_bytes2bits, read_utf_8_c

BLOCK_SIZE = 1000


class StaticHuffmanDecoder:
    def __init__(self):
        self.codes = {}
        self.root = Node()
        self.stopped_node = self.root

    def __build_tree_helper(self, cur_node, leaves, idx):
        if len(leaves) == 1:
            if leaves[0].code[idx - 1] == '0':
                cur_node.parent.left = leaves[0]
            else:
                cur_node.parent.right = leaves[0]
            return

        leaves0, leaves1 = [], []

        for leaf in leaves:
            if leaf.code[idx] == '0':
                leaves0.append(leaf)
            else:
                leaves1.append(leaf)

        node0 = Node()
        node1 = Node()

        cur_node.left, cur_node.right = node0, node1

        self.__build_tree_helper(node0, leaves0, idx + 1)
        self.__build_tree_helper(node1, leaves1, idx + 1)

    def build_tree(self):
        nodes = [HuffmanLeaf(word=ch, code=code) for ch, code in self.codes.items()]
        if len(nodes) == 1:
            self.root = nodes[0]
        else:
            self.__build_tree_helper(self.root, nodes, 0)

    def assign_codes(self):
        codes = list(self.codes.items())
        codes.sort(key=lambda x: (x[1], x[0]))

        self.codes = canonize_codes(codes)

    # не работает для одного символа
    def __decode_text(self, bits):
        cur_node = self.stopped_node
        result = bytearray()
        bits_len = len(bits)

        for i in range(bits_len):
            cur_node = cur_node.left if bits[i] == '0' else cur_node.right
            if not cur_node.has_children:
                result.extend(cur_node.word)
                cur_node = self.root

        self.stopped_node = cur_node

        # b''.join(result)
        return result

    def decode_c(self, bits, cur_pos):
        cur_node = self.root
        read_bits = 1
        bits_len = len(bits)

        # для одного бита
        if bits_len - cur_pos - 1 == 0:
            return cur_node.word, read_bits

        for i in range(cur_pos, bits_len):
            cur_node = cur_node.left if bits[i] == '0' else cur_node.right
            if not cur_node.has_children:
                return cur_node.word, read_bits

            read_bits += 1

        raise ValueError('Не нашелся символ')
        # return None, read_bits

    def extract_header_to_dict(self, f):
        """
        :param f:       файл на чтение в бинарном моде
        :return:        количество прочитанных байт
        """
        read_bytes = 0

        count_items = int.from_bytes(f.read(2), 'big')
        read_bytes += 2

        for i in range(count_items):
            # ch = f.read(1)
            # чтение utf8 символа из файла
            ch, _read_bytes = read_utf_8_c(f)
            code_len = int.from_bytes(f.read(1), 'big')
            read_bytes += _read_bytes + 1
            self.codes[ch] = code_len

        return read_bytes

    def decompress(self, path_in):
        f_in = open(path_in, 'rb')

        self.extract_header_to_dict(f_in)
        self.assign_codes()
        self.build_tree()

        # длина паддинга
        padding_len = int.from_bytes(f_in.read(1), 'big')
        block = f_in.read(2)
        block = many_bytes2bits(block)
        # блок без паддинга
        block = block[padding_len:]

        result = bytearray()

        while block:
            result.extend(self.__decode_text(block))
            block = many_bytes2bits(f_in.read(BLOCK_SIZE))

        f_in.close()

        return result

    # def decompress(self, path_in, path_out):
    #     f_in = open(path_in, 'rb')
    #
    #     self.__extract_header_to_dict(f_in)
    #     self.__assign_codes()
    #     self.__build_tree()
    #
    #     padding_len = int.from_bytes(f_in.read(1), 'big')
    #     block = f_in.read(2)
    #     block = many_bytes2bits(block)
    #     block = block[padding_len:]
    #
    #     f_out = open(path_out, 'wb')
    #
    #     while block:
    #         f_out.write(self.__decode_text(block))
    #         block = many_bytes2bits(f_in.read(READ_BLOCK_SIZE))
    #
    #     f_in.close()
    #     f_out.close()
