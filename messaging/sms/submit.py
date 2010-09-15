# See LICENSE
"""Classes for sending SMS"""

from datetime import datetime, timedelta
import re

from messaging.sms import consts
from messaging.utils import (debug, encode_str, clean_number,
                             pack_8bits_to_ucs2, pack_8bits_to_7bits,
                             pack_8bits_to_8bit,
                             timedelta_to_relative_validity,
                             datetime_to_absolute_validity)
from messaging.sms.base import SmsBase
from messaging.sms.gsm0338 import is_gsm_text
from messaging.sms.pdu import Pdu

VALID_NUMBER = re.compile("^\+?\d{3,20}$")


class SmsSubmit(SmsBase):
    """I am a SMS ready to be sent"""

    def __init__(self, number, text):
        super(SmsSubmit, self).__init__()
        self._number = None
        self._csca = None
        self._klass = None
        self._validity = None
        self.request_status = False
        self.ref = None
        self.rand_id = None
        self.id_list = range(0, 255)
        self.msgvp = 0xaa
        self.pid = 0x00

        self.number = number
        self.text = text
        self.text_gsm = None

    def _set_number(self, number):
        if number and not VALID_NUMBER.match(number):
            raise ValueError("Invalid number format: %s" % number)

        self._number = number

    number = property(lambda self: self._number, _set_number)

    def _set_csca(self, csca):
        if csca and not VALID_NUMBER.match(csca):
            raise ValueError("Invalid csca format: %s" % csca)

        self._csca = csca

    csca = property(lambda self: self._csca, _set_csca)

    def _set_validity(self, validity):
        if validity is None or isinstance(validity, (timedelta, datetime)):
            # valid values are None, timedelta and datetime
            self._validity = validity
        else:
            raise TypeError("Don't know what to do with %s" % validity)

    validity = property(lambda self: self._validity, _set_validity)

    def _set_klass(self, klass):
        if not isinstance(klass, int):
            raise TypeError("_set_klass only accepts int objects")

        if klass not in [0, 1, 2, 3]:
            raise ValueError("class must be between 0 and 3")

        self._klass = klass

    klass = property(lambda self: self._klass, _set_klass)

    def to_pdu(self):
        """Returns a list of :class:`~messaging.pdu.Pdu` objects"""
        smsc_pdu = self._get_smsc_pdu()
        sms_submit_pdu = self._get_sms_submit_pdu()
        tpmessref_pdu = self._get_tpmessref_pdu()
        sms_phone_pdu = self._get_phone_pdu()
        tppid_pdu = self._get_tppid_pdu()
        sms_msg_pdu = self._get_msg_pdu()

        if len(sms_msg_pdu) == 1:
            pdu = smsc_pdu
            len_smsc = len(smsc_pdu) / 2
            pdu += sms_submit_pdu
            pdu += tpmessref_pdu
            pdu += sms_phone_pdu
            pdu += tppid_pdu
            pdu += sms_msg_pdu[0]
            debug("smsc_pdu: %s" % smsc_pdu)
            debug("sms_submit_pdu: %s" % sms_submit_pdu)
            debug("tpmessref_pdu: %s" % tpmessref_pdu)
            debug("sms_phone_pdu: %s" % sms_phone_pdu)
            debug("tppid_pdu: %s" % tppid_pdu)
            debug("sms_msg_pdu: %s" % sms_msg_pdu)
            debug("-" * 20)
            debug("full_pdu: %s" % pdu)
            debug("full_text: %s" % self.text)
            debug("-" * 20)
            return [Pdu(pdu, len_smsc)]

        # multipart SMS
        sms_submit_pdu = self._get_sms_submit_pdu(udh=True)
        pdu_list = []
        cnt = len(sms_msg_pdu)
        for i, sms_msg_pdu_item in enumerate(sms_msg_pdu):
            pdu = smsc_pdu
            len_smsc = len(smsc_pdu) / 2
            pdu += sms_submit_pdu
            pdu += tpmessref_pdu
            pdu += sms_phone_pdu
            pdu += tppid_pdu
            pdu += sms_msg_pdu_item
            debug("smsc_pdu: %s" % smsc_pdu)
            debug("sms_submit_pdu: %s" % sms_submit_pdu)
            debug("tpmessref_pdu: %s" % tpmessref_pdu)
            debug("sms_phone_pdu: %s" % sms_phone_pdu)
            debug("tppid_pdu: %s" % tppid_pdu)
            debug("sms_msg_pdu: %s" % sms_msg_pdu_item)
            debug("-" * 20)
            debug("full_pdu: %s" % pdu)
            debug("full_text: %s" % self.text)
            debug("-" * 20)

            pdu_list.append(Pdu(pdu, len_smsc, cnt=cnt, seq=i + 1))

        return pdu_list

    def _get_smsc_pdu(self):
        if not self.csca or not self.csca.strip():
            return "00"

        number = clean_number(self.csca)
        ptype = 0x81  # set to unknown number by default
        if number[0] == '+':
            number = number[1:]
            ptype = 0x91

        if len(number) % 2:
            number += 'F'

        ps = chr(ptype)
        for n in range(0, len(number), 2):
            num = number[n + 1] + number[n]
            ps += chr(int(num, 16))

        pl = len(ps)
        ps = chr(pl) + ps

        return encode_str(ps)

    def _get_tpmessref_pdu(self):
        if self.ref is None:
            self.ref = self._get_rand_id()

        self.ref &= 0xFF
        return encode_str(chr(self.ref))

    def _get_phone_pdu(self):
        number = clean_number(self.number)
        ptype = 0x81
        if number[0] == '+':
            number = number[1:]
            ptype = 0x91

        pl = len(number)
        if len(number) % 2:
            number += 'F'

        ps = chr(ptype)
        for n in range(0, len(number), 2):
            num = number[n + 1] + number[n]
            ps += chr(int(num, 16))

        ps = chr(pl) + ps
        return encode_str(ps)

    def _get_tppid_pdu(self):
        return encode_str(chr(self.pid))

    def _get_sms_submit_pdu(self, udh=False):
        sms_submit = 0x1
        if self.validity is None:
            # handle no validity
            pass
        elif isinstance(self.validity, datetime):
            # handle absolute validity
            sms_submit |= 0x18
        elif isinstance(self.validity, timedelta):
            # handle relative validity
            sms_submit |= 0x10

        if self.request_status:
            sms_submit |= 0x20

        if udh:
            sms_submit |= 0x40

        return encode_str(chr(sms_submit))

    def _get_msg_pdu(self):
        # Data coding scheme
        if self.fmt is None:
            if is_gsm_text(self.text):
                self.fmt = 0x00
            else:
                self.fmt = 0x08

        self.dcs = self.fmt

        if self.klass is not None:
            if self.klass == 0:
                self.dcs |= 0x10
            elif self.klass == 1:
                self.dcs |= 0x11
            elif self.klass == 2:
                self.dcs |= 0x12
            elif self.klass == 3:
                self.dcs |= 0x13

        dcs_pdu = encode_str(chr(self.dcs))

        # Validity period
        msgvp_pdu = ""
        if self.validity is None:
            # handle no validity
            pass

        elif isinstance(self.validity, timedelta):
            # handle relative
            msgvp = timedelta_to_relative_validity(self.validity)
            msgvp_pdu = encode_str(chr(msgvp))

        elif isinstance(self.validity, datetime):
            # handle absolute
            msgvp = datetime_to_absolute_validity(self.validity)
            msgvp_pdu = ''.join(map(encode_str, map(chr, msgvp)))

        # UDL + UD
        message_pdu = ""

        if self.fmt == 0x00:
            self.text_gsm = self.text.encode("gsm0338")
            if len(self.text_gsm) <= consts.SEVENBIT_SIZE:
                message_pdu = [pack_8bits_to_7bits(self.text_gsm)]
            else:
                message_pdu = self._split_sms_message(self.text_gsm)
        elif self.fmt == 0x04:
            if len(self.text) <= consts.EIGHTBIT_SIZE:
                message_pdu = [pack_8bits_to_8bit(self.text)]
            else:
                message_pdu = self._split_sms_message(self.text)
        elif self.fmt == 0x08:
            if len(self.text) <= consts.UCS2_SIZE:
                message_pdu = [pack_8bits_to_ucs2(self.text)]
            else:
                message_pdu = self._split_sms_message(self.text)
        else:
            raise ValueError("Unknown data coding scheme: %d" % self.fmt)

        ret = []
        for msg in message_pdu:
            ret.append(dcs_pdu + msgvp_pdu + msg)

        return ret

    def _split_sms_message(self, text):
        if self.fmt == 0x00:
            len_without_udh = consts.SEVENBIT_MP_SIZE
            limit = consts.SEVENBIT_SIZE
            packing_func = pack_8bits_to_7bits
            total_len = len(self.text_gsm)

        elif self.fmt == 0x04:
            len_without_udh = consts.EIGHTBIT_MP_SIZE
            limit = consts.EIGHTBIT_SIZE
            packing_func = pack_8bits_to_8bit
            total_len = len(self.text)

        elif self.fmt == 0x08:
            len_without_udh = consts.UCS2_MP_SIZE
            limit = consts.UCS2_SIZE
            packing_func = pack_8bits_to_ucs2
            total_len = len(self.text)

        msgs = []
        pi, pe = 0, len_without_udh

        while pi < total_len:
            if text[pi:pe][-1] == '\x1b':
                pe -= 1

            msgs.append(text[pi:pe])
            pi = pe
            pe += len_without_udh

        pdu_msgs = []

        udh_len = 0x05
        mid = 0x00
        data_len = 0x03

        sms_ref = self._get_rand_id() if self.rand_id is None else self.rand_id
        sms_ref &= 0xFF

        for i, msg in enumerate(msgs):
            i += 1
            total_parts = len(msgs)
            if limit == consts.SEVENBIT_SIZE:
                udh = (chr(udh_len) + chr(mid) + chr(data_len) +
                       chr(sms_ref) + chr(total_parts) + chr(i))
                padding = " "
            else:
                udh = (unichr(int("%04x" % ((udh_len << 8) | mid), 16)) +
                       unichr(int("%04x" % ((data_len << 8) | sms_ref), 16)) +
                       unichr(int("%04x" % ((total_parts << 8) | i), 16)))
                padding = ""

            pdu_msgs.append(packing_func(padding + msg, udh))

        return pdu_msgs

    def _get_rand_id(self):
        if not self.id_list:
            self.id_list = range(0, 255)

        return self.id_list.pop(0)
