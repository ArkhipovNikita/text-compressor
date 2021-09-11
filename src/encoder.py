import struct
from collections import defaultdict

from common import get_io_params
from lz77.encoder import LZ77Encoder
from static_huffman.encoder import StaticHuffmanEncoder
from utils import get_padding, many_bytes2bits, encode_varint

# блока размера 64KB
BLOCK_SIZE = 65536


def encode_block_length(n: int):
    return encode_varint(n)


def count_frequencies(s):
    d = defaultdict(int)

    for b in s:
        d[b] += 1

    return d


lz77_encoder = LZ77Encoder()


def encode_block(block: str):
    # кодирование блока алгоритмом lz77
    lz77_encoded_text = lz77_encoder.encode_text(block)

    del block

    # подсчет частоты блока
    frequencies = count_frequencies(filter(lambda x: not isinstance(x, tuple), lz77_encoded_text))
    # создание кода хаффмана
    static_huffman_encoder = StaticHuffmanEncoder(frequencies)

    item_codes = []
    result = bytearray()
    len_to_count_padding = 0

    for i, item in enumerate(lz77_encoded_text):
        # если объект в lz77_encoded_text - не тапл, то добавить маркер 1
        # и задированный объект кодом хаффмана
        if not isinstance(item, tuple):
            item_codes.append('1')
            encoded_c = static_huffman_encoder.encode_c(item)
            len_to_count_padding += len(encoded_c)
            item_codes.append(encoded_c)
        # если объект в lz77_encoded_text - тапл, то добавить маркер 0
        # и  offset length
        else:
            item_codes.append('0')
            # не прибавляю в len_to_count_padding, так как всегда ровно 3 байта
            item_codes.append(many_bytes2bits(struct.pack('hB', item[0], item[1])))

        # всегда +1 за счет маркера
        len_to_count_padding += 1

    # информация о дереве и о количестве символов в нем
    huffman_header = many_bytes2bits(static_huffman_encoder.encode_header())
    # паддинг для того, чтобы выровнить байты
    padding = get_padding(len_to_count_padding)

    bits = []
    bits.extend(huffman_header)
    bits.extend(padding)
    bits.extend(''.join(item_codes))
    bits = ''.join(bits)

    block_length = encode_block_length(len(bits) // 8)
    # блок представлятся как: длина блока | коды хаффмана | паддинг | коды хаффмана и offset length
    result.extend(block_length)

    for i in range(0, len(bits), 8):
        result.extend(int(bits[i: i + 8], 2).to_bytes(1, 'big'))

    return result


def main():
    input_path, output_path = '/Users/arkhipov/Downloads/[SubtitleTools.com] golding_william_lord_of_the_flies.txt', 'tests/test.out'
    # input_path, output_path = get_io_params()

    input_file = open(input_path, 'r')
    output_file = open(output_path, 'wb')

    block = input_file.read(BLOCK_SIZE)

    while block:
        encoded_block = encode_block(block)
        output_file.write(encoded_block)
        block = input_file.read(BLOCK_SIZE)

    input_file.close()
    output_file.close()


if __name__ == '__main__':
    main()
