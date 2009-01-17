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

### Codec APIs

class Codec(codecs.Codec):
    def encode(self, _input, errors='strict'):
        print "encode input: %s" % _input
        return codecs.charmap_encode(_input, errors, encoding_map)

    def decode(self, _input, errors='strict'):
        return codecs.charmap_decode(_input, errors, decoding_table)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, _input, final=False):
        print "increment encode input: %s" % _input
        return codecs.charmap_encode(_input, self.errors, encoding_map)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, _input, final=False):
        return codecs.charmap_decode(_input, self.errors, decoding_table)[0]

class StreamWriter(Codec, codecs.StreamWriter):
    pass

class StreamReader(Codec, codecs.StreamReader):
    pass

### encodings module API

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

decoding_table = {
    0x00 : 0x40,    #   COMMERCIAL AT
    0x01 : 0xA3,    #   POUND SIGN
    0x02 : 0x24,    #   DOLLAR SIGN
    0x03 : 0xA5,    #   YEN SIGN
    0x04 : 0xE8,    #   LATIN SMALL LETTER E WITH GRAVE
    0x05 : 0xE9,    #   LATIN SMALL LETTER E WITH ACUTE
    0x06 : 0xF9,    #   LATIN SMALL LETTER U WITH GRAVE
    0x07 : 0xEC,    #   LATIN SMALL LETTER I WITH GRAVE
    0x08 : 0xF2,    #   LATIN SMALL LETTER O WITH GRAVE
    0x09 : 0xC7,    #   LATIN LARGE LETTER C WITH CEDILLA
    0x0A : 0x0A,    #   LINE FEED
    0x0B : 0xD8,    #   LATIN CAPITAL LETTER O WITH STROKE
    0x0C : 0xF8,    #   LATIN SMALL LETTER O WITH STROKE
    0x0D : 0x0D,    #   CARRIAGE RETURN
    0x0E : 0xC5,    #   LATIN CAPITAL LETTER A WITH RING ABOVE
    0x0F : 0xE5,    #   LATIN SMALL LETTER A WITH RING ABOVE
    0x10 : 0x0394,  #   GREEK CAPITAL LETTER DELTA
    0x11 : 0x5F,    #   LOW LINE
    0x12 : 0x3A6,   #   GREEK CAPITAL LETTER PHI
    0x13 : 0x393,   #   GREEK CAPITAL LETTER GAMMA
    0x14 : 0x39B,   #   GREEK CAPITAL LETTER LAMDA
    0x15 : 0x3A9,   #   GREEK CAPITAL LETTER OMEGA
    0x16 : 0x3A0,   #   GREEK CAPITAL LETTER PI
    0x17 : 0x3A8,   #   GREEK CAPITAL LETTER PSI
    0x18 : 0x3A3,   #   GREEK CAPITAL LETTER SIGMA
    0x19 : 0x398,   #   GREEK CAPITAL LETTER THETA
    0x1A : 0x39E,   #   GREEK CAPITAL LETTER XI
    0x1B : 0xA0,    #   ESCAPE TO EXTENSION TABLE (or as NBSP, see note above)
    0x1B0A : 0x0C,  #   FORM FEED
    0x1B14 : 0x5E,  #   CIRCUMFLEX ACCENT
    0x1B28 : 0x7B,  #   LEFT CURLY BRACKET
    0x1B29 : 0x7D,  #   RIGHT CURLY BRACKET
    0x1B2F : 0x5C,  #   REVERSE SOLIDUS
    0x1B3C : 0x5B,  #   LEFT SQUARE BRACKET
    0x1B3D : 0x7E,  #   TILDE
    0x1B3E : 0x5D,  #   RIGHT SQUARE BRACKET
    0x1B40 : 0x7C,  #   VERTICAL LINE
    0x1B65 : 0x20AC,#   EURO SIGN
    0x1C : 0xC6,    #   LATIN CAPITAL LETTER AE
    0x1D : 0xE6,    #   LATIN SMALL LETTER AE
    0x1E : 0xDF,    #   LATIN SMALL LETTER SHARP S (German)
    0x1F : 0xC9,    #   LATIN CAPITAL LETTER E WITH ACUTE
    0x20 : 0x20,    #   SPACE
    0x21 : 0x21,    #   EXCLAMATION MARK
    0x22 : 0x22,    #   QUOTATION MARK
    0x23 : 0x23,    #   NUMBER SIGN
    0x24 : 0xA4,    #   CURRENCY SIGN
    0x25 : 0x25,    #   PERCENT SIGN
    0x26 : 0x26,    #   AMPERSAND
    0x27 : 0x27,    #   APOSTROPHE
    0x28 : 0x28,    #   LEFT PARENTHESIS
    0x29 : 0x29,    #   RIGHT PARENTHESIS
    0x2A : 0x2A,    #   ASTERISK
    0x2B : 0x2B,    #   PLUS SIGN
    0x2C : 0x2C,    #   COMMA
    0x2D : 0x2D,    #   HYPHEN-MINUS
    0x2E : 0x2E,    #   FULL STOP
    0x2F : 0x2F,    #   SOLIDUS
    0x30 : 0x30,    #   DIGIT ZERO
    0x31 : 0x31,    #   DIGIT ONE
    0x32 : 0x32,    #   DIGIT TWO
    0x33 : 0x33,    #   DIGIT THREE
    0x34 : 0x34,    #   DIGIT FOUR
    0x35 : 0x35,    #   DIGIT FIVE
    0x36 : 0x36,    #   DIGIT SIX
    0x37 : 0x37,    #   DIGIT SEVEN
    0x38 : 0x38,    #   DIGIT EIGHT
    0x39 : 0x39,    #   DIGIT NINE
    0x3A : 0x3A,    #   COLON
    0x3B : 0x3B,    #   SEMICOLON
    0x3C : 0x3C,    #   LESS-THAN SIGN
    0x3D : 0x3D,    #   EQUALS SIGN
    0x3E : 0x3E,    #   GREATER-THAN SIGN
    0x3F : 0x3F,    #   QUESTION MARK
    0x40 : 0xA1,    #   INVERTED EXCLAMATION MARK
    0x41 : 0x41,    #   LATIN CAPITAL LETTER A
    0x42 : 0x42,    #   LATIN CAPITAL LETTER B
    0x43 : 0x43,    #   LATIN CAPITAL LETTER C
    0x44 : 0x44,    #   LATIN CAPITAL LETTER D
    0x45 : 0x45,    #   LATIN CAPITAL LETTER E
    0x46 : 0x46,    #   LATIN CAPITAL LETTER F
    0x47 : 0x47,    #   LATIN CAPITAL LETTER G
    0x48 : 0x48,    #   LATIN CAPITAL LETTER H
    0x49 : 0x49,    #   LATIN CAPITAL LETTER I
    0x4A : 0x4A,    #   LATIN CAPITAL LETTER J
    0x4B : 0x4B,    #   LATIN CAPITAL LETTER K
    0x4C : 0x4C,    #   LATIN CAPITAL LETTER L
    0x4D : 0x4D,    #   LATIN CAPITAL LETTER M
    0x4E : 0x4E,    #   LATIN CAPITAL LETTER N
    0x4F : 0x4F,    #   LATIN CAPITAL LETTER O
    0x50 : 0x50,    #   LATIN CAPITAL LETTER P
    0x51 : 0x51,    #   LATIN CAPITAL LETTER Q
    0x52 : 0x52,    #   LATIN CAPITAL LETTER R
    0x53 : 0x53,    #   LATIN CAPITAL LETTER S
    0x54 : 0x54,    #   LATIN CAPITAL LETTER T
    0x55 : 0x55,    #   LATIN CAPITAL LETTER U
    0x56 : 0x56,    #   LATIN CAPITAL LETTER V
    0x57 : 0x57,    #   LATIN CAPITAL LETTER W
    0x58 : 0x58,    #   LATIN CAPITAL LETTER X
    0x59 : 0x59,    #   LATIN CAPITAL LETTER Y
    0x5A : 0x5A,    #   LATIN CAPITAL LETTER Z
    0x5B : 0xC4,    #   LATIN CAPITAL LETTER A WITH DIAERESIS
    0x5C : 0xD6,    #   LATIN CAPITAL LETTER O WITH DIAERESIS
    0x5D : 0xD1,    #   LATIN CAPITAL LETTER N WITH TILDE
    0x5E : 0xDC,    #   LATIN CAPITAL LETTER U WITH DIAERESIS
    0x5F : 0xA7,    #   SECTION SIGN
    0x60 : 0xBF,    #   INVERTED QUESTION MARK
    0x61 : 0x61,    #   LATIN SMALL LETTER A
    0x62 : 0x62,    #   LATIN SMALL LETTER B
    0x63 : 0x63,    #   LATIN SMALL LETTER C
    0x64 : 0x64,    #   LATIN SMALL LETTER D
    0x65 : 0x65,    #   LATIN SMALL LETTER E
    0x66 : 0x66,    #   LATIN SMALL LETTER F
    0x67 : 0x67,    #   LATIN SMALL LETTER G
    0x68 : 0x68,    #   LATIN SMALL LETTER H
    0x69 : 0x69,    #   LATIN SMALL LETTER I
    0x6A : 0x6A,    #   LATIN SMALL LETTER J
    0x6B : 0x6B,    #   LATIN SMALL LETTER K
    0x6C : 0x6C,    #   LATIN SMALL LETTER L
    0x6D : 0x6D,    #   LATIN SMALL LETTER M
    0x6E : 0x6E,    #   LATIN SMALL LETTER N
    0x6F : 0x6F,    #   LATIN SMALL LETTER O
    0x70 : 0x70,    #   LATIN SMALL LETTER P
    0x71 : 0x71,    #   LATIN SMALL LETTER Q
    0x72 : 0x72,    #   LATIN SMALL LETTER R
    0x73 : 0x73,    #   LATIN SMALL LETTER S
    0x74 : 0x74,    #   LATIN SMALL LETTER T
    0x75 : 0x75,    #   LATIN SMALL LETTER U
    0x76 : 0x76,    #   LATIN SMALL LETTER V
    0x77 : 0x77,    #   LATIN SMALL LETTER W
    0x78 : 0x78,    #   LATIN SMALL LETTER X
    0x79 : 0x79,    #   LATIN SMALL LETTER Y
    0x7A : 0x7A,    #   LATIN SMALL LETTER Z
    0x7B : 0xE4,    #   LATIN SMALL LETTER A WITH DIAERESIS
    0x7C : 0xF6,    #   LATIN SMALL LETTER O WITH DIAERESIS
    0x7D : 0xF1,    #   LATIN SMALL LETTER N WITH TILDE
    0x7E : 0xFC,    #   LATIN SMALL LETTER U WITH DIAERESIS
    0x7F : 0xE0,    #   LATIN SMALL LETTER A WITH GRAVE
}

