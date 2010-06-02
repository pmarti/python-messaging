# -*- coding: utf-8 -*-
# Copyright (C) 2008 Telefonica I+D
#
# Author : Roberto Majadas <roberto.majadas (at) openshine.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import codecs

class Codec(codecs.Codec):
    def encode(self, _input, errors='strict'):
        return codecs.charmap_encode(_input, errors, encoding_map)

    def decode(self, _input, errors='strict'):
        result, index = [], 0
        while index < len(_input):
            c = ord(_input[index])
            index += 1
            if c == 0x1b:
                c = ord(_input[index])
                index += 1
                result.append(unichr(escape_decode_dict[c]))
            else:
                result.append(unichr(decoding_table[c]))

        return u''.join(result), len(result)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, _input, final=False):
        return codecs.charmap_encode(_input, self.errors, encoding_map)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, _input, final=False):
        return codecs.charmap_decode(_input, self.errors, decoding_table)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


# encodings module API
def getregentry(encoding):
    if not encoding == 'gsm0338':
        return

    return codecs.CodecInfo(
        name='gsm0338',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter)


decoding_table = codecs.make_identity_dict(range(256))

decoding_table.update({
    0x00: 0x40,      # COMMERCIAL AT
    0x01: 0xA3,      # POUND SIGN
    0x02: 0x24,      # DOLLAR SIGN
    0x03: 0xA5,      # YEN SIGN
    0x04: 0xE8,      # LATIN SMALL LETTER E WITH GRAVE
    0x05: 0xE9,      # LATIN SMALL LETTER E WITH ACUTE
    0x06: 0xF9,      # LATIN SMALL LETTER U WITH GRAVE
    0x07: 0xEC,      # LATIN SMALL LETTER I WITH GRAVE
    0x08: 0xF2,      # LATIN SMALL LETTER O WITH GRAVE
    0x09: 0xC7,      # LATIN LARGE LETTER C WITH CEDILLA
    0x0A: 0x0A,      # LINE FEED
    0x0B: 0xD8,      # LATIN CAPITAL LETTER O WITH STROKE
    0x0C: 0xF8,      # LATIN SMALL LETTER O WITH STROKE
    0x0D: 0x0D,      # CARRIAGE RETURN
    0x0E: 0xC5,      # LATIN CAPITAL LETTER A WITH RING ABOVE
    0x0F: 0xE5,      # LATIN SMALL LETTER A WITH RING ABOVE
    0x10: 0x0394,    # GREEK CAPITAL LETTER DELTA
    0x11: 0x5F,      # LOW LINE
    0x12: 0x3A6,     # GREEK CAPITAL LETTER PHI
    0x13: 0x393,     # GREEK CAPITAL LETTER GAMMA
    0x14: 0x39B,     # GREEK CAPITAL LETTER LAMDA
    0x15: 0x3A9,     # GREEK CAPITAL LETTER OMEGA
    0x16: 0x3A0,     # GREEK CAPITAL LETTER PI
    0x17: 0x3A8,     # GREEK CAPITAL LETTER PSI
    0x18: 0x3A3,     # GREEK CAPITAL LETTER SIGMA
    0x19: 0x398,     # GREEK CAPITAL LETTER THETA
    0x1A: 0x39E,     # GREEK CAPITAL LETTER XI
    0x1B: 0xA0,      # ESCAPE TO EXTENSION TABLE (or as NBSP, see note above)
    0x1C: 0xC6,      # LATIN CAPITAL LETTER AE
    0x1D: 0xE6,      # LATIN SMALL LETTER AE
    0x1E: 0xDF,      # LATIN SMALL LETTER SHARP S (German)
    0x1F: 0xC9,      # LATIN CAPITAL LETTER E WITH ACUTE
    0x24: 0xA4,      # CURRENCY SIGN
    0x40: 0xA1,      # INVERTED EXCLAMATION MARK
    0x5B: 0xC4,      # LATIN CAPITAL LETTER A WITH DIAERESIS
    0x5C: 0xD6,      # LATIN CAPITAL LETTER O WITH DIAERESIS
    0x5D: 0xD1,      # LATIN CAPITAL LETTER N WITH TILDE
    0x5E: 0xDC,      # LATIN CAPITAL LETTER U WITH DIAERESIS
    0x5F: 0xA7,      # SECTION SIGN
    0x60: 0xBF,      # INVERTED QUESTION MARK
    0x7B: 0xE4,      # LATIN SMALL LETTER A WITH DIAERESIS
    0x7C: 0xF6,      # LATIN SMALL LETTER O WITH DIAERESIS
    0x7D: 0xF1,      # LATIN SMALL LETTER N WITH TILDE
    0x7E: 0xFC,      # LATIN SMALL LETTER U WITH DIAERESIS
    0x7F: 0xE0,      # LATIN SMALL LETTER A WITH GRAVE
})

escape_decode_dict = {
    0x000a: 0x000c,  # FORM FEED
    0x0014: 0x005e,  # CIRCUMFLEX ACCENT
    0x0028: 0x007b,  # LEFT CURLY BRACKET
    0x0029: 0x007d,  # RIGHT CURLY BRACKET
    0x002f: 0x005c,  # REVERSE SOLIDUS
    0x003c: 0x005b,  # LEFT SQUARE BRACKET
    0x003d: 0x007e,  # TILDE
    0x003e: 0x005d,  # RIGHT SQUARE BRACKET
    0x0040: 0x007c,  # VERTICAL LINE
    0x0065: 0x20ac,  # EURO SIGN
}

### Encoding table
encoding_map = codecs.make_encoding_map(decoding_table)

encoding_map.update({
    0xC0: 0x41,
    0xC1: 0x41,
    0xC2: 0x41,
    0xC3: 0x41,
    0xC8: 0x45,
    0xC9: 0x45,
    0xCA: 0x45,
    0xCB: 0x45,
    0xCC: 0x49,
    0xCD: 0x49,
    0xCE: 0x49,
    0xCF: 0x49,
    0xD2: 0x4F,
    0xD3: 0x4F,
    0xD4: 0x4F,
    0xD5: 0x4F,
    0xD9: 0x55,
    0xDA: 0x55,
    0xDB: 0x55,
    0xDD: 0x59,
    0xE1: 0x61,
    0xE2: 0x61,
    0xE3: 0x61,
    0xE7: 0x09,
    0xE9: 0x65,
    0xEA: 0x65,
    0xEB: 0x65,
    0xED: 0x69,
    0xEE: 0x69,
    0xEF: 0x69,
    0xF3: 0x6F,
    0xF3: 0x6F,
    0xF4: 0x6F,
    0xF5: 0x6F,
    0xFA: 0x75,
    0xFB: 0x75,
    0xFD: 0x79,
    0xFF: 0x79,
})


def is_valid_gsm_text(text):
    """Returns True if ``text`` can be encoded as gsm text"""
    try:
        text.encode("gsm0338")
    except:
        return False

    return True

# Codec registration
codecs.register(getregentry)
