import sys


def bytes_to_str(b):
    if sys.version_info >= (3,):
        return b.decode('latin1')

    return b


def to_bytes(s):
    if sys.version_info >= (3,):
        return bytes(s)

    return ''.join(map(unichr, s))


def debug(s):
    # set this to True if you want to poke at PDU encoding/decoding
    if False:
        sys.stdout.write('%s\n' % s)


def swap(s):
    """Swaps ``address`` according to GSM 23.040"""
    address = list(encode_str(s).replace('f', ''))
    for n in range(1, len(address), 2):
        address[n - 1], address[n] = address[n], address[n - 1]

    return ''.join(address).strip()


def clean_number(n):
    return n.strip().replace(' ', '')


def encode_str(s):
    """Returns the hexadecimal representation of ``s``"""
    return ''.join(["%02x" % ord(n) for n in s])


def encode_byte(i):
    """Returns the hexadecimal representation of ``i``"""
    return ''.join(["%02x" % ord(n) for n in chr(i)])
