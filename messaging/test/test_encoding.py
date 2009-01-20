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

    def test_encoding_7bit_to_store_message(self):
        number = "+34123456"
        csca = "+34987654"
        text = "hey there"
        expected = "0591438967450100089143214365000009E8721E444797E565"

        pdu = self.pdu.encode_pdu(number, text, csca=csca, msgvp=0x00)[0]
        self.assertEqual(pdu[1], expected)

    def test_encoding_ucs2_message(self):
        number = "+34616585119"
        text = u'あ叶葉'
        csca = '+34646456456'
        expected = "07914346466554F611000B914316565811F90008AA06304253F68449"

        pdu = self.pdu.encode_pdu(number, text, csca=csca)[0]
        self.assertEqual(pdu[1], expected)

