# See LICENSE

from array import array

from messaging.mms.mms_pdu import MMSDecoder


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
