# все комментраии напсаны для байт
# сейчас все константы представляют собой количесвто символов,
# кроме тех, которые содержат слово BYTE

MAX_MATCH_LEN = 255                 # 2^8 - 1
MIN_MATCH_LEN = 4                   # так как 3 байта занимают отступ и длина
MAX_OFFSET = 32153                  # 2^16 - 1 (2 байта)
OFFSET_BYTE_TAKEN = 2
LENGTH_BYTE_TAKEN = 1
OFFSET_LEN_BYTES_TAKEN = OFFSET_BYTE_TAKEN + LENGTH_BYTE_TAKEN
SEARCH_BUF_SIZE = 32153             # 32KB - 255B
LOOKAHEAD_BUF_SIZE = 255            # 2^8 - 1 чтобы длина совпадения умещалась в 1 байт
