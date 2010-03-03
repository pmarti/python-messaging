# -*- coding: utf-8 -*-
# Copyright (C) 2004 Paul Hardwick paul@peck.org.uk
# Copyright (C) 2008 Warp Networks S.L.
# Copyright (C) 2008 Telefonica I+D
#
# Imported for the wader project on 5 June 2008 by Pablo Martí
# Imported for the mobile-manager on 1 Oct 2008 by Roberto Majadas
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

from cStringIO import StringIO
from binascii import hexlify, unhexlify
from datetime import datetime, timedelta
import random
random.seed()

from messaging import gsm0338

SEVENBIT_FORMAT = 0x00
EIGHTBIT_FORMAT = 0x04
UNICODE_FORMAT  = 0x08

SEVENBIT_SIZE = 160
UCS2_SIZE = 70
SEVENBIT_MP_SIZE = SEVENBIT_SIZE - 7
UCS2_MP_SIZE = UCS2_SIZE - 3

UNKNOWN_NUMBER = 129
INTERNATIONAL_NUMBER = 145

SMS_DELIVER = 0x00
SMS_SUBMIT = 0x01
SMS_CONCAT = 0x40
SMS_STATUS_REPORT = 0x03

UNKNOWN = 0
INTERNATIONAL = 1
NATIONAL = 2
NETWORK_SPECIFIC = 3
SUBSCRIBER = 4
ALPHANUMERIC = 5
ABBREVIATED = 6
RESERVED = 7


def debug(s):
    # set this to True if you want to poke at PDU encoding/decoding
    if False:
        print s


def swap(s):
    """Swaps ``address`` according to GSM 23.040"""
    address = list(hexlify(s).replace('f', ''))
    for n in range(1, len(address), 2):
        address[n-1], address[n] = address[n], address[n-1]

    return ''.join(address).strip()


