# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from messaging.sms import SmsSubmit, SmsDeliver
from messaging.utils import (timedelta_to_relative_validity as to_relative,
                             datetime_to_absolute_validity as to_absolute,
                             FixedOffset)


class TestEncodingFunctions(unittest.TestCase):

    def test_converting_timedelta_to_validity(self):
        self.assertRaises(ValueError, to_relative, timedelta(minutes=4))
        self.assertRaises(ValueError, to_relative, timedelta(weeks=64))

        self.assertTrue(isinstance(to_relative(timedelta(hours=6)), int))
        self.assertTrue(isinstance(to_relative(timedelta(hours=18)), int))
        self.assertTrue(isinstance(to_relative(timedelta(days=15)), int))
        self.assertTrue(isinstance(to_relative(timedelta(weeks=31)), int))

        self.assertEqual(to_relative(timedelta(minutes=5)), 0)
        self.assertEqual(to_relative(timedelta(minutes=6)), 0)
        self.assertEqual(to_relative(timedelta(minutes=10)), 1)

        self.assertEqual(to_relative(timedelta(hours=12)), 143)
        self.assertEqual(to_relative(timedelta(hours=13)), 145)
        self.assertEqual(to_relative(timedelta(hours=24)), 167)

        self.assertEqual(to_relative(timedelta(days=2)), 168)
        self.assertEqual(to_relative(timedelta(days=30)), 196)

    def test_converting_datetime_to_validity(self):
        # http://www.dreamfabric.com/sms/scts.html
        # 12. Feb 1999 05:57:30 GMT+3
        when = datetime(1999, 2, 12, 5, 57, 30, 0,
                         FixedOffset(3 * 60, "GMT+3"))
        expected = [0x99, 0x20, 0x21, 0x50, 0x75, 0x03, 0x21]
        self.assertEqual(to_absolute(when, "GMT+3"), expected)

        when = datetime(1999, 2, 12, 5, 57, 30, 0)
        expected = [0x99, 0x20, 0x21, 0x50, 0x75, 0x03, 0x0]
        self.assertEqual(to_absolute(when, "UTC"), expected)

        when = datetime(1999, 2, 12, 5, 57, 30, 0,
                         FixedOffset(-3 * 60, "GMT-3"))
        expected = [0x99, 0x20, 0x21, 0x50, 0x75, 0x03, 0x29]
        self.assertEqual(to_absolute(when, "GMT-3"), expected)


