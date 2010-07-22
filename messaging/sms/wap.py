# See LICENSE

from array import array

from pywbxml import wbxml2xml, xml2wbxml

from messaging.utils import decode_str, encode_str
from messaging.mms.mms_pdu import MMSDecoder


def pdu2xml(pdu):
    return wbxml2xml(decode_str(pdu))


def xml2pdu(xml):
    return encode_str(xml2wbxml(xml)).upper()


def is_a_wap_push_notification(s):
    if not isinstance(s, str):
        raise TypeError("data must be an array.array serialised to string")

    data = array("B", s)

    try:
        return data[1] == 0x06
    except IndexError:
        return False


def extract_push_notification(s):
    data = array("B", s)

    trans_id, wap_push, offset = data[:3]
    assert wap_push == 0x06

    offset += 3
    data = data[offset:]
    return MMSDecoder().decode_data(data), trans_id
