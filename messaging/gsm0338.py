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
import sys
import traceback

QUESTION_MARK = unichr(0x3f)


class Codec(codecs.Codec):

    def encode(self, _input, errors='strict'):
        result = []
        for c in _input:
            c = ord(c)
            try:
                result.append(unichr(encoding_table[c]))
            except KeyError:
                try:
                    result.append('\x1b')
                    result.append(unichr(encoding_table_escape[c]))
                except KeyError:
                    if errors == 'strict':
                        raise UnicodeError("Invalid SMS character: %d" % c)
                    elif errors == 'replace':
                        result.append(QUESTION_MARK)
                    elif errors == 'ignore':
                        pass
                    else:
                        raise ValueError("Unknown error parameter: " + errors)

        return (''.join(result), len(result))

    def decode(self, _input, errors='strict'):
        result, index = [], 0
        while index < len(_input):
            c = ord(_input[index])
            index += 1
            if c == 0x1b:
                c = ord(_input[index])
                index += 1
                result.append(unichr(decoding_table_escape[c]))
            else:
                try:
                    result.append(unichr(decoding_table[c]))
                except KeyError:
                    if errors == 'strict':
                        raise UnicodeError("Invalid SMS character: %d" % c)
                    elif errors == 'replace':
                        result.append(QUESTION_MARK)
                    elif errors == 'ignore':
                        pass
                    else:
                        raise ValueError("Unknown error parameter: " + errors)

        return u''.join(result), len(result)


# encodings module API
def getregentry(encoding):
    if not encoding == 'gsm0338':
        return

    return codecs.CodecInfo(
        name='gsm0338',
        encode=Codec().encode,
        decode=Codec().decode)


