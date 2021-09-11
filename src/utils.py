import _io
from typing import Union, List


def byte2bits(s: bytes, byteorder: str):
    return '{0:08b}'.format(int.from_bytes(s, byteorder))


def count_utf_8_bytes(byte: Union[int, bytes]):
    bits = byte2bits(byte, 'big')
    first_zero_idx = bits.find('0')
    res = 1 if first_zero_idx == 0 else first_zero_idx

    return res


def read_utf_8_c(f: _io.TextIOWrapper):
    byte = f.read(1)
    bytes_count = count_utf_8_bytes(byte)
    # следующие байты надо бы проверять на наличие 10 в начале
    remain_bytes = f.read(bytes_count - 1)
    c = byte + remain_bytes
    c = c.decode('utf-8')

    return c, bytes_count


def read_utf_8_c_str(s, pos: int):
    byte = s[pos: pos + 1]
    bytes_count = count_utf_8_bytes(byte)
    # следующие байты надо бы проверять на наличие 10 в начале
    remain_bytes = s[pos + 1: pos + bytes_count]
    c = byte + remain_bytes
    c = c.decode('utf-8')

    return c, bytes_count


def get_padding(code_len: int):
    padding_len = 8 - code_len % 8
    padded_info = '{0:08b}'.format(padding_len)
    padding = '0' * padding_len
    result = padded_info + padding

    return result


def pad_code(bin_code: str):
    padding = get_padding(len(bin_code))
    result = padding + bin_code

    return result


def int2bits(s: int):
    return '{0:08b}'.format(s)


def many_bytes2bits(s: bytes):
    return ''.join(map(int2bits, s))


def bits2byte(bits: Union[str, list]):
    if len(bits) != 8:
        raise ValueError('Must be 8 bits to convert to byte')

    return int(bits, 2)


def bits2bytes(bits: Union[str, list]):
    if len(bits) % 8 != 0:
        raise ValueError('Bits is not padded properly')

    result = bytearray([bits2byte(bits[i: i + 8]) for i in range(0, len(bits), 8)])

    return result


def int2bytes_in_int(n: int, bytes_count: int, byteorder: str):
    return [i for i in int.to_bytes(n, bytes_count, byteorder)]


def increment_bin_n(bin_n: str):
    bin_n = list(bin_n)
    for i in range(len(bin_n) - 1, -1, -1):
        new_bit = int(bin_n[i]) + 1
        if new_bit >= 2:
            bin_n[i] = '0'
        else:
            bin_n[i] = str(new_bit)
            break
    else:
        bin_n.insert(0, '1')

    return ''.join(bin_n)


def encode_varint(value: int) -> List[int]:
    negative = value < 0
    encoded = []

    if negative:
        final = -1
    else:
        final = 0

    while True:
        encoded.append(0x80 | (value & 0x7F))
        value >>= 7

        if value == final:
            break

    if negative:
        encoded.append(0x80)

    encoded.reverse()

    encoded[-1] &= 0x7F

    return encoded


def decode_varint(encoded) -> int:
    byte = int.from_bytes(encoded.read(1), 'big')

    if byte == 0x80:
        value = -1
        byte = int.from_bytes(encoded.read(1), 'big')
    else:
        value = 0

    value = (value << 7) | (byte & 0x7F)

    while (byte & 0x80) != 0:
        byte = int.from_bytes(encoded.read(1), 'big')
        value = (value << 7) | (byte & 0x7F)

    return value