class TestSmsSubmit(unittest.TestCase):

    def test_encoding_validity(self):
        # no validity
        number = '2b3334363136353835313139'.decode('hex')
        text = "hola"
        expected = "0001000B914316565811F9000004E8373B0C"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

        # absolute validity
        number = '2b3334363136353835313139'.decode('hex')
        text = "hola"
        expected = "0019000B914316565811F900000170520251930004E8373B0C"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.validity = datetime(2010, 7, 25, 20, 15, 39)

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

        # relative validity
        number = '2b3334363136353835313139'.decode('hex')
        text = "hola"
        expected = "0011000B914316565811F90000AA04E8373B0C"
        expected_len = 18

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.validity = timedelta(days=4)

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)
        self.assertEqual(pdu.length, expected_len)

    def test_encoding_csca(self):
        number = '2b3334363136353835313139'.decode('hex')
        text = "hola"
        csca = "+34646456456"
        expected = "07914346466554F601000B914316565811F9000004E8373B0C"
        expected_len = 17

        sms = SmsSubmit(number, text)
        sms.csca = csca
        sms.ref = 0x0

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)
        self.assertEqual(pdu.length, expected_len)
        self.assertEqual(pdu.cnt, 1)
        self.assertEqual(pdu.seq, 1)

    def test_encoding_class(self):
        number = '2b3334363534313233343536'.decode('hex')
        text = "hey yo"
        expected_0 = "0001000B914356143254F6001006E8721E947F03"
        expected_1 = "0001000B914356143254F6001106E8721E947F03"
        expected_2 = "0001000B914356143254F6001206E8721E947F03"
        expected_3 = "0001000B914356143254F6001306E8721E947F03"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.klass = 0

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected_0)

        sms.klass = 1
        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected_1)

        sms.klass = 2
        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected_2)

        sms.klass = 3
        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected_3)

    def test_encoding_request_status(self):
        # tested with pduspy.exe and http://www.rednaxela.net/pdu.php
        number = '2b3334363534313233343536'.decode('hex')
        text = "hey yo"
        expected = "0021000B914356143254F6000006E8721E947F03"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.request_status = True

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

    def test_encoding_message_with_latin1_chars(self):
        # tested with pduspy.exe
        number = '2b3334363534313233343536'.decode('hex')
        text = u"Hölä"
        expected = "0011000B914356143254F60000AA04483E7B0F"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.validity = timedelta(days=4)

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

        # tested with pduspy.exe
        number = '2b3334363534313233343536'.decode('hex')
        text = u"BÄRÇA äñ@"
        expected = "0001000B914356143254F6000009C2AD341104EDFB00"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

    def test_encoding_8bit_message(self):
        number = "01000000000"
        csca = "+44000000000"
        text = "Hi there..."
        expected = "07914400000000F001000B811000000000F000040B48692074686572652E2E2E"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.csca = csca
        sms.fmt = 0x04  # 8 bits

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

    def test_encoding_ucs2_message(self):
        number = '2b3334363136353835313139'.decode('hex')
        text = u'あ叶葉'
        csca = '+34646456456'
        expected = "07914346466554F601000B914316565811F9000806304253F68449"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.csca = csca

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

        text = u"Русский"
        number = '363535333435363738'.decode('hex')
        expected = "001100098156355476F80008AA0E0420044304410441043A04380439"

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.validity = timedelta(days=4)

        pdu = sms.to_pdu()[0]
        self.assertEqual(pdu.pdu, expected)

    def test_encoding_multipart_7bit(self):
        # text encoded with umts-tools
        text = "Or walk with Kings - nor lose the common touch, if neither foes nor loving friends can hurt you, If all men count with you, but none too much; If you can fill the unforgiving minute With sixty seconds' worth of distance run, Yours is the Earth and everything thats in it, And - which is more - you will be a Man, my son"
        number = '363535333435363738'.decode('hex')
        expected = [
            "005100098156355476F80000AAA00500038803019E72D03DCC5E83EE693A1AB44CBBCF73500BE47ECB41ECF7BC0CA2A3CBA0F1BBDD7EBB41F4777D8C6681D26690BB9CA6A3CB7290F95D9E83DC6F3988FDB6A7DD6790599E2EBBC973D038EC06A1EB723A28FFAEB340493328CC6683DA653768FCAEBBE9A07B9A8E06E5DF7516485CA783DC6F7719447FBF41EDFA18BD0325CDA0FCBB0E1A87DD",
            "005100098156355476F80000AAA005000388030240E6349B0DA2A3CBA0BADBFC969FD3F6B4FB0C6AA7DD757A19744DD3D1A0791A4FCF83E6E5F1DB4D9E9F40F7B79C8E06BDCD20727A4E0FBBC76590BCEE6681B2EFBA7C0E4ACF41747419540CCBE96850D84D0695ED65799E8E4EBBCF203A3A4C9F83D26E509ACE0205DD64500B7447A7C768507A0E6ABFE565500B947FD741F7349B0D129741",
            "005100098156355476F80000AA14050003880303C2A066D8CD02B5F3A0F9DB0D",
        ]

        sms = SmsSubmit(number, text)
        sms.ref = 0x0
        sms.rand_id = 136
        sms.validity = timedelta(days=4)

        ret = sms.to_pdu()
        cnt = len(ret)
        for i, pdu in enumerate(ret):
            self.assertEqual(pdu.pdu, expected[i])
            self.assertEqual(pdu.seq, i + 1)
            self.assertEqual(pdu.cnt, cnt)

    def test_encoding_bad_number_raises_error(self):
        self.assertRaises(ValueError, SmsSubmit, "032BADNUMBER", "text")

    def test_encoding_bad_csca_raises_error(self):
        sms = SmsSubmit("54342342", "text")
        self.assertRaises(ValueError, setattr, sms, 'csca', "1badcsca")