class PDU(object):

    def __init__(self):
        self.id_list = range(0, 255)

    def encode_pdu(self, number, text, csca='', request_status=False,
                   msgref=None, msgvp=0xaa, store=False, rand_id=None):
        """
        Returns a list of messages in PDU format

        :param csca: The SMSC number
        :param request_status: Receive a confirmation SMS when readed
        :type request_status: bool
        :param msgref: SMS reference number, if None it'll be auto generated
        :type msgref: int or None
        :param msgvp: relative validity period as per ETSI
        :type msgvp: int
        :param store: Whether the SMS will be stored or not
        :type store: bool
        :param rand_id: Specify a random id to use in multipart SMS, only
                        use it for testing
        :type rand_id: int
        """
        smsc_pdu = self._get_smsc_pdu(csca)
        sms_submit_pdu = self._get_sms_submit_pdu(request_status, msgvp, store)
        tpmessref_pdu = self._get_tpmessref_pdu(msgref)
        sms_phone_pdu = self._get_phone_pdu(number)
        tppid_pdu = self._get_tppid_pdu()
        sms_msg_pdu = self._get_msg_pdu(text, msgvp, store, rand_id)

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
            debug("full_text: %s" % text)
            debug("-" * 20)
            return [((len(pdu) / 2) - len_smsc, pdu.upper())]

        # multipart SMS
        sms_submit_pdu = self._get_sms_submit_pdu(request_status, msgvp,
                                                  store, udh=True)
        pdu_list = []
        for sms_msg_pdu_item in sms_msg_pdu:
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
            debug("full_text: %s" % text)
            debug("-" * 20)
            pdu_list.append(((len(pdu) / 2) - len_smsc, pdu.upper()))

        return pdu_list

    def decode_pdu(self, pdu):
        """
        Decodes ``pdu`` and returns a dict with:

        sender
          SMS Sender. It can be either a number or string if
          it is an operator originated SMS.

        csca
          SMSC number

        date
          GSM format date string

        text
          The SMS text

        pid
          SMS PID

        type
          SMS type

        ref
          SMS reference number

        cnt
          Number of SMS in the sequence (concat msgs)

        seq
          Sequence number of the SMS (concat msgs)

        fmt
          Format of received SMS
        """
        pdu = pdu.upper()
        d = StringIO(unhexlify(pdu))
        # Service centre address
        smscl = ord(d.read(1))
        smscertype = ord(d.read(1))
        smscer = swap(d.read(smscl-1))
        if smscertype == INTERNATIONAL_NUMBER:
            smscer = '+' + smscer

        csca = smscer

        # 1 byte(octet) == 2 char
        # Message type TP-MTI bits 0,1
        # More messages to send/deliver bit 2
        # Status report request indicated bit 5
        # User Data Header Indicator bit 6
        # Reply path set bit 7
        # 1st octet position == smscerlen+4

        mtype = ord(d.read(1))
        if mtype & SMS_STATUS_REPORT:
            return self._decode_status_report_pdu(pdu, d, csca)

        # is this a SMS_DELIVER or SMS_SUBMIT type?
        sms_type = SMS_SUBMIT if mtype & SMS_SUBMIT else SMS_DELIVER

        # is this a concatenated msg?
        testheader = bool(mtype & SMS_CONCAT)

        if sms_type == SMS_SUBMIT:
            # skip the message reference
            d.read(1)

        sndlen = ord(d.read(1))
        if sndlen % 2:
            sndlen += 1

        sndtype = (ord(d.read(1)) >> 4) & 0x07 # bits 654
        if sndtype == ALPHANUMERIC:
            # coded according to 3GPP TS 23.038 [9] GSM 7-bit default alphabet
            sender = hexlify(d.read(int(sndlen/2.0)))
            sender = self._unpack_msg(sender)
            sender = sender.decode("gsm0338")
        else:
            # Extract phone number of sender
            sender = swap(d.read(int(sndlen/2.0)))
            if sndtype == INTERNATIONAL:
                sender = '+' + sender

        # 1 byte TP-PID (Protocol IDentifier)
        pid = d.read(1)
        # 1 byte TP-DCS (Data Coding Scheme)
        dcs = ord(d.read(1))
        fmt = SEVENBIT_FORMAT
        if dcs & (EIGHTBIT_FORMAT | UNICODE_FORMAT) == 0:
            fmt = SEVENBIT_FORMAT
        elif dcs & EIGHTBIT_FORMAT:
            fmt = EIGHTBIT_FORMAT
        elif dcs & UNICODE_FORMAT:
            fmt = UNICODE_FORMAT

        datestr = ''
        if sms_type == SMS_DELIVER:
            # Get date stamp (sender's local time)
            date = list(hexlify(d.read(6)))
            for n in range(1, len(date), 2):
                date[n-1], date[n] = date[n], date[n-1]

            # Get sender's offset from GMT (TS 23.040 TP-SCTS)
            lo_hi = ord(d.read(1))
            lo = lo_hi >> 4
            hi = lo_hi & 0xF

            loval = lo
            hival = (hi & 0x07) << 4
            direction = -1 if (hi & 0x08) else 1

            offset = (hival | loval) * 15 * direction

            #  02/08/26 19:37:41
            _datestr = "%s%s/%s%s/%s%s %s%s:%s%s:%s%s" % tuple(date)
            outputfmt = '%y/%m/%d %H:%M:%S'

            sndlocaltime = datetime.strptime(_datestr, outputfmt)
            sndoffset = timedelta(minutes=offset)
            gmttime = sndlocaltime - sndoffset

            datestr = gmttime.strftime(outputfmt)

        # Now get message body
        msgl = ord(d.read(1))
        msg = hexlify(d.read(msgl))
        # check for header
        cnt = seq = ref = headlen = 0

        if testheader:
            if msg[2:4] == "00": # found header for concat message
                headlen = (int(msg[0:2], 16) + 1) * 8
                # subheadlen = int(msg[4:6], 16)
                ref = int(msg[6:8], 16)
                cnt = int(msg[8:10], 16)
                seq = int(msg[10:12], 16)
                if fmt == SEVENBIT_FORMAT:
                    while headlen % 7:
                        headlen += 1
                    headlen /= 7

        if fmt == SEVENBIT_FORMAT:
            msg = self._unpack_msg(msg)[headlen:msgl]
            msg = msg.decode("gsm0338")

        elif fmt == EIGHTBIT_FORMAT:
            msg = ''.join([chr(int(msg[x:x+2], 16))
                            for x in range(0, len(msg), 2)])
            msg = unicode(msg[headlen:], 'latin-1')

        elif fmt == UNICODE_FORMAT:
            msg = u''.join([unichr(int(msg[x:x+4], 16))
                            for x in range(0, len(msg), 4)])

        return dict(number=sender, date=datestr, text=msg.strip(),
                    csca=csca, ref=ref, cnt=cnt, seq=seq, fmt=fmt,
                    type=sms_type, pid=pid)

    def _decode_status_report_pdu(self, pdu, d, csca):
        # XXX: We are not returning the pid here
        ref = ord(d.read(1))

        sndlen = ord(d.read(1))
        if sndlen % 2:
            sndlen += 1
        sndtype = ord(d.read(1))
        recipient = swap(d.read(int(sndlen/2.0)))
        if sndtype == INTERNATIONAL_NUMBER:
            recipient = '+%s' % recipient

        scts_str = ''
        date = list(hexlify(d.read(7)))
        for n in range(1, len(date), 2):
            date[n-1], date[n] = date[n], date[n-1]
            scts_str = "%s%s/%s%s/%s%s %s%s:%s%s:%s%s" % tuple(date[0:12])

        dt_str = ''
        date = list(hexlify(d.read(7)))
        for n in range(1, len(date), 2):
            date[n-1], date[n] = date[n], date[n-1]
            dt_str = "%s%s/%s%s/%s%s %s%s:%s%s:%s%s" % tuple(date[0:12])

        status = ord(d.read(1))
        msg = recipient + "|" + scts_str + "|" + dt_str
        sender = ""
        if status == 0x0:
            sender = "SR-OK"
        elif status == 0x1:
            sender = "SR-UNKNOWN"
            msg = recipient + "|" + scts_str + "|"
        elif status == 0x30:
            sender = "SR-STORED"
            msg = recipient + "|" + scts_str + "|"
        else:
            sender = "SR-UNKNOWN"
            msg = recipient + "|" + scts_str + "|"

        cnt = seq = 0
        return dict(number=sender, date=scts_str, text=msg.strip(),
                    csca=csca, ref=ref, cnt=cnt, seq=seq,
                    fmt=UNICODE_FORMAT, type=SMS_STATUS_REPORT)

    def _get_smsc_pdu(self, number):
        if not number.strip():
            return "00"

        number = self._clean_number(number)
        ptype = UNKNOWN_NUMBER
        if number[0] == '+':
            number = number[1:]
            ptype = INTERNATIONAL_NUMBER

        if len(number) % 2:
            number += 'F'

        ps = chr(ptype)
        for n in range(0, len(number), 2):
            num = number[n+1] + number[n]
            ps += chr(int(num, 16))

        pl = len(ps)
        ps = chr(pl) + ps

        return ''.join(["%02x" % ord(n) for n in ps])

    def _get_tpmessref_pdu(self, msgref):
        if msgref is None:
            msgref = self._get_rand_id()

        tpmessref = msgref & 0xFF
        return ''.join(["%02x" % ord(n) for n in chr(tpmessref)])

    def _get_phone_pdu(self, number):
        number = self._clean_number(number)
        ptype = UNKNOWN_NUMBER
        if number[0] == '+':
            number = number[1:]
            ptype = INTERNATIONAL_NUMBER

        pl = len(number)
        if len(number) % 2:
            number += 'F'

        ps = chr(ptype)
        for n in range(0, len(number), 2):
            num = number[n+1] + number[n]
            ps += chr(int(num, 16))

        ps = chr(pl) + ps

        return ''.join(["%02x" % ord(n) for n in ps])

    def _clean_number(self, number):
        return number.strip().replace(' ', '')

    def _get_tppid_pdu(self):
        tppid = 0x00
        return ''.join(["%02x" % ord(n) for n in chr(tppid)])

    def _get_sms_submit_pdu(self, request_status, msgvp, store, udh=False):
        sms_submit = 0x1
        if request_status:
            sms_submit |= 0x20
        if not store and msgvp != 0xFF:
            sms_submit |= 0x10

        if udh:
            sms_submit |= 0x40

        return ''.join(["%02x" % ord(n) for n in chr(sms_submit)])

    def _get_msg_pdu(self, text, validity_period, store, rand_id):
        # Data coding scheme
        if gsm0338.is_valid_gsm_text(text):
            text_format = SEVENBIT_FORMAT
        else:
            text_format = UNICODE_FORMAT

        dcs = 0x00 | text_format

        dcs_pdu = ''.join(["%02x" % ord(n) for n in chr(dcs)])

        # Validity period
        if not store:
            msgvp = validity_period & 0xFF
            msgvp_pdu = ''.join(["%02x" % ord(n) for n in chr(msgvp)])

        # UDL + UD
        message_pdu = ""

        if text_format == SEVENBIT_FORMAT:
            if len(text) <= SEVENBIT_SIZE:
                message_pdu = [self._pack_8bits_to_7bits(text)]
            else:
                message_pdu = self._split_sms_message(text,
                                                      limit=SEVENBIT_SIZE,
                                                      encoding=SEVENBIT_FORMAT,
                                                      rand_id=rand_id)
        else:
            if len(text) <= UCS2_SIZE:
                message_pdu = [self._pack_8bits_to_ucs2(text)]
            else:
                message_pdu = self._split_sms_message(text, limit=UCS2_SIZE,
                                                      encoding=UNICODE_FORMAT,
                                                      rand_id=rand_id)

        ret = []
        for msg in message_pdu:
            if store:
                ret.append(dcs_pdu + msg)
            else:
                ret.append(dcs_pdu + msgvp_pdu + msg)

        return ret

    def _pack_8bits_to_ucs2(self, message, udh=None):
        # XXX: This does not control the size respect to UDH
        text = message
        nmesg = ''

        if udh is not None:
            text = udh + text

        for n in text:
            nmesg += chr(ord(n) >> 8) + chr(ord(n) & 0xFF)

        mlen = len(text) * 2
        message = chr(mlen) + nmesg

        return ''.join(["%02x" % ord(n) for n in message])

    def _pack_8bits_to_7bits(self, message, udh=None):
        pdu = ""
        txt = message.encode("gsm0338")

        if udh is None:
            tl = len(txt)
            txt += '\x00'
            msgl = len(txt) * 7 / 8
            op = [-1] * msgl
            c = shift = 0

            for n in range(msgl):
                if shift == 6:
                    c += 1

                shift = n % 7
                lb = ord(txt[c]) >> shift
                hb = (ord(txt[c+1]) << (7-shift) & 255)
                op[n] = lb + hb
                c += 1

            pdu = chr(tl) + ''.join(map(chr, op))
        else:
            txt = "\x00\x00\x00\x00\x00\x00" + txt
            tl = len(txt)

            txt += '\x00'
            msgl = len(txt) * 7 / 8
            op = [-1] * msgl
            c = shift = 0

            for n in range(msgl):
                if shift == 6:
                    c += 1

                shift = n % 7
                lb = ord(txt[c]) >> shift
                hb = (ord(txt[c+1]) << (7-shift) & 255)
                op[n] = lb + hb
                c += 1

            for i, char in enumerate(udh):
                op[i] = ord(char)

            pdu = chr(tl) + ''.join(map(chr, op))

        return ''.join(["%02x" % ord(n) for n in pdu])

    def _split_sms_message(self, text, encoding=SEVENBIT_FORMAT,
                           limit=SEVENBIT_SIZE, rand_id=None):
        if limit == SEVENBIT_SIZE:
            len_without_udh = limit - 7
        else:
            len_without_udh = limit - 3

        msgs = []
        total_len = len(text)
        pi, pe = 0, len_without_udh

        while pi < total_len:
            msgs.append(text[pi:pe])
            pi = pe
            pe += len_without_udh

        packing_func = None
        if encoding == SEVENBIT_FORMAT:
            packing_func = self._pack_8bits_to_7bits
        else:
            packing_func = self._pack_8bits_to_ucs2

        pdu_msgs = []

        udh_len = 0x05
        mid = 0x00
        data_len = 0x03
        if rand_id is not None:
            csms_ref = rand_id
        else:
            csms_ref = self._get_rand_id()

        for i, msg in enumerate(msgs):
            i += 1
            total_parts = len(msgs)
            if limit == SEVENBIT_SIZE:
                udh = (chr(udh_len) + chr(mid) + chr(data_len) + chr(csms_ref) +
                       chr(total_parts) + chr(i))
                pdu_msgs.append(packing_func(" " + msg, udh))
            else:
                udh = (unichr(int("%04x" % ((udh_len << 8) | mid), 16)) +
                       unichr(int("%04x" % ((data_len << 8) | csms_ref), 16)) +
                       unichr(int("%04x" % ((total_parts << 8) | i ), 16))
                       )
                pdu_msgs.append(packing_func("" + msg, udh))

        return pdu_msgs

    def _unpack_msg(self, pdu, limit=SEVENBIT_SIZE):
        """
        Unpacks ``pdu`` into 7-bit characters and returns the decoded string
        """
        # Taken/modified from Dave Berkeley's pysms package
        count = last = 0
        result = []

        for i in range(0, len(pdu), 2):
            byte = int(pdu[i:i+2], 16)
            mask = 0x7F >> count
            out = ((byte & mask) << count) + last
            last = byte >> (7 - count)
            result.append(chr(out))

            if limit and len(result) >= limit:
                break

            if count == 6:
                result.append(chr(last))
                last = 0

            count = (count + 1) % 7

        return ''.join(result)

    def _get_rand_id(self):
        if not self.id_list:
            self.id_list = range(0, 255)

        return self.id_list.pop(0)
