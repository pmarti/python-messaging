# -*- coding: utf-8 -*-
from array import array
import unittest

from messaging.sms import SmsDeliver
from messaging.sms.wap import (is_a_wap_push_notification as is_push,
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
        number = "88850100000018"
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
        self.assertEqual(mms.headers['Message-Type'], 'm-notification-ind')
        self.assertEqual(mms.headers['Transaction-Id'],
                'NOK5CiKcoTMYSG4MBSwAAsKv14FUHAAAAAAAA')
        self.assertEqual(mms.headers['MMS-Version'], '1.0')
        self.assertEqual(mms.headers['From'], '+447785342749/TYPE=PLMN')
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
        self.assertEqual(mms.headers['Message-Type'], 'm-notification-ind')
        self.assertEqual(mms.headers['Transaction-Id'],
                'NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA')
        self.assertEqual(mms.headers['MMS-Version'], '1.0')
        self.assertEqual(mms.headers['From'], '+447717275049/TYPE=PLMN')
        self.assertEqual(mms.headers['Message-Class'], 'Personal')
        self.assertEqual(mms.headers['Message-Size'], 29696)
        self.assertEqual(mms.headers['Expiry'], 259199)
        self.assertEqual(mms.headers['Content-Location'],
                'http://promms/servlets/NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA')
