import heapq
from itertools import chain
import collections


def create_tree(frequencies):
    heapq.heapify(frequencies)
    n = len(frequencies)
    for i in range(1, n):
        left = heapq.heappop(frequencies)
        right = heapq.heappop(frequencies)
        new_node = (left[0] + right[0], left, right)
        heapq.heappush(frequencies, new_node)
    return frequencies[0]


def huffman(text):
    """
    Creates a huffman tree and returns the codes with a translation
    dictionary.
    """

    # count the shit
    counts = collections.defaultdict(int)
    for i in text:
        counts[i] += 1

    return create_tree([(v, k) for k, v in counts.items()])


def code_tree(tree, code, prefix=''):
    if len(tree) == 2:
        code[tree[1]] = prefix
    else:
        code_tree(tree[1], code, prefix + '0')
        code_tree(tree[2], code, prefix + '1')
    return code


def codify(text, codes):
    new_text = [codes[x] for x in text]
    return ''.join(new_text)


def _pack(text):
    bts = []
    for i in range(0, len(text), 8):
        t = text[i:i+8]
        char = chr(int(t, 2))
        bts.append(char)
    return ''.join(bts)


def pack(text, codes):
    """
    Creates binary data out of the text and the codes
    """
    # print(text)

    codes = [(k, v) for k, v in codes.items()]
    code_lengths = [(k, len(v)) for k, v in codes]
    code_lengths = [(k, chr(v)) for k, v in code_lengths]
    codes_text = ''.join([v for _, v in codes])

    # print(codes_text)

    packed_codes = ''.join(chr(int(codes_text[i:i+8], 2))
                           for i in range(0, len(codes_text), 8))

    last_code_len = (len(codes_text) % 8) or 8
    # print('Last code len %s' % last_code_len)
    last_code_len = chr(last_code_len)

    alpha_text = ''.join(['%s%s' % (k, v) for k, v in code_lengths])
    alpha_header_len = len(alpha_text)  # reserve 4 bytes
    # print('Alpha-Header length: %s' % alpha_header_len)
    alpha_header_len = bin(alpha_header_len)[2:].zfill(32)
    alpha_header_len = _pack(alpha_header_len)

    packed_header = last_code_len
    packed_header += alpha_header_len
    packed_header += alpha_text
    packed_header += packed_codes

    header_len = len(packed_header)
    # print('Header length: %s' % header_len)
    header_len = bin(header_len)[2:].zfill(32)
    header_len = _pack(header_len)
    # print('Len header len %s' % len(header_len))

    packed_header = header_len + packed_header
    # print('Packed Header length: %s' % len(packed_header))

    packed_data = _pack(text)
    length = (len(text) % 8) or 8
    packed_data = chr(length) + packed_data

    return packed_header + packed_data


def _unpack_len(text):
    text = [ord(text[i])
            for i in range(0, len(text))]
    text = ''.join([bin(x)[2:].zfill(8) for x in text])
    return int(text, 2)


def substr(s, start, num):
    return s[start: start+num]


def unpack(code_text):
    # header is constructed like this:
    # [1:header_len][1:lenght_of_last_code][1:number_of_codes]([1:plain][code_len])+[codes]

    header_len = _unpack_len(code_text[0:4])
    header = substr(code_text, 4, header_len)
    last_code_len = ord(header[0])
    # print('Unpacked last code len %s' % last_code_len)
    alpha_len = _unpack_len(substr(header, 1, 4))
    # print('Unpacked alpha len %s' % alpha_len)
    alphas = substr(header, 5, alpha_len)
    # print('verfy: Unpacked alpha lenght: %s' % len(alphas))
    codes = header[5+alpha_len:-1]
    # print('verfy: Codes lenght: %s' % len(codes))
    last_code_byte = header[-1]

    # parse the header
    codes_input = ''.join(chain((bin(ord(byte))[2:].zfill(8) for byte in codes),
                          tuple(bin(ord(last_code_byte))[2:].zfill(last_code_len),)))

    cur = []
    alpha_input = []
    for i in alphas:
        if len(cur) == 1:
            i = int(ord(i))
        cur.append(i)
        if len(cur) == 2:
            alpha_input.append(tuple(cur))
            cur = []

    codes = []
    cursor = 0
    for a, l in alpha_input:
        codes.append((a, codes_input[cursor:cursor+l]))
        cursor += l

    text = code_text[header_len+4:]

    last_byte_length, packed_input, last_byte = (text[0],
                                                 text[1:-1],
                                                 text[-1])

    last_byte_length = int(ord(last_byte_length))

    bts = [bin(ord(byte))[2:].zfill(8) for byte in packed_input]
    bts.append(bin(ord(last_byte))[2:].zfill(last_byte_length))

    ascii_input = ''.join(bts)

    # print(ascii_input)

    return ascii_input, codes


def dehuffman(text, codes):
    sorted_codes = list(reversed(sorted(codes, key=lambda x: len(x[1]))))
    dehuffed = []
    cursor = 0
    while cursor < len(text):
        for alpha, code in sorted_codes:
            if text[cursor:cursor+len(code)] == code:
                dehuffed.append(alpha)
                cursor += len(code)
                break

    dehuffed = ''.join(dehuffed)
    return dehuffed


if __name__ == '__main__':
    text_ = 'aaaaaaaaaaaaaaaaaaaaaaaaaasdlfkjsadlkfjdslf'
    codes_ = code_tree(huffman(text_), {})
    code_text_ = codify(text_, codes_)
    packed_ = pack(code_text_, codes_)
    unpacked_, unpacked_codes_ = unpack(packed_)
    de_text_ = dehuffman(unpacked_, unpacked_codes_)
    assert text_ == de_text_