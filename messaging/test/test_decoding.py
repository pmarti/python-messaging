# -*- coding: utf-8 -*-
import unittest

from messaging.pdu import PDU

class TestDecodingFunctions(unittest.TestCase):

    def setUp(self):
        self.pdu = PDU()

    def test_decoding_7bit_pdu(self):
        pdu = "07911326040000F0040B911346610089F60000208062917314080CC8F71D14969741F977FD07"
        expected = "How are you?"
        _csca = "+31624000000"
        number = "+31641600986"

        sender, datestr, text, csca, ref, cnt, seq, fmt = self.pdu.decode_pdu(pdu)
        self.assertEqual(text, expected)
        self.assertEqual(csca, _csca)
        self.assertEqual(number, sender)

    def test_decoding_7bit_stored_pdu(self):
        pdu = "0591438967450100089143214365000009E8721E444797E565"
        expected = "hey there"
        _csca = "+34987654"
        number = "+34123456"

        sender, datestr, text, csca, ref, cnt, seq, fmt = self.pdu.decode_pdu(pdu)
        self.assertEqual(csca, _csca)
        self.assertEqual(number, sender)
        self.assertEqual(text, expected)

    def test_decoding_ucs2_pdu(self):
        expected = u"中兴通讯"
        pdu = "07914306073011F0040B914316709807F2000880604290224080084E2D5174901A8BAF"
        _csca = "+34607003110"
        number = "+34610789702"

        sender, datestr, text, csca, ref, cnt, seq, fmt = self.pdu.decode_pdu(pdu)
        self.assertEqual(csca, _csca)
        self.assertEqual(number, sender)
        self.assertEqual(text, expected)

    def test_decoding_datetime_gmtplusone(self):
        expected = "1741 bst"
        pdu = "0791447758100650040C914497716247010000909010711423400A2050EC468B81C4733A"
        number = "+447917267410"
        _datestr = "09/09/01 16:41:32" # UTC

        sender, datestr, text, csca, ref, cnt, seq, fmt = self.pdu.decode_pdu(pdu)

        self.assertEqual(datestr, _datestr)
        self.assertEqual(number, sender)
        self.assertEqual(text, expected)

    def test_decoding_sender_alpha1(self): # Odd length test
        expected = "FONIC"
        pdu = "07919471060040340409D0C6A733390400009060920173018093CC74595C96838C4F6772085AD6DDE4320B444E9741D4B03C6D7EC3E9E9B71B9474D3CB727799DEA286CFE5B9991DA6CBC3F432E85E9793CBA0F09A9EB6A7CB72BA0B9474D3CB727799DE72D6E9FABAFB0CBAA7E56490BA4CD7D34170F91BE4ACD3F575F7794E0F9F4161F1B92C2F8FD1EE32DD054AA2E520E3D3991C82A8E5701B"

        sender, datestr, text, csca, ref, cnt, seq, fmt = self.pdu.decode_pdu(pdu)

        self.assertEqual(sender, expected)

    def test_decoding_sender_alpha2(self): # Even length test
        expected = "www.tim.it"
        pdu = "07919333852804000412D0F7FBDD454FB75D693A0000903002801153402BCD301E9F0605D9E971191483C140412A35690D52832063D2F9040599A058EE05A3BD6430580E"

        sender, datestr, text, csca, ref, cnt, seq, fmt = self.pdu.decode_pdu(pdu)

        self.assertEqual(sender, expected)