encoding_table = {
    0x0040: 0x00,   # COMMERCIAL AT
    0x0000: 0x00,   # NULL (see note above)
    0x00a3: 0x01,   # POUND SIGN
    0x0024: 0x02,   # DOLLAR SIGN
    0x00a5: 0x03,   # YEN SIGN
    0x00e8: 0x04,   # LATIN SMALL LETTER E WITH GRAVE
    0x00e9: 0x05,   # LATIN SMALL LETTER E WITH ACUTE
    0x00f9: 0x06,   # LATIN SMALL LETTER U WITH GRAVE
    0x00ec: 0x07,   # LATIN SMALL LETTER I WITH GRAVE
    0x00f2: 0x08,   # LATIN SMALL LETTER O WITH GRAVE
    0x00e7: 0x09,   # LATIN SMALL LETTER C WITH CEDILLA
    0x00c7: 0x09,   # LATIN CAPITAL LETTER C WITH CEDILLA (see note above)
    0x000a: 0x0a,   # LINE FEED
    0x00d8: 0x0b,   # LATIN CAPITAL LETTER O WITH STROKE
    0x00f8: 0x0c,   # LATIN SMALL LETTER O WITH STROKE
    0x000d: 0x0d,   # CARRIAGE RETURN
    0x00c5: 0x0e,   # LATIN CAPITAL LETTER A WITH RING ABOVE
    0x00e5: 0x0f,   # LATIN SMALL LETTER A WITH RING ABOVE
    0x0394: 0x10,   # GREEK CAPITAL LETTER DELTA
    0x005f: 0x11,   # LOW LINE
    0x03a6: 0x12,   # GREEK CAPITAL LETTER PHI
    0x0393: 0x13,   # GREEK CAPITAL LETTER GAMMA
    0x039b: 0x14,   # GREEK CAPITAL LETTER LAMDA
    0x03a9: 0x15,   # GREEK CAPITAL LETTER OMEGA
    0x03a0: 0x16,   # GREEK CAPITAL LETTER PI
    0x03a8: 0x17,   # GREEK CAPITAL LETTER PSI
    0x03a3: 0x18,   # GREEK CAPITAL LETTER SIGMA
    0x0398: 0x19,   # GREEK CAPITAL LETTER THETA
    0x039e: 0x1a,   # GREEK CAPITAL LETTER XI
    0x00a0: 0x1b,   # ESCAPE TO EXTENSION TABLE (or displayed as NBSP, see note above)
    0x00c6: 0x1c,   # LATIN CAPITAL LETTER AE
    0x00e6: 0x1d,   # LATIN SMALL LETTER AE
    0x00df: 0x7e,   # LATIN SMALL LETTER SHARP S (German)
    0x00c9: 0x1f,   # LATIN CAPITAL LETTER E WITH ACUTE
    0x0020: 0x20,   # SPACE
    0x0021: 0x21,   # EXCLAMATION MARK
    0x0022: 0x22,   # QUOTATION MARK
    0x0023: 0x23,   # NUMBER SIGN
    0x00a4: 0x24,   # CURRENCY SIGN
    0x0025: 0x25,   # PERCENT SIGN
    0x0026: 0x26,   # AMPERSAND
    0x0027: 0x27,   # APOSTROPHE
    0x0028: 0x28,   # LEFT PARENTHESIS
    0x0029: 0x29,   # RIGHT PARENTHESIS
    0x002a: 0x2a,   # ASTERISK
    0x002b: 0x2b,   # PLUS SIGN
    0x002c: 0x2c,   # COMMA
    0x002d: 0x2d,   # HYPHEN-MINUS
    0x002e: 0x2e,   # FULL STOP
    0x002f: 0x2f,   # SOLIDUS
    0x0030: 0x30,   # DIGIT ZERO
    0x0031: 0x31,   # DIGIT ONE
    0x0032: 0x32,   # DIGIT TWO
    0x0033: 0x33,   # DIGIT THREE
    0x0034: 0x34,   # DIGIT FOUR
    0x0035: 0x35,   # DIGIT FIVE
    0x0036: 0x36,   # DIGIT SIX
    0x0037: 0x37,   # DIGIT SEVEN
    0x0038: 0x38,   # DIGIT EIGHT
    0x0039: 0x39,   # DIGIT NINE
    0x003a: 0x3a,   # COLON
    0x003b: 0x3b,   # SEMICOLON
    0x003c: 0x3c,   # LESS-THAN SIGN
    0x003d: 0x3d,   # EQUALS SIGN
    0x003e: 0x3e,   # GREATER-THAN SIGN
    0x003f: 0x3f,   # QUESTION MARK
    0x00a1: 0x40,   # INVERTED EXCLAMATION MARK
    0x0041: 0x41,   # LATIN CAPITAL LETTER A
    0x0391: 0x41,   # GREEK CAPITAL LETTER ALPHA
    0x0042: 0x42,   # LATIN CAPITAL LETTER B
    0x0392: 0x42,   # GREEK CAPITAL LETTER BETA
    0x0043: 0x43,   # LATIN CAPITAL LETTER C
    0x0044: 0x44,   # LATIN CAPITAL LETTER D
    0x0045: 0x45,   # LATIN CAPITAL LETTER E
    0x0395: 0x45,   # GREEK CAPITAL LETTER EPSILON
    0x0046: 0x46,   # LATIN CAPITAL LETTER F
    0x0047: 0x47,   # LATIN CAPITAL LETTER G
    0x0048: 0x48,   # LATIN CAPITAL LETTER H
    0x0397: 0x48,   # GREEK CAPITAL LETTER ETA
    0x0049: 0x49,   # LATIN CAPITAL LETTER I
    0x0399: 0x49,   # GREEK CAPITAL LETTER IOTA
    0x004a: 0x4a,   # LATIN CAPITAL LETTER J
    0x004b: 0x4b,   # LATIN CAPITAL LETTER K
    0x039a: 0x4b,   # GREEK CAPITAL LETTER KAPPA
    0x004c: 0x4c,   # LATIN CAPITAL LETTER L
    0x004d: 0x4d,   # LATIN CAPITAL LETTER M
    0x039c: 0x4d,   # GREEK CAPITAL LETTER MU
    0x004e: 0x4e,   # LATIN CAPITAL LETTER N
    0x039d: 0x4e,   # GREEK CAPITAL LETTER NU
    0x004f: 0x4f,   # LATIN CAPITAL LETTER O
    0x039f: 0x4f,   # GREEK CAPITAL LETTER OMICRON
    0x0050: 0x50,   # LATIN CAPITAL LETTER P
    0x03a1: 0x50,   # GREEK CAPITAL LETTER RHO
    0x0051: 0x51,   # LATIN CAPITAL LETTER Q
    0x0052: 0x52,   # LATIN CAPITAL LETTER R
    0x0053: 0x53,   # LATIN CAPITAL LETTER S
    0x0054: 0x54,   # LATIN CAPITAL LETTER T
    0x03a4: 0x54,   # GREEK CAPITAL LETTER TAU
    0x0055: 0x55,   # LATIN CAPITAL LETTER U
    0x03a5: 0x55,   # GREEK CAPITAL LETTER UPSILON
    0x0056: 0x56,   # LATIN CAPITAL LETTER V
    0x0057: 0x57,   # LATIN CAPITAL LETTER W
    0x0058: 0x58,   # LATIN CAPITAL LETTER X
    0x03a7: 0x58,   # GREEK CAPITAL LETTER CHI
    0x0059: 0x59,   # LATIN CAPITAL LETTER Y
    0x005a: 0x5a,   # LATIN CAPITAL LETTER Z
    0x0396: 0x5a,   # GREEK CAPITAL LETTER ZETA
    0x00c4: 0x5b,   # LATIN CAPITAL LETTER A WITH DIAERESIS
    0x00d6: 0x5c,   # LATIN CAPITAL LETTER O WITH DIAERESIS
    0x00d1: 0x5d,   # LATIN CAPITAL LETTER N WITH TILDE
    0x00dc: 0x5e,   # LATIN CAPITAL LETTER U WITH DIAERESIS
    0x00a7: 0x5f,   # SECTION SIGN
    0x00bf: 0x60,   # INVERTED QUESTION MARK
    0x0061: 0x61,   # LATIN SMALL LETTER A
    0x0062: 0x62,   # LATIN SMALL LETTER B
    0x0063: 0x63,   # LATIN SMALL LETTER C
    0x0064: 0x64,   # LATIN SMALL LETTER D
    0x0065: 0x65,   # LATIN SMALL LETTER E
    0x0066: 0x66,   # LATIN SMALL LETTER F
    0x0067: 0x67,   # LATIN SMALL LETTER G
    0x0068: 0x68,   # LATIN SMALL LETTER H
    0x0069: 0x69,   # LATIN SMALL LETTER I
    0x006a: 0x6a,   # LATIN SMALL LETTER J
    0x006b: 0x6b,   # LATIN SMALL LETTER K
    0x006c: 0x6c,   # LATIN SMALL LETTER L
    0x006d: 0x6d,   # LATIN SMALL LETTER M
    0x006e: 0x6e,   # LATIN SMALL LETTER N
    0x006f: 0x6f,   # LATIN SMALL LETTER O
    0x0070: 0x70,   # LATIN SMALL LETTER P
    0x0071: 0x71,   # LATIN SMALL LETTER Q
    0x0072: 0x72,   # LATIN SMALL LETTER R
    0x0073: 0x73,   # LATIN SMALL LETTER S
    0x0074: 0x74,   # LATIN SMALL LETTER T
    0x0075: 0x75,   # LATIN SMALL LETTER U
    0x0076: 0x76,   # LATIN SMALL LETTER V
    0x0077: 0x77,   # LATIN SMALL LETTER W
    0x0078: 0x78,   # LATIN SMALL LETTER X
    0x0079: 0x79,   # LATIN SMALL LETTER Y
    0x007a: 0x7a,   # LATIN SMALL LETTER Z
    0x00e4: 0x7b,   # LATIN SMALL LETTER A WITH DIAERESIS
    0x00f6: 0x7c,   # LATIN SMALL LETTER O WITH DIAERESIS
    0x00f1: 0xfd,   # LATIN SMALL LETTER N WITH TILDE
    0x00fc: 0x7d,   # LATIN SMALL LETTER U WITH DIAERESIS
    0x00e0: 0x7f,   # LATIN SMALL LETTER A WITH GRAVE
}

