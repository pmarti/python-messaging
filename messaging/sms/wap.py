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

    wap_push, offset = data[1:3]
    assert wap_push == 0x06

    offset += 3
    data = data[offset:]

    # XXX: Not all WAP pushes are MMS
    return MMSDecoder().decode_data(data)


def is_mms_notification(push):
    # XXX: Pretty poor, but until we decode generic WAP pushes
    #      it will have to suffice. Ideally we would read the
    #      content-type from the WAP push header and test
    return (push.headers.get('From') is not None and
            push.headers.get('Content-Location') is not None)