class TestSubmitPduCounts(unittest.TestCase):

    DEST = "+3530000000"
    GSM_CHAR = "x"
    EGSM_CHAR = u"€"
    UNICODE_CHAR = u"ő"

    def test_gsm_1(self):
        sms = SmsSubmit(self.DEST, self.GSM_CHAR * 160)
        self.assertEqual(len(sms.to_pdu()), 1)

    def test_gsm_2(self):
        sms = SmsSubmit(self.DEST, self.GSM_CHAR * 161)
        self.assertEqual(len(sms.to_pdu()), 2)

    def test_gsm_3(self):
        sms = SmsSubmit(self.DEST, self.GSM_CHAR * 153 * 2)
        self.assertEqual(len(sms.to_pdu()), 2)

    def test_gsm_4(self):
        sms = SmsSubmit(self.DEST,
                        self.GSM_CHAR * 153 * 2 + self.GSM_CHAR)
        self.assertEqual(len(sms.to_pdu()), 3)

    def test_gsm_5(self):
        sms = SmsSubmit(self.DEST, self.GSM_CHAR * 153 * 3)
        self.assertEqual(len(sms.to_pdu()), 3)

    def test_gsm_6(self):
        sms = SmsSubmit(self.DEST,
                        self.GSM_CHAR * 153 * 3 + self.GSM_CHAR)
        self.assertEqual(len(sms.to_pdu()), 4)

    def test_egsm_1(self):
        sms = SmsSubmit(self.DEST, self.EGSM_CHAR * 80)
        self.assertEqual(len(sms.to_pdu()), 1)

    def test_egsm_2(self):
        sms = SmsSubmit(self.DEST,
                        self.EGSM_CHAR * 79 + self.GSM_CHAR)
        self.assertEqual(len(sms.to_pdu()), 1)

    def test_egsm_3(self):
        sms = SmsSubmit(self.DEST, self.EGSM_CHAR * 153)  # 306 septets
        self.assertEqual(len(sms.to_pdu()), 3)

    def test_egsm_4(self):
        sms = SmsSubmit(self.DEST,
                          self.EGSM_CHAR * 229 + self.GSM_CHAR)  # 459 septets
        self.assertEqual(len(sms.to_pdu()), 4)

    def test_unicode_1(self):
        sms = SmsSubmit(self.DEST, self.UNICODE_CHAR * 70)
        self.assertEqual(len(sms.to_pdu()), 1)

    def test_unicode_2(self):
        sms = SmsSubmit(self.DEST, self.UNICODE_CHAR * 70 + self.GSM_CHAR)
        self.assertEqual(len(sms.to_pdu()), 2)

    def test_unicode_3(self):
        sms = SmsSubmit(self.DEST, self.UNICODE_CHAR * 67 * 2)
        self.assertEqual(len(sms.to_pdu()), 2)

    def test_unicode_4(self):
        sms = SmsSubmit(self.DEST, self.UNICODE_CHAR * 67 * 2 + self.GSM_CHAR)
        self.assertEqual(len(sms.to_pdu()), 3)

    def test_unicode_5(self):
        sms = SmsSubmit(self.DEST, self.UNICODE_CHAR * 67 * 3)
        self.assertEqual(len(sms.to_pdu()), 3)

    def test_unicode_6(self):
        sms = SmsSubmit(self.DEST, self.UNICODE_CHAR * 67 * 3 + self.GSM_CHAR)
        self.assertEqual(len(sms.to_pdu()), 4)


