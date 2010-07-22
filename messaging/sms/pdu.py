# see LICENSE


class Pdu(object):

    def __init__(self, pdu, len_smsc, cnt=1, seq=1):
        self.pdu = pdu.upper()
        self.length = len(pdu) / 2 - len_smsc
        self.cnt = cnt
        self.seq = seq
