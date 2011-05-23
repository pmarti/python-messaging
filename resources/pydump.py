# Use this file to dump a python string into a format that wireshark's
# text2pcap can interpret and convert to a pcap that wireshark can read
#
# Suggested workflow:
#   edit 'data' string to contain the interesting data
#   python pydump.py > wsp.dmp
#   text2pcap -o hex -u9200,50 wsp.dmp wsp.pcap
#   wireshark wsp.pcap
#   export plain text format from wireshark

from struct import unpack

# generic WAP Push
data = '\x01\x06\x0b\x03\xae\x81\xea\xc3\x95\x8d\x01\xa2\xb4\x84\x03\x05j\n Vodafone\x00E\xc6\x0c\x03wap.meincallya.de/\x00\x08\x01\x03Zum kostenlosen Portal "Mein\x00\x83\x00\x03" - einfach auf den folgenden Link klicken oder die Seite direkt aufrufen. Ihr\x00\x83\x00\x03 Team\x00\x01\x01'

"""
No.     Time        Source                Destination           Protocol Info
      1 0.000000    1.1.1.1               2.2.2.2               WSP      WSP Push (0x06) (WBXML 1.3, Public ID: "-//WAPFORUM//DTD SI 1.0//EN (Service Indication 1.0)")

Frame 1: 218 bytes on wire (1744 bits), 218 bytes captured (1744 bits)
Ethernet II, Src: Private_01:01:01 (01:01:01:01:01:01), Dst: MS-NLB-PhysServer-02_02:02:02:02 (02:02:02:02:02:02)
Internet Protocol, Src: 1.1.1.1 (1.1.1.1), Dst: 2.2.2.2 (2.2.2.2)
User Datagram Protocol, Src Port: wap-wsp (9200), Dst Port: re-mail-ck (50)
Wireless Session Protocol, Method: Push (0x06), Content-Type: application/vnd.wap.sic
    Transaction ID: 0x01
    PDU Type: Push (0x06)
    Headers Length: 11
    Content-Type: application/vnd.wap.sic; charset=utf-8
        Charset: utf-8
    Headers
        Encoding-Version: 1.5
        Content-Length: 162
        Push-Flag:  (Last push message)
            .... ...0 = Initiator URI is authenticated: False (0)
            .... ..0. = Content is trusted: False (0)
            .... .1.. = Last push message: True (1)
WAP Binary XML, Version: 1.3, Public ID: "-//WAPFORUM//DTD SI 1.0//EN (Service Indication 1.0)"
    Version: 1.3 (0x03)
    Public Identifier (known): -//WAPFORUM//DTD SI 1.0//EN (Service Indication 1.0) (0x00000005)
    Character Set: utf-8 (0x0000006a)
    String table: 10 bytes
        Start  | Length | String
             0 |     10 | ' Vodafone'
    Data representation
        Level | State | Codepage | WBXML Token Description         | Rendering
            0 | Tag   | T   0    |   Known Tag 0x05           (.C) |  <si>
            1 | Tag   | T   0    |   Known Tag 0x06           (AC) |    <indication
            1 |  Attr | A   0    |   Known attrStart 0x0C          |      href='http://'
            1 |  Attr | A   0    | STR_I (Inline string)           |        'wap.meincallya.de/'
            1 |  Attr | A   0    |   Known attrStart 0x08          |      action='signal-high'
            1 | Tag   | T   0    | END (attribute list)            |    >
            1 | Tag   | T   0    | STR_I (Inline string)           |    'Zum kostenlosen Portal "Mein'
            1 | Tag   | T   0    | STR_T (Tableref string)         |    ' Vodafone'
            1 | Tag   | T   0    | STR_I (Inline string)           |    '" - einfach auf den folgenden Link klicken oder die Seite direkt aufrufen. Ihr'
            1 | Tag   | T   0    | STR_T (Tableref string)         |    ' Vodafone'
            1 | Tag   | T   0    | STR_I (Inline string)           |    ' Team'
            1 | Tag   | T   0    | END (Known Tag 0x06)            |    </indication>
            0 | Tag   | T   0    | END (Known Tag 0x05)            |  </si>
"""

# MMS WAP Push
data = '\x01\x06"application/vnd.wap.mms-message\x00\xaf\x84\x8c\x82\x98NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA\x00\x8d\x90\x89\x19\x80+447717275049/TYPE=PLMN\x00\x8a\x80\x8e\x02t\x00\x88\x05\x81\x03\x03\xf4\x7f\x83http://promms/servlets/NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA\x00'

"""
No.     Time        Source                Destination           Protocol Info
      1 0.000000    1.1.1.1               2.2.2.2               MMSE     MMS m-notification-ind

Frame 1: 224 bytes on wire (1792 bits), 224 bytes captured (1792 bits)
Ethernet II, Src: Private_01:01:01 (01:01:01:01:01:01), Dst: MS-NLB-PhysServer-02_02:02:02:02 (02:02:02:02:02:02)
Internet Protocol, Src: 1.1.1.1 (1.1.1.1), Dst: 2.2.2.2 (2.2.2.2)
User Datagram Protocol, Src Port: wap-wsp (9200), Dst Port: re-mail-ck (50)
Wireless Session Protocol, Method: Push (0x06), Content-Type: application/vnd.wap.mms-message
    Transaction ID: 0x01
    PDU Type: Push (0x06)
    Headers Length: 34
    Content-Type: application/vnd.wap.mms-message
    Headers
        X-Wap-Application-Id: x-wap-application:mms.ua
MMS Message Encapsulation, Type: m-notification-ind
    X-Mms-Message-Type: m-notification-ind (0x82)
    X-Mms-Transaction-ID: NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA
    X-Mms-MMS-Version: 1.0
    From: +447717275049/TYPE=PLMN
    X-Mms-Message-Class: Personal (0x80)
    X-Mms-Message-Size: 29696
    X-Mms-Expiry: 259199.000000000 seconds
    X-Mms-Content-Location: http://promms/servlets/NOK5A1ZdFTMYSG4O3VQAAsJv94GoNAAAAAAAA
"""

offset = 0
length = len(data)
perline = 8

while True:
    if offset >= length:
        break

    end = offset + perline
    if end > length:
        end = length
    line = data[offset:end]

    s = ''
    for c in line:
        s += " %02x" % unpack('B', c)

    # 000000 00 e0 1e a7 05 6f 00 10
    print "%06x%s" % (offset, s)

    offset += perline