### Encoding table
encoding_map = codecs.make_encoding_map(decoding_table)

encoding_map.update({
    0xC0 : 0x41,
    0xC1 : 0x41,
    0xC2 : 0x41,
    0xC3 : 0x41,
    0xC8 : 0x45,
    0xC9 : 0x45,
    0xCA : 0x45,
    0xCB : 0x45,
    0xCC : 0x49,
    0xCD : 0x49,
    0xCE : 0x49,
    0xCF : 0x49,
    0xD2 : 0x4F,
    0xD3 : 0x4F,
    0xD4 : 0x4F,
    0xD5 : 0x4F,
    0xD9 : 0x55,
    0xDA : 0x55,
    0xDB : 0x55,
    0xDD : 0x59,
    0xE1 : 0x61,
    0xE2 : 0x61,
    0xE3 : 0x61,
    0xE7 : 0x09,
    0xE9 : 0x65,
    0xEA : 0x65,
    0xEB : 0x65,
    0xED : 0x69,
    0xEE : 0x69,
    0xEF : 0x69,
    0xF3 : 0x6F,
    0xF3 : 0x6F,
    0xF4 : 0x6F,
    0xF5 : 0x6F,
    0xFA : 0x75,
    0xFB : 0x75,
    0xFD : 0x79,
    0xFF : 0x79,
})

### Detect if a given text can represent it as gsm text
def is_valid_gsm_text(text):
    try:
        text.encode("gsm0338")
    except:
        return False

    return True

### Registering Codec
codecs.register(getregentry)

