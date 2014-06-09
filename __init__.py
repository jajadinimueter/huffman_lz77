# coding=utf-8

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse
from lz77_huffman import huffman
from lz77_huffman import lz77


def lz77_compress(text):
    """
    Compresses the given text to a mixture of huffman an lz77
    """

    text_len = len(text)
    lz77_tuples = list(lz77.compress(text, sliding_win_len=128, preview_win_len=64))
    lz77_text, codes, lz77_inter_text, huff_text = lz77.pack(lz77_tuples)
    ntext_len = len(lz77_text)
    print('Size before: %.2fkb, size after: %.2fkb, compression rate: %.2f%%'
          % (text_len/1024, ntext_len/1024,
             100 - ntext_len * 100 / text_len))

    return lz77_text


def lz77_decompress(text):
    lz77_unpacked_text = lz77.unpack(text)
    return lz77.decompress(lz77_unpacked_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='lz77-hoffman')
    parser.add_argument('-c', action='store_true', dest='compress', help='Compress File',
                        default=False)
    parser.add_argument('-d', action='store_true', dest='decompress', help='Decompress File',
                        default=False)
    parser.add_argument('filename', help='The File')
    parser.add_argument('out_filename', help='The Out-File')
    args = parser.parse_args()

    if not args.compress and not args.decompress:
        parser.print_help()
        exit(1)

    fname_out = os.path.abspath(args.out_filename)
    fname = os.path.abspath(args.filename)

    with open(fname, 'rb') as f:
        if args.compress:
            print('Compressing file %s' % fname)
            t1 = f.read()
            result = lz77_compress(t1)
        else:
            result = lz77_decompress(f.read())
        with open(fname_out, 'wb') as fout:
            fout.write(result)