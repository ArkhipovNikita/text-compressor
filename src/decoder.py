import lz77
from common import get_io_params
from lz77.consts import OFFSET_LEN_BYTES_TAKEN
from static_huffman.decoder import StaticHuffmanDecoder
from utils import byte2bits, bits2bytes, many_bytes2bits, decode_varint


# чтение дерева хаффмана из header'a
# удаление падинга
# воазращает тело блока и колличество прочитанных байт
def get_body_beginning(f, static_huffman_decoder):
    read_bytes = static_huffman_decoder.extract_header_to_dict(f)
    static_huffman_decoder.assign_codes()
    static_huffman_decoder.build_tree()

    padding_len = int.from_bytes(f.read(1), 'big')
    block = f.read(1)
    block = byte2bits(block, 'big')
    block = block[padding_len:]
    read_bytes += 2

    return block, read_bytes


def decode_block_length(f):
    return decode_varint(f)


# строка бит yf вход
def decode_block(f, block_len):
    static_huffman_decoder = StaticHuffmanDecoder()
    body_beginning, read_bytes = get_body_beginning(f, static_huffman_decoder)

    remain_body = many_bytes2bits(f.read(block_len - read_bytes))
    # тело блока
    body = body_beginning + remain_body

    block_len = len(body)
    pos = 0
    result = []
    result_len = 0

    while pos < block_len:
        # если маркер равен 0, то следующие 3 байта это offset length
        if body[pos] == '0':
            # read offset and length from bits
            read_bits = OFFSET_LEN_BYTES_TAKEN * 8
            t = body[pos + 1: pos + read_bits + 1]
            t = bits2bytes(t)
            offset, length = lz77.read_offset_len_from_bytes(t)

            # получение объектов по offset length
            items = lz77.get_items(result, result_len, offset, length)
            result.extend(items)
            result_len += length
        else:
            # если маркер равен 1, то следующие несколько байт представляют utf8 символ
            item, read_bits = static_huffman_decoder.decode_c(body, pos + 1)
            result.append(item)
            result_len += len(item)

        pos += 1 + read_bits

    return ''.join(result)


input_path, output_path = get_io_params()

input_file = open(input_path, 'rb')
output_file = open(output_path, 'w')

while True:
    # первые несколько байт отвечаеют за длину блока в байтах
    # несколько, потому что число представляется переменным количество байт
    block_length = decode_block_length(input_file)
    if not block_length:
        break
    # декодировать блока
    decoded_block = decode_block(input_file, block_length)
    # запись в исходящий файл
    output_file.write(decoded_block)

input_file.close()
output_file.close()
