# -*- coding: utf-8 -*-
# Copyright (C) 2011  Sphere Systems Ltd
# Author:  Andrew Bird
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
"""Unittests for the gsm encoding/decoding module"""

import unittest
import messaging.sms.gsm0338  # imports GSM7 codec

# Reversed from: ftp://ftp.unicode.org/Public/MAPPINGS/ETSI/GSM0338.TXT
MAP = {
#    unichr(0x0000): (0x0000, 0x00),  # Null
    u'@': (0x0040, 0x00),
    u'£': (0x00a3, 0x01),
    u'$': (0x0024, 0x02),
    u'¥': (0x00a5, 0x03),
    u'è': (0x00e8, 0x04),
    u'é': (0x00e9, 0x05),
    u'ù': (0x00f9, 0x06),
    u'ì': (0x00ec, 0x07),
    u'ò': (0x00f2, 0x08),
    u'Ç': (0x00c7, 0x09),  #   LATIN CAPITAL LETTER C WITH CEDILLA
    unichr(0x000a): (0x000a, 0x0a),  # Linefeed
    u'Ø': (0x00d8, 0x0b),
    u'ø': (0x00f8, 0x0c),
    unichr(0x000d): (0x000d, 0x0d),  # Carriage return
    u'Å': (0x00c5, 0x0e),
    u'å': (0x00e5, 0x0f),
    u'Δ': (0x0394, 0x10),
    u'_': (0x005f, 0x11),
    u'Φ': (0x03a6, 0x12),
    u'Γ': (0x0393, 0x13),
    u'Λ': (0x039b, 0x14),
    u'Ω': (0x03a9, 0x15),
    u'Π': (0x03a0, 0x16),
    u'Ψ': (0x03a8, 0x17),
    u'Σ': (0x03a3, 0x18),
    u'Θ': (0x0398, 0x19),
    u'Ξ': (0x039e, 0x1a),
    unichr(0x00a0): (0x00a0, 0x1b),  #  Escape to extension table (displayed
                                     #  as NBSP, on decode of invalid escape
                                     #  sequence)
    u'Æ': (0x00c6, 0x1c),
    u'æ': (0x00e6, 0x1d),
    u'ß': (0x00df, 0x1e),
    u'É': (0x00c9, 0x1f),
    u' ': (0x0020, 0x20),
    u'!': (0x0021, 0x21),
    u'"': (0x0022, 0x22),
    u'#': (0x0023, 0x23),
    u'¤': (0x00a4, 0x24),
    u'%': (0x0025, 0x25),
    u'&': (0x0026, 0x26),
    u'\'': (0x0027, 0x27),
    u'{': (0x007b, 0x1b28),
    u'}': (0x007d, 0x1b29),
    u'*': (0x002a, 0x2a),
    u'+': (0x002b, 0x2b),
    u',': (0x002c, 0x2c),
    u'-': (0x002d, 0x2d),
    u'.': (0x002e, 0x2e),
    u'\\': (0x005c, 0x1b2f),
    u'0': (0x0030, 0x30),
    u'1': (0x0031, 0x31),
    u'2': (0x0032, 0x32),
    u'3': (0x0033, 0x33),
    u'4': (0x0034, 0x34),
    u'5': (0x0035, 0x35),
    u'6': (0x0036, 0x36),
    u'7': (0x0037, 0x37),
    u'8': (0x0038, 0x38),
    u'9': (0x0039, 0x39),
    u':': (0x003a, 0x3a),
    u';': (0x003b, 0x3b),
    u'[': (0x005b, 0x1b3c),
    unichr(0x000c): (0x000c, 0x1b0a),  # Formfeed
    u']': (0x005d, 0x1b3e),
    u'?': (0x003f, 0x3f),
    u'|': (0x007c, 0x1b40),
    u'A': (0x0041, 0x41),
    u'B': (0x0042, 0x42),
    u'C': (0x0043, 0x43),
    u'D': (0x0044, 0x44),
    u'E': (0x0045, 0x45),
    u'F': (0x0046, 0x46),
    u'G': (0x0047, 0x47),
    u'H': (0x0048, 0x48),
    u'I': (0x0049, 0x49),
    u'J': (0x004a, 0x4a),
    u'K': (0x004b, 0x4b),
    u'L': (0x004c, 0x4c),
    u'M': (0x004d, 0x4d),
    u'N': (0x004e, 0x4e),
    u'O': (0x004f, 0x4f),
    u'P': (0x0050, 0x50),
    u'Q': (0x0051, 0x51),
    u'R': (0x0052, 0x52),
    u'S': (0x0053, 0x53),
    u'T': (0x0054, 0x54),
    u'U': (0x0055, 0x55),
    u'V': (0x0056, 0x56),
    u'W': (0x0057, 0x57),
    u'X': (0x0058, 0x58),
    u'Y': (0x0059, 0x59),
    u'Z': (0x005a, 0x5a),
    u'Ä': (0x00c4, 0x5b),
    u'Ö': (0x00d6, 0x5c),
    u'Ñ': (0x00d1, 0x5d),
    u'Ü': (0x00dc, 0x5e),
    u'§': (0x00a7, 0x5f),
    u'¿': (0x00bf, 0x60),
    u'a': (0x0061, 0x61),
    u'b': (0x0062, 0x62),
    u'c': (0x0063, 0x63),
    u'd': (0x0064, 0x64),
    u'€': (0x20ac, 0x1b65),
    u'f': (0x0066, 0x66),
    u'g': (0x0067, 0x67),
    u'h': (0x0068, 0x68),
    u'<': (0x003c, 0x3c),
    u'j': (0x006a, 0x6a),
    u'k': (0x006b, 0x6b),
    u'l': (0x006c, 0x6c),
    u'm': (0x006d, 0x6d),
    u'n': (0x006e, 0x6e),
    u'~': (0x007e, 0x1b3d),
    u'p': (0x0070, 0x70),
    u'q': (0x0071, 0x71),
    u'r': (0x0072, 0x72),
    u's': (0x0073, 0x73),
    u't': (0x0074, 0x74),
    u'>': (0x003e, 0x3e),
    u'v': (0x0076, 0x76),
    u'i': (0x0069, 0x69),
    u'x': (0x0078, 0x78),
    u'^': (0x005e, 0x1b14),
    u'z': (0x007a, 0x7a),
    u'ä': (0x00e4, 0x7b),
    u'ö': (0x00f6, 0x7c),
    u'ñ': (0x00f1, 0x7d),
    u'ü': (0x00fc, 0x7e),
    u'à': (0x00e0, 0x7f),
    u'¡': (0x00a1, 0x40),
    u'/': (0x002f, 0x2f),
    u'o': (0x006f, 0x6f),
    u'u': (0x0075, 0x75),
    u'w': (0x0077, 0x77),
    u'y': (0x0079, 0x79),
    u'e': (0x0065, 0x65),
    u'=': (0x003d, 0x3d),
    u'(': (0x0028, 0x28),
    u')': (0x0029, 0x29),
}

