import struct

from src.utils import byte2bits, read_utf_8_c_str


def read_offset_len(s, pos):
    bs = s[pos: pos + 3]
    offset, length = struct.unpack('hB', bs)

    return offset, length, 3


def decode(s: bytes):
    result = []
    res_len = 0
    pos = 0
    s_len = len(s)
    read_bytes = 0

    while pos < s_len:
        markers = byte2bits(s[pos: pos + 1], 'big')
        pos += 1
        for marker in markers:
            if marker == '0':
                offset, length, read_bytes = read_offset_len(s, pos)
                data = result[res_len - offset:res_len - offset + length]
                res_len += len(data)
                result.extend(data)
            elif marker == '1':
                ch, read_bytes = read_utf_8_c_str(s, pos)
                res_len += 1
                result.append(ch)
                # result.extend(s[pos: pos + 1])
            pos += read_bytes

            if pos == s_len:
                break

    return ''.join(result)