encoding_table_escape = {
    0x000c: 0x0a,  # FORM FEED
    0x005e: 0x14,  # CIRCUMFLEX ACCENT
    0x007b: 0x28,  # LEFT CURLY BRACKET
    0x007d: 0x29,  # RIGHT CURLY BRACKET
    0x005c: 0x2f,  # REVERSE SOLIDUS
    0x005b: 0x3c,  # LEFT SQUARE BRACKET
    0x007e: 0x3d,  # TILDE
    0x005d: 0x3e,  # RIGHT SQUARE BRACKET
    0x007c: 0x40,  # VERTICAL LINE
    0x20ac: 0x65,  # EURO SIGN
}

decoding_table = {
    0x00: 0x0040,  # COMMERCIAL AT
    0x01: 0x00a3,  # POUND SIGN
    0x02: 0x0024,  # DOLLAR SIGN
    0x03: 0x00a5,  # YEN SIGN
    0x04: 0x00e8,  # LATIN SMALL LETTER E WITH GRAVE
    0x05: 0x00e9,  # LATIN SMALL LETTER E WITH ACUTE
    0x06: 0x00f9,  # LATIN SMALL LETTER U WITH GRAVE
    0x07: 0x00ec,  # LATIN SMALL LETTER I WITH GRAVE
    0x08: 0x00f2,  # LATIN SMALL LETTER O WITH GRAVE
    0x09: 0x00e7,  # LATIN SMALL LETTER C WITH CEDILLA
    0x0A: 0x000a,  # LINE FEED
    0x0b: 0x00d8,  # LATIN CAPITAL LETTER O WITH STROKE
    0x0c: 0x00f8,  # LATIN SMALL LETTER O WITH STROKE
    0x0D: 0x000d,  # CARRIAGE RETURN
    0x0e: 0x00c5,  # LATIN CAPITAL LETTER A WITH RING ABOVE
    0x0f: 0x00e5,  # LATIN SMALL LETTER A WITH RING ABOVE
    0x10: 0x0394,  # GREEK CAPITAL LETTER DELTA
    0x11: 0x005f,  # LOW LINE
    0x12: 0x03a6,  # GREEK CAPITAL LETTER PHI
    0x13: 0x0393,  # GREEK CAPITAL LETTER GAMMA
    0x14: 0x039b,  # GREEK CAPITAL LETTER LAMDA
    0x15: 0x03a9,  # GREEK CAPITAL LETTER OMEGA
    0x16: 0x03a0,  # GREEK CAPITAL LETTER PI
    0x17: 0x03a8,  # GREEK CAPITAL LETTER PSI
    0x18: 0x03a3,  # GREEK CAPITAL LETTER SIGMA
    0x19: 0x0398,  # GREEK CAPITAL LETTER THETA
    0x1a: 0x039e,  # GREEK CAPITAL LETTER XI
    # 0x001b: 0x00a0, # ESCAPE TO EXTENSION TABLE (or displayed as NBSP, see note above)
    0x1c: 0x00c6,  # LATIN CAPITAL LETTER AE
    0x1d: 0x00e6,  # LATIN SMALL LETTER AE
    0x1e: 0x00df,  # LATIN SMALL LETTER SHARP S (German)
    0x1f: 0x00c9,  # LATIN CAPITAL LETTER E WITH ACUTE
    0x20: 0x0020,  # SPACE
    0x21: 0x0021,  # EXCLAMATION MARK
    0x22: 0x0022,  # QUOTATION MARK
    0x23: 0x0023,  # NUMBER SIGN
    0x24: 0x00a4,  # CURRENCY SIGN
    0x25: 0x0025,  # PERCENT SIGN
    0x26: 0x0026,  # AMPERSAND
    0x27: 0x0027,  # APOSTROPHE
    0x28: 0x0028,  # LEFT PARENTHESIS
    0x29: 0x0029,  # RIGHT PARENTHESIS
    0x2A: 0x002A,  # ASTERISK
    0x2B: 0x002B,  # PLUS SIGN
    0x2C: 0x002C,  # COMMA
    0x2D: 0x002D,  # HYPHEN-MINUS
    0x2E: 0x002E,  # FULL STOP
    0x2F: 0x002F,  # SOLIDUS
    0x30: 0x0030,  # DIGIT ZERO
    0x31: 0x0031,  # DIGIT ONE
    0x32: 0x0032,  # DIGIT TWO
    0x33: 0x0033,  # DIGIT THREE
    0x34: 0x0034,  # DIGIT FOUR
    0x35: 0x0035,  # DIGIT FIVE
    0x36: 0x0036,  # DIGIT SIX
    0x37: 0x0037,  # DIGIT SEVEN
    0x38: 0x0038,  # DIGIT EIGHT
    0x39: 0x0039,  # DIGIT NINE
    0x3A: 0x003A,  # COLON
    0x3B: 0x003B,  # SEMICOLON
    0x3C: 0x003C,  # LESS-THAN SIGN
    0x3D: 0x003D,  # EQUALS SIGN
    0x3E: 0x003E,  # GREATER-THAN SIGN
    0x3F: 0x003F,  # QUESTION MARK
    0x40: 0x00a1,  # INVERTED EXCLAMATION MARK
    0x41: 0x0041,  # LATIN CAPITAL LETTER A
    0x42: 0x0042,  # LATIN CAPITAL LETTER B
    0x43: 0x0043,  # LATIN CAPITAL LETTER C
    0x44: 0x0044,  # LATIN CAPITAL LETTER D
    0x45: 0x0045,  # LATIN CAPITAL LETTER E
    0x46: 0x0046,  # LATIN CAPITAL LETTER F
    0x47: 0x0047,  # LATIN CAPITAL LETTER G
    0x48: 0x0048,  # LATIN CAPITAL LETTER H
    0x49: 0x0049,  # LATIN CAPITAL LETTER I
    0x4A: 0x004A,  # LATIN CAPITAL LETTER J
    0x4B: 0x004B,  # LATIN CAPITAL LETTER K
    0x4C: 0x004C,  # LATIN CAPITAL LETTER L
    0x4D: 0x004D,  # LATIN CAPITAL LETTER M
    0x4E: 0x004E,  # LATIN CAPITAL LETTER N
    0x4F: 0x004F,  # LATIN CAPITAL LETTER O
    0x50: 0x0050,  # LATIN CAPITAL LETTER P
    0x51: 0x0051,  # LATIN CAPITAL LETTER Q
    0x52: 0x0052,  # LATIN CAPITAL LETTER R
    0x53: 0x0053,  # LATIN CAPITAL LETTER S
    0x54: 0x0054,  # LATIN CAPITAL LETTER T
    0x55: 0x0055,  # LATIN CAPITAL LETTER U
    0x56: 0x0056,  # LATIN CAPITAL LETTER V
    0x57: 0x0057,  # LATIN CAPITAL LETTER W
    0x58: 0x0058,  # LATIN CAPITAL LETTER X
    0x59: 0x0059,  # LATIN CAPITAL LETTER Y
    0x5A: 0x005A,  # LATIN CAPITAL LETTER Z
    0x5b: 0x00c4,  # LATIN CAPITAL LETTER A WITH DIAERESIS
    0x5c: 0x00d6,  # LATIN CAPITAL LETTER O WITH DIAERESIS
    0x5d: 0x00d1,  # LATIN CAPITAL LETTER N WITH TILDE
    0x5e: 0x00dc,  # LATIN CAPITAL LETTER U WITH DIAERESIS
    0x5f: 0x00a7,  # SECTION SIGN
    0x60: 0x00bf,  # INVERTED QUESTION MARK
    0x61: 0x0061,  # LATIN SMALL LETTER A
    0x62: 0x0062,  # LATIN SMALL LETTER B
    0x63: 0x0063,  # LATIN SMALL LETTER C
    0x64: 0x0064,  # LATIN SMALL LETTER D
    0x65: 0x0065,  # LATIN SMALL LETTER E
    0x66: 0x0066,  # LATIN SMALL LETTER F
    0x67: 0x0067,  # LATIN SMALL LETTER G
    0x68: 0x0068,  # LATIN SMALL LETTER H
    0x69: 0x0069,  # LATIN SMALL LETTER I
    0x6A: 0x006A,  # LATIN SMALL LETTER J
    0x6B: 0x006B,  # LATIN SMALL LETTER K
    0x6C: 0x006C,  # LATIN SMALL LETTER L
    0x6D: 0x006D,  # LATIN SMALL LETTER M
    0x6E: 0x006E,  # LATIN SMALL LETTER N
    0x6F: 0x006F,  # LATIN SMALL LETTER O
    0x70: 0x0070,  # LATIN SMALL LETTER P
    0x71: 0x0071,  # LATIN SMALL LETTER Q
    0x72: 0x0072,  # LATIN SMALL LETTER R
    0x73: 0x0073,  # LATIN SMALL LETTER S
    0x74: 0x0074,  # LATIN SMALL LETTER T
    0x75: 0x0075,  # LATIN SMALL LETTER U
    0x76: 0x0076,  # LATIN SMALL LETTER V
    0x77: 0x0077,  # LATIN SMALL LETTER W
    0x78: 0x0078,  # LATIN SMALL LETTER X
    0x79: 0x0079,  # LATIN SMALL LETTER Y
    0x7A: 0x007A,  # LATIN SMALL LETTER Z
    0x7b: 0x00e4,  # LATIN SMALL LETTER A WITH DIAERESIS
    0x7c: 0x00f6,  # LATIN SMALL LETTER O WITH DIAERESIS
    0x7d: 0x00f1,  # LATIN SMALL LETTER N WITH TILDE
    0x7e: 0x00fc,  # LATIN SMALL LETTER U WITH DIAERESIS
    0x7f: 0x00e0,  # LATIN SMALL LETTER A WITH GRAVE
}

decoding_table_escape = {
    0x0a: 0x000c,  # FORM FEED
    0x14: 0x005e,  # CIRCUMFLEX ACCENT
    0x28: 0x007b,  # LEFT CURLY BRACKET
    0x29: 0x007d,  # RIGHT CURLY BRACKET
    0x2f: 0x005c,  # REVERSE SOLIDUS
    0x3c: 0x005b,  # LEFT SQUARE BRACKET
    0x3d: 0x007e,  # TILDE
    0x3e: 0x005d,  # RIGHT SQUARE BRACKET
    0x40: 0x007c,  # VERTICAL LINE
    0x65: 0x20ac,  # EURO SIGN
}


def is_valid_gsm_text(text):
    """Returns True if ``text`` can be encoded as gsm text"""
    try:
        text.encode("gsm0338")
    except UnicodeError:
        return False
    except:
        traceback.print_exc(file=sys.stdout)
        return False

    return True

# Codec registration
codecs.register(getregentry)