GREEK_MAP = {  # Note: these might look like Latin uppercase, but they aren't
    u'Α': (0x0391, 0x41),
    u'Β': (0x0392, 0x42),
    u'Ε': (0x0395, 0x45),
    u'Η': (0x0397, 0x48),
    u'Ι': (0x0399, 0x49),
    u'Κ': (0x039a, 0x4b),
    u'Μ': (0x039c, 0x4d),
    u'Ν': (0x039d, 0x4e),
    u'Ο': (0x039f, 0x4f),
    u'Ρ': (0x03a1, 0x50),
    u'Τ': (0x03a4, 0x54),
    u'Χ': (0x03a7, 0x58),
    u'Υ': (0x03a5, 0x59),
    u'Ζ': (0x0396, 0x5a),
}

QUIRK_MAP = {
    u'ç': (0x00e7, 0x09),
}

BAD = -1


class TestEncodingFunctions(unittest.TestCase):

    def test_encoding_supported_unicode_gsm(self):

        for key in MAP.keys():
            # Use 'ignore' so that we see the code tested, not an exception
            s_gsm = key.encode('gsm0338', 'ignore')

            if len(s_gsm) == 1:
                i_gsm = ord(s_gsm)
            elif len(s_gsm) == 2:
                i_gsm = (ord(s_gsm[0]) << 8) + ord(s_gsm[1])
            else:
                i_gsm = BAD  # so we see the comparison, not an exception

            # We shouldn't generate an invalid escape sequence
            if key == unichr(0x00a0):
                self.assertEqual(BAD, i_gsm)
            else:
                self.assertEqual(MAP[key][1], i_gsm)

    def test_encoding_supported_greek_unicode_gsm(self):
        # Note: Conversion is one way, hence no corresponding decode test

        for key in GREEK_MAP.keys():
            # Use 'replace' so that we trigger the mapping
            s_gsm = key.encode('gsm0338', 'replace')

            if len(s_gsm) == 1:
                i_gsm = ord(s_gsm)
            else:
                i_gsm = BAD  # so we see the comparison, not an exception

            self.assertEqual(GREEK_MAP[key][1], i_gsm)

    def test_encoding_supported_quirk_unicode_gsm(self):
        # Note: Conversion is one way, hence no corresponding decode test

        for key in QUIRK_MAP.keys():
            # Use 'replace' so that we trigger the mapping
            s_gsm = key.encode('gsm0338', 'replace')

            if len(s_gsm) == 1:
                i_gsm = ord(s_gsm)
            else:
                i_gsm = BAD  # so we see the comparison, not an exception

            self.assertEqual(QUIRK_MAP[key][1], i_gsm)

    def test_decoding_supported_unicode_gsm(self):
        for key in MAP.keys():
            i_gsm = MAP[key][1]
            if i_gsm <= 0xff:
                s_gsm = chr(i_gsm)
            elif i_gsm <= 0xffff:
                s_gsm = chr((i_gsm & 0xff00) >> 8)
                s_gsm += chr(i_gsm & 0x00ff)

            s_unicode = s_gsm.decode('gsm0338', 'strict')
            self.assertEqual(MAP[key][0], ord(s_unicode))

    def test_is_gsm_text_true(self):
        for key in MAP.keys():
            if key == unichr(0x00a0):
                continue
            self.assertEqual(messaging.sms.gsm0338.is_gsm_text(key), True)

    def test_is_gsm_text_false(self):
        self.assertEqual(
            messaging.sms.gsm0338.is_gsm_text(unichr(0x00a0)), False)

        for i in xrange(1, 0xffff + 1):
            if unichr(i) not in MAP:
                # Note: it's a little odd, but on error we want to see values
                if messaging.sms.gsm0338.is_gsm_text(unichr(i)) is not False:
                    self.assertEqual(BAD, i)
