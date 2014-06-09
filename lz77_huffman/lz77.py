"""
Compress a text using the lz77 method. Return a list of tuples
which has to be converted into a binary format. Huffman in our
case.
"""
from lz77_huffman import huffman


def DEBUG(m):
    print(m)


def _no_debug(m):
    pass


def next_char(text, l):
    if len(text) > l:
        return text[l]


def compress(text, sliding_win_len=31, preview_win_len=31):
    cursor = 0

    yield (sliding_win_len, preview_win_len, chr(0x01))

    while cursor < len(text):
        sliding_window_start = cursor - sliding_win_len
        if sliding_window_start < 0:
            sliding_window_start = 0
        sliding_window = text[sliding_window_start:cursor]
        f_index = 0
        f_len = 0
        f_next = chr(0x01)

        # look for searches in the lookahead, when
        # longest found, we break
        for search in [text[cursor:i] for i in reversed(range(cursor, cursor+preview_win_len+1))]:
            if search:
                # search the sliding window backwards
                j = sliding_window.rfind(search)

                if j > -1:
                    f_index = len(sliding_window) - j
                    f_len = len(search)
                    break

        if f_index:
            if cursor + f_len < len(text):
                f_next = text[cursor + f_len]
            cursor += f_len
        else:
            f_next = text[cursor]

        cursor += 1

        yield (f_index, f_len, f_next)


def pack(lz77_codes):
    chars = []
    for a, b, c in lz77_codes:
        chars.append(chr(a))
        chars.append(chr(b))
        chars.append(c)

    lz77_text = ''.join(chars)

    huff_codes = huffman.code_tree(
        huffman.huffman(lz77_text), {})

    huff_text = huffman.codify(lz77_text, huff_codes)

    codes_tuple = [(k, v) for k, v in huff_codes.items()]

    assert huffman.dehuffman(huff_text, codes_tuple) == lz77_text

    huff_packed = huffman.pack(huff_text, huff_codes)
    unpacked_ascii, unpacked_codes = huffman.unpack(huff_packed)
    unpacked_codes = {k: v for k, v in unpacked_codes}
    assert unpacked_ascii == huff_text
    assert unpacked_codes == huff_codes

    assert len(set(huff_codes.values())) == len(huff_codes)

    return huff_packed, huff_codes, lz77_text, huff_text


def unpack(text, original_codes=None):
    unpacked, codes = huffman.unpack(text)

    d = {k: v for k, v in codes}

    if original_codes:
        assert d == original_codes

    unpacked = huffman.dehuffman(unpacked, codes)

    return unpacked


def decompress(text):
    lz77_chars = [(ord(text[i]), ord(text[i+1]), len(text) - 1 >= i+2 and text[i+2] or '')
                  for i in range(0, len(text), 3)]
    win_len, prev_len, _ = lz77_chars[0]
    lz77_chars = lz77_chars[1:]

    cursor = 0
    dtext = ''

    for i, (pos, length, nchar) in enumerate(lz77_chars):
        if pos == 0:
            dtext += nchar
            cursor += 1
        else:
            # find in window
            win_pos = cursor-win_len
            if win_pos < 0:
                win_pos = 0
            window = ''.join(list(dtext[win_pos:cursor]))
            cur_win_len = len(window)
            chars = window[cur_win_len-pos:cur_win_len-pos+length]
            dtext += chars
            if nchar == chr(0x01):
                if i < len(lz77_chars) - 1:
                    dtext += nchar
            else:
                dtext += nchar
            cursor += length + 1

    decompressed_text = ''.join(dtext)
    return decompressed_text
