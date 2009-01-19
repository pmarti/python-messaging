# -*- coding: utf-8 -*-
import unittest

from messaging.pdu import PDU

class TestEncodingFunctions(unittest.TestCase):

    def setUp(self):
        self.pdu = PDU()

    def test_encoding_7bit_message(self):
        number = "+34616585119"
        text = "hola"
        csca = "+34646456456"
        expected = "07914346466554F611000B914316565811F90000AA04E8373B0C"

        pdu = self.pdu.encode_pdu(number, text, csca=csca)[0]
        self.assertEqual(pdu[1], expected)

    def test_encoding_ucs2_message(self):
        number = "+34616585119"
        text = u'あ叶葉'
        csca = '+34646456456'
        expected = "07914346466554F611000B914316565811F90008AA06304253F68449"

        pdu = self.pdu.encode_pdu(number, text, csca=csca)[0]
        self.assertEqual(pdu[1], expected)