class TestSmsDeliver(unittest.TestCase):

    def test_decoding_7bit_pdu(self):
        pdu = "07911326040000F0040B911346610089F60000208062917314080CC8F71D14969741F977FD07"
        text = "How are you?"
        csca = "+31624000000"
        number = '2b3331363431363030393836'.decode('hex')

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.text, text)
        self.assertEqual(sms.csca, csca)
        self.assertEqual(sms.number, number)

    def test_decoding_ucs2_pdu(self):
        pdu = "07914306073011F0040B914316709807F2000880604290224080084E2D5174901A8BAF"
        text = u"中兴通讯"
        csca = "+34607003110"
        number = '2b3334363130373839373032'.decode('hex')

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.text, text)
        self.assertEqual(sms.csca, csca)
        self.assertEqual(sms.number, number)

    def test_decoding_7bit_pdu_data(self):
        pdu = "07911326040000F0040B911346610089F60000208062917314080CC8F71D14969741F977FD07"
        text = "How are you?"
        csca = "+31624000000"
        number = '2b3331363431363030393836'.decode('hex')

        data = SmsDeliver(pdu).data
        self.assertEqual(data['text'], text)
        self.assertEqual(data['csca'], csca)
        self.assertEqual(data['number'], number)
        self.assertEqual(data['pid'], 0)
        self.assertEqual(data['fmt'], 0)
        self.assertEqual(data['date'], datetime(2002, 8, 26, 19, 37, 41))

    def test_decoding_datetime_gmtplusone(self):
        pdu = "0791447758100650040C914497716247010000909010711423400A2050EC468B81C4733A"
        text = "  1741 bst"
        number = '2b343437393137323637343130'.decode('hex')
        date = datetime(2009, 9, 1, 16, 41, 32)

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.text, text)
        self.assertEqual(sms.number, number)
        self.assertEqual(sms.date, date)

    def test_decoding_datetime_gmtminusthree(self):
        pdu = "0791553001000001040491578800000190115101112979CF340B342F9FEBE536E83D0791C3E4F71C440E83E6F53068FE66A7C7697A781C7EBB4050F99BFE1EBFD96F1D48068BC16030182E66ABD560B41988FC06D1D3F03768FA66A7C7697A781C7E83CCEF34282C2ECBE96F50B90D8AC55EB0DC4B068BC140B1994E16D3D1622E"
        date = datetime(2010, 9, 11, 18, 10, 11)  # 11/09/10 15:10 GMT-3.00

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.date, date)

    def test_decoding_number_alphanumeric(self):
        # Odd length test
        pdu = "07919471060040340409D0C6A733390400009060920173018093CC74595C96838C4F6772085AD6DDE4320B444E9741D4B03C6D7EC3E9E9B71B9474D3CB727799DEA286CFE5B9991DA6CBC3F432E85E9793CBA0F09A9EB6A7CB72BA0B9474D3CB727799DE72D6E9FABAFB0CBAA7E56490BA4CD7D34170F91BE4ACD3F575F7794E0F9F4161F1B92C2F8FD1EE32DD054AA2E520E3D3991C82A8E5701B"
        number = "FONIC"
        text = "Lieber FONIC Kunde, die Tarifoption Internet-Tagesflatrate wurde aktiviert. Internet-Nutzung wird jetzt pro Nutzungstag abgerechnet. Ihr FONIC Team"
        csca = "+491760000443"

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.text, text)
        self.assertEqual(sms.csca, csca)
        self.assertEqual(sms.number, number)

        # Even length test
        pdu = "07919333852804000412D0F7FBDD454FB75D693A0000903002801153402BCD301E9F0605D9E971191483C140412A35690D52832063D2F9040599A058EE05A3BD6430580E"
        number = "www.tim.it"
        text = 'Maxxi Alice 100 ATTIVATA FINO AL 19/04/2009'
        csca = '+393358824000'

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.text, text)
        self.assertEqual(sms.csca, csca)
        self.assertEqual(sms.number, number)

    def test_decode_sms_confirmation(self):
        pdu = "07914306073011F006270B913426565711F7012081111345400120811174054043"
        csca = "+34607003110"
        date = datetime(2010, 2, 18, 11, 31, 54)
        number = "SR-UNKNOWN"
        # XXX: the number should be +344626575117, is the prefix flipped ?
        text = "+43626575117|10/02/18 11:31:54|"

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.text, text)
        self.assertEqual(sms.csca, csca)
        self.assertEqual(sms.number, number)
        self.assertEqual(sms.date, date)

    def test_decode_weird_multipart_german_pdu(self):
        pdus = [
            "07919471227210244405852122F039F101506271217180A005000319020198E9B2B82C0759DFE4B0F9ED2EB7967537B9CC02B5D37450122D2FCB41EE303DFD7687D96537881A96A7CD6F383DFD7683F46134BBEC064DD36550DA0D22A7CBF3721BE42CD3F5A0198B56036DCA20B8FC0D6A0A4170767D0EAAE540433A082E7F83A6E5F93CFD76BB40D7B2DB0D9AA6CB2072BA3C2F83926EF31BE44E8FD17450BB8C9683CA",
            "07919471227210244405852122F039F1015062712181804F050003190202E4E8309B5E7683DAFC319A5E76B340F73D9A5D7683A6E93268FD9ED3CB6EF67B0E5AD172B19B2C2693C9602E90355D6683A6F0B007946E8382F5393BEC26BB00",
        ]
        texts = [
            u"Lieber Vodafone-Kunde, mit Ihrer nationalen Tarifoption zahlen Sie in diesem Netz 3,45 € pro MB plus 59 Ct pro Session. Wenn Sie diese Info nicht mehr e",
            u"rhalten möchten, wählen Sie kostenlos +4917212220. Viel Spaß im Ausland.",
        ]

        for i, sms in enumerate(map(SmsDeliver, pdus)):
            self.assertEqual(sms.text, texts[i])
            self.assertEqual(sms.udh.concat.cnt, len(pdus))
            self.assertEqual(sms.udh.concat.seq, i + 1)
            self.assertEqual(sms.udh.concat.ref, 25)

    def test_decoding_odd_length_pdu_strict_raises_valueerror(self):
        # same pdu as in test_decoding_number_alpha1 minus last char
        pdu = "07919471060040340409D0C6A733390400009060920173018093CC74595C96838C4F6772085AD6DDE4320B444E9741D4B03C6D7EC3E9E9B71B9474D3CB727799DEA286CFE5B9991DA6CBC3F432E85E9793CBA0F09A9EB6A7CB72BA0B9474D3CB727799DE72D6E9FABAFB0CBAA7E56490BA4CD7D34170F91BE4ACD3F575F7794E0F9F4161F1B92C2F8FD1EE32DD054AA2E520E3D3991C82A8E5701"
        self.assertRaises(ValueError, SmsDeliver, pdu)

    def test_decoding_odd_length_pdu_no_strict(self):
        # same pdu as in test_decoding_number_alpha1 minus last char
        pdu = "07919471060040340409D0C6A733390400009060920173018093CC74595C96838C4F6772085AD6DDE4320B444E9741D4B03C6D7EC3E9E9B71B9474D3CB727799DEA286CFE5B9991DA6CBC3F432E85E9793CBA0F09A9EB6A7CB72BA0B9474D3CB727799DE72D6E9FABAFB0CBAA7E56490BA4CD7D34170F91BE4ACD3F575F7794E0F9F4161F1B92C2F8FD1EE32DD054AA2E520E3D3991C82A8E5701"
        text = "Lieber FONIC Kunde, die Tarifoption Internet-Tagesflatrate wurde aktiviert. Internet-Nutzung wird jetzt pro Nutzungstag abgerechnet. Ihr FONIC Tea"

        sms = SmsDeliver(pdu, strict=False)
        self.assertEqual(sms.text, text)

    def test_decoding_delivery_status_report(self):
        pdu = "0791538375000075061805810531F1019082416500400190824165004000"
        sr = {
            'status': 0,
            'scts': datetime(2010, 9, 28, 14, 56),
            'dt': datetime(2010, 9, 28, 14, 56),
            'recipient': '50131'
        }

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.csca, "+353857000057")
        data = sms.data
        self.assertEqual(data['ref'], 24)
        self.assertEqual(sms.sr, sr)

    def test_decoding_delivery_status_report_without_smsc_address(self):
        pdu = "00060505810531F1010150610000400101506100004000"
        sr = {
            'status': 0,
            'scts': datetime(2010, 10, 5, 16, 0),
            'dt': datetime(2010, 10, 5, 16, 0),
            'recipient': '50131'
        }

        sms = SmsDeliver(pdu)
        self.assertEqual(sms.csca, None)
        data = sms.data
        self.assertEqual(data['ref'], 5)
        self.assertEqual(sms.sr, sr)

# XXX: renable when support added
#    def test_decoding_submit_status_report(self):
#        # sent from SMSC to indicate submission failed or additional info
#        pdu = "07914306073011F001000B914306565711F9000007F0B2FC0DCABF01"
#        csca = "+34607003110"
#        number = "SR-UNKNOWN"
#
#        sms = SmsDeliver(pdu)
#        self.assertEqual(sms.csca, csca)
#        self.assertEqual(sms.number, number)
