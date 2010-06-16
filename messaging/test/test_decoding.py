# -*- coding: utf-8 -*-
import unittest

from messaging.pdu import PDU


class TestDecodingFunctions(unittest.TestCase):

    def setUp(self):
        self.pdu = PDU()

    def test_decoding_7bit_pdu(self):
        pdu = "07911326040000F0040B911346610089F60000208062917314080CC8F71D14969741F977FD07"
        text = "How are you?"
        csca = "+31624000000"
        number = "+31641600986"

        ret = self.pdu.decode_pdu(pdu)
        self.assertEqual(ret['text'], text)
        self.assertEqual(ret['csca'], csca)
        self.assertEqual(ret['number'], number)

    #def test_decoding_7bit_stored_pdu(self):
    #    pdu = "0591438967450100089143214365000009E8721E444797E565"
    #    text = "hey there"
    #    csca = "+34987654"
    #    number = "+34123456"

    #    ret = self.pdu.decode_pdu(pdu)
    #    self.assertEqual(ret['csca'], csca)
    #    self.assertEqual(ret['number'], number)
    #    self.assertEqual(ret['text'], text)

    def test_decoding_ucs2_pdu(self):
        pdu = "07914306073011F0040B914316709807F2000880604290224080084E2D5174901A8BAF"
        text = u"中兴通讯"
        csca = "+34607003110"
        number = "+34610789702"

        ret = self.pdu.decode_pdu(pdu)
        self.assertEqual(ret['text'], text)
        self.assertEqual(ret['csca'], csca)
        self.assertEqual(ret['number'], number)

    def test_decoding_datetime_gmtplusone(self):
        pdu = "0791447758100650040C914497716247010000909010711423400A2050EC468B81C4733A"
        text = "  1741 bst"
        number = "+447917267410"
        datestr = "09/09/01 16:41:32"  # UTC

        ret = self.pdu.decode_pdu(pdu)

        self.assertEqual(ret['date'], datestr)
        self.assertEqual(ret['text'], text)
        self.assertEqual(ret['number'], number)

    def test_decoding_number_alpha1(self):  # Odd length test
        pdu = "07919471060040340409D0C6A733390400009060920173018093CC74595C96838C4F6772085AD6DDE4320B444E9741D4B03C6D7EC3E9E9B71B9474D3CB727799DEA286CFE5B9991DA6CBC3F432E85E9793CBA0F09A9EB6A7CB72BA0B9474D3CB727799DE72D6E9FABAFB0CBAA7E56490BA4CD7D34170F91BE4ACD3F575F7794E0F9F4161F1B92C2F8FD1EE32DD054AA2E520E3D3991C82A8E5701B"
        number = "FONIC"
        text = "Lieber FONIC Kunde, die Tarifoption Internet-Tagesflatrate wurde aktiviert. Internet-Nutzung wird jetzt pro Nutzungstag abgerechnet. Ihr FONIC Team"
        csca = "+491760000443"

        ret = self.pdu.decode_pdu(pdu)

        self.assertEqual(ret['csca'], csca)
        self.assertEqual(ret['number'], number)
        self.assertEqual(ret['text'], text)

    def test_decoding_number_alpha2(self):  # Even length test
        pdu = "07919333852804000412D0F7FBDD454FB75D693A0000903002801153402BCD301E9F0605D9E971191483C140412A35690D52832063D2F9040599A058EE05A3BD6430580E"
        number = "www.tim.it"
        text = 'Maxxi Alice 100 ATTIVATA FINO AL 19/04/2009'
        csca = '+393358824000'

        ret = self.pdu.decode_pdu(pdu)

        self.assertEqual(ret['csca'], csca)
        self.assertEqual(ret['number'], number)
        self.assertEqual(ret['text'], text)

    def test_decode_sms_confirmation(self):
        pdu = "07914306073011F006270B913426565711F7012081111345400120811174054043"
        csca = "+34607003110"
        datestr = "10/02/18 11:31:54"
        number = "SR-UNKNOWN"
        # XXX: the number should be +344626575117, is the prefix flipped ?
        text = "+43626575117|10/02/18 11:31:54|"

        ret = self.pdu.decode_pdu(pdu)

        self.assertEqual(ret['csca'], csca)
        self.assertEqual(ret['date'], datestr)
        self.assertEqual(ret['number'], number)
        self.assertEqual(ret['text'], text)

    def test_decode_weird_sms_confirmation(self):
        pdu = "07914306073011F001000B914306565711F9000007F0B2FC0DCABF01"
        csca = "+34607003110"
        number = "SR-UNKNOWN"

        ret = self.pdu.decode_pdu(pdu)

        self.assertEqual(ret['csca'], csca)
        self.assertEqual(ret['number'], number)

    def test_decode_weird_multipart_german_pdu(self):
        pdus = [
            "07919471227210244405852122F039F101506271217180A005000319020198E9B2B82C0759DFE4B0F9ED2EB7967537B9CC02B5D37450122D2FCB41EE303DFD7687D96537881A96A7CD6F383DFD7683F46134BBEC064DD36550DA0D22A7CBF3721BE42CD3F5A0198B56036DCA20B8FC0D6A0A4170767D0EAAE540433A082E7F83A6E5F93CFD76BB40D7B2DB0D9AA6CB2072BA3C2F83926EF31BE44E8FD17450BB8C9683CA",
            "07919471227210244405852122F039F1015062712181804F050003190202E4E8309B5E7683DAFC319A5E76B340F73D9A5D7683A6E93268FD9ED3CB6EF67B0E5AD172B19B2C2693C9602E90355D6683A6F0B007946E8382F5393BEC26BB00",
        ]
        texts = [
            u"Lieber Vodafone-Kunde, mit Ihrer nationalen Tarifoption zahlen Sie in diesem Netz 3,45 € pro MB plus 59 Ct pro Session. Wenn Sie diese Info nicht mehr e",
            u"rhalten möchten, wählen Sie kostenlos +4917212220. Viel Spaß im Ausland.",
        ]

        for pdu, text in zip(pdus, texts):
            ret = self.pdu.decode_pdu(pdu)
            self.assertEqual(ret['text'], text)

    def test_decoding_odd_length_pdu_strict_raises_valueerror(self):
        # same pdu as in test_decoding_number_alpha1 minus last char
        pdu = "07919471060040340409D0C6A733390400009060920173018093CC74595C96838C4F6772085AD6DDE4320B444E9741D4B03C6D7EC3E9E9B71B9474D3CB727799DEA286CFE5B9991DA6CBC3F432E85E9793CBA0F09A9EB6A7CB72BA0B9474D3CB727799DE72D6E9FABAFB0CBAA7E56490BA4CD7D34170F91BE4ACD3F575F7794E0F9F4161F1B92C2F8FD1EE32DD054AA2E520E3D3991C82A8E5701"
        self.assertRaises(ValueError, self.pdu.decode_pdu, pdu)

    def test_decoding_odd_length_pdu_no_strict(self):
        # same pdu as in test_decoding_number_alpha1 minus last char
        pdu = "07919471060040340409D0C6A733390400009060920173018093CC74595C96838C4F6772085AD6DDE4320B444E9741D4B03C6D7EC3E9E9B71B9474D3CB727799DEA286CFE5B9991DA6CBC3F432E85E9793CBA0F09A9EB6A7CB72BA0B9474D3CB727799DE72D6E9FABAFB0CBAA7E56490BA4CD7D34170F91BE4ACD3F575F7794E0F9F4161F1B92C2F8FD1EE32DD054AA2E520E3D3991C82A8E5701"
        ret = self.pdu.decode_pdu(pdu, strict=False)
        text = "Lieber FONIC Kunde, die Tarifoption Internet-Tagesflatrate wurde aktiviert. Internet-Nutzung wird jetzt pro Nutzungstag abgerechnet. Ihr FONIC Tea"
        self.assertEqual(ret['text'], text)
