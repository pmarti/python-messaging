import sys


def bytes_to_str(b):
    if sys.version_info >= (3,):
        return b.decode('latin1')

    return b


def debug(s):
    # set this to True if you want to poke at PDU encoding/decoding
    if False:
        sys.stdout.write('%s\n' % s)


def swap(s):
    """Swaps ``address`` according to GSM 23.040"""
    address = list(encode_seq(s).replace('f', ''))
    for n in range(1, len(address), 2):
        address[n-1], address[n] = address[n], address[n-1]

    return ''.join(address).strip()


def encode_seq(seq):
    return ''.join(["%02x" % ord(n) for n in seq])


def encode_byte(i):
    return ''.join(["%02x" % ord(n) for n in chr(i)])
