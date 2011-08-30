# -*- coding: utf-8 -*-
from array import array
import unittest

from messaging.sms import SmsDeliver
from messaging.sms.wap import (is_a_wap_push_notification as is_push,
                               is_mms_notification,
                               extract_push_notification)


def list_to_str(l):
    a = array("B", l)
    return a.tostring()


class TestSmsWapPush(unittest.TestCase):

    data = [1, 6, 34, 97, 112, 112, 108, 105, 99, 97, 116, 105, 111,
        110, 47, 118, 110, 100, 46, 119, 97, 112, 46, 109, 109, 115, 45,
        109, 101, 115, 115, 97, 103, 101, 0, 175, 132, 140, 130, 152, 78,
        79, 75, 53, 67, 105, 75, 99, 111, 84, 77, 89, 83, 71, 52, 77, 66,
        83, 119, 65, 65, 115, 75, 118, 49, 52, 70, 85, 72, 65, 65, 65, 65,
        65, 65, 65, 65, 0, 141, 144, 137, 25, 128, 43, 52, 52, 55, 55, 56,
        53, 51, 52, 50, 55, 52, 57, 47, 84, 89, 80, 69, 61, 80, 76, 77, 78,
        0, 138, 128, 142, 2, 116, 0, 136, 5, 129, 3, 1, 25, 64, 131, 104,
        116, 116, 112, 58, 47, 47, 112, 114, 111, 109, 109, 115, 47, 115,
        101, 114, 118, 108, 101, 116, 115, 47, 78, 79, 75, 53, 67, 105, 75,
        99, 111, 84, 77, 89, 83, 71, 52, 77, 66, 83, 119, 65, 65, 115, 75,
        118, 49, 52, 70, 85, 72, 65, 65, 65, 65, 65, 65, 65, 65, 0]

    def test_is_a_wap_push_notification(self):
        self.assertTrue(is_push(list_to_str(self.data)))
        self.assertTrue(is_push(list_to_str([1, 6, 57, 92, 45])))
        self.assertFalse(is_push(list_to_str([4, 5, 57, 92, 45])))
        self.assertRaises(TypeError, is_push, 1)

    def test_decoding_m_notification_ind(self):
        pdus = [
            "0791447758100650400E80885810000000810004016082415464408C0C08049F8E020105040B8423F00106226170706C69636174696F6E2F766E642E7761702E6D6D732D6D65737361676500AF848C82984E4F4B3543694B636F544D595347344D4253774141734B7631344655484141414141414141008D908919802B3434373738353334323734392F545950453D504C4D4E008A808E0274008805810301194083687474703A2F",
            "0791447758100650440E8088581000000081000401608241547440440C08049F8E020205040B8423F02F70726F6D6D732F736572766C6574732F4E4F4B3543694B636F544D595347344D4253774141734B763134465548414141414141414100",
        ]
        number = '3838383530313030303030303138'.decode('hex')
        csca = "+447785016005"
        data = ""

        sms = SmsDeliver(pdus[0])
        self.assertEqual(sms.udh.concat.ref, 40846)
        self.assertEqual(sms.udh.concat.cnt, 2)
        self.assertEqual(sms.udh.concat.seq, 1)
        self.assertEqual(sms.number, number)
        self.assertEqual(sms.csca, csca)
        data += sms.text

        sms = SmsDeliver(pdus[1])
        self.assertEqual(sms.udh.concat.ref, 40846)
        self.assertEqual(sms.udh.concat.cnt, 2)
        self.assertEqual(sms.udh.concat.seq, 2)
        self.assertEqual(sms.number, number)
        data += sms.text

        mms = extract_push_notification(data)
        self.assertEqual(is_mms_notification(mms), True)

        self.assertEqual(mms.headers['Message-Type'], 'm-notification-ind')
        self.assertEqual(mms.headers['Transaction-Id'],
                'NOK5CiKcoTMYSG4MBSwAAsKv14FUHAAAAAAAA')
        self.assertEqual(mms.headers['MMS-Version'], '1.0')
        self.assertEqual(mms.headers['From'],
                '2b3434373738353334323734392f545950453d504c4d4e'.decode('hex'))
        self.assertEqual(mms.headers['Message-Class'], 'Personal')
        self.assertEqual(mms.headers['Message-Size'], 29696)
        self.assertEqual(mms.headers['Expiry'], 72000)
        self.assertEqual(mms.headers['Content-Location'],
                'http://promms/servlets/NOK5CiKcoTMYSG4MBSwAAsKv14FUHAAAAAAAA')

        pdus = [
            "0791447758100650400E80885810000000800004017002314303408C0C0804DFD3020105040B8423F00106226170706C69636174696F6E2F766E642E7761702E6D6D732D6D65737361676500AF848C82984E4F4B3541315A6446544D595347344F3356514141734A763934476F4E4141414141414141008D908919802B3434373731373237353034392F545950453D504C4D4E008A808E0274008805810303F47F83687474703A2F",
            "0791447758100650440E8088581000000080000401700231431340440C0804DFD3020205040B8423F02F70726F6D6D732F736572766C6574732F4E4F4B3541315A6446544D595347344F3356514141734A763934476F4E414141414141414100",
        ]

        number = "88850100000008"
        data = ""

        sms = SmsDeliver(pdus[0])
        self.assertEqual(sms.udh.concat.ref, 57299)
        self.assertEqual(sms.udh.concat.cnt, 2)
        self.assertEqual(sms.udh.concat.seq, 1)
        self.assertEqual(sms.number, number)
        data += sms.text

        sms = SmsDeliver(pdus[1])
        self.assertEqual(sms.udh.concat.ref, 57299)
        self.assertEqual(sms.udh.concat.cnt, 2)
        self.assertEqual(sms.udh.concat.seq, 2)
        self.assertEqual(sms.number, number)
        data += sms.text

        mms = extract_push_notification(data)
        self.assertEqual(is_mms_notification(mms), True)

        self.assertEqual(mms.headers['Message-Type'], 'm-notification-ind')
        self.assertEqual(mms.headers['Transaction-Id'],
                'NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA')
        self.assertEqual(mms.headers['MMS-Version'], '1.0')
        self.assertEqual(mms.headers['From'],
                '2b3434373731373237353034392f545950453d504c4d4e'.decode('hex'))
        self.assertEqual(mms.headers['Message-Class'], 'Personal')
        self.assertEqual(mms.headers['Message-Size'], 29696)
        self.assertEqual(mms.headers['Expiry'], 259199)
        self.assertEqual(mms.headers['Content-Location'],
                'http://promms/servlets/NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA')

    def test_decoding_generic_wap_push(self):
        pdus = [
            "0791947122725014440C8500947122921105F5112042519582408C0B05040B8423F0000396020101060B03AE81EAC3958D01A2B48403056A0A20566F6461666F6E650045C60C037761702E6D65696E63616C6C79612E64652F000801035A756D206B6F7374656E6C6F73656E20506F7274616C20224D65696E0083000322202D2065696E66616368206175662064656E20666F6C67656E64656E204C696E6B206B6C69636B656E",
            "0791947122725014440C8500947122921105F5112042519592403C0B05040B8423F00003960202206F6465722064696520536569746520646972656B7420617566727566656E2E2049687200830003205465616D000101",
        ]
        number = '303034393137323232393131'.decode('hex')
        csca = "+491722270541"
        data = ""

        sms = SmsDeliver(pdus[0])
        self.assertEqual(sms.udh.concat.ref, 150)
        self.assertEqual(sms.udh.concat.cnt, 2)
        self.assertEqual(sms.udh.concat.seq, 1)
        self.assertEqual(sms.number, number)
        self.assertEqual(sms.csca, csca)
        data += sms.text

        sms = SmsDeliver(pdus[1])
        self.assertEqual(sms.udh.concat.ref, 150)
        self.assertEqual(sms.udh.concat.cnt, 2)
        self.assertEqual(sms.udh.concat.seq, 2)
        self.assertEqual(sms.number, number)
        data += sms.text

        self.assertEqual(data, '\x01\x06\x0b\x03\xae\x81\xea\xc3\x95\x8d\x01\xa2\xb4\x84\x03\x05j\n Vodafone\x00E\xc6\x0c\x03wap.meincallya.de/\x00\x08\x01\x03Zum kostenlosen Portal "Mein\x00\x83\x00\x03" - einfach auf den folgenden Link klicken oder die Seite direkt aufrufen. Ihr\x00\x83\x00\x03 Team\x00\x01\x01')

        push = extract_push_notification(data)
        self.assertEqual(is_mms_notification(push), False)
