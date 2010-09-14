============
MMS tutorial
============

Features
========

 * Full featured MMS encoder/decoder
 * Supports MMS 1.0-1.4
 * Supports presentation layout
 * Handles well known formats: JPEG, GIF, AMR, MIDI, 3GP, etc.
 * Tested with WAP 2.0 gateways


Encoding
========

How to encode a MMS::

    from messaging.mms.message import MMSMessage, MMSMessagePage

    mms = MMSMessage()
    mms.headers['To'] = '+34231342234/TYPE=PLMN'
    mms.headers['Message-Type'] = 'm-send-req'
    mms.headers['Subject'] = 'Test python-messaging.mms'

    slide1 = MMSMessagePage()
    slide1.add_image('image1.jpg')
    slide1.add_text('This is the first slide, with a static image and some text.')

    slide2 = MMSMessagePage()
    slide2.set_duration(4500)
    slide2.add_image('image2.jpg', 1500)
    slide2.add_text('This second slide has some timing effects.', 500, 3500)

    mms.add_page(slide1)
    mms.add_page(slide2)

    payload = mms.encode()


The above snippet binary encodes a MMS for '+34231342234' and subject 'Test
python-messaging.mms' with two slides. The first slide is just an static
image with some text, the second one has timing effects and will last 4.5s.

Sending a MMS
+++++++++++++

In a WAP2.0 gateway, the binary message (payload) will be used as an argument
for a plain HTTP POST::

    from cStringIO import StringIO
    import socket

    gw_host, gw_port = "212.11.23.23", 7899

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((gw_host, gw_port))
    s.send("POST %s HTTP/1.0\r\n" % mmsc)
    s.send("Content-Type: application/vnd.wap.mms-message\r\n")
    s.send("Content-Length: %d\r\n\r\n" % len(payload))

    s.sendall(payload)

    buf = StringIO()

    while True:
        data = s.recv(4096)
        if not data:
            break

        buf.write(data)

    s.close()
    data = buf.getvalue()
    buf.close()

    print "PROXY RESPONSE", data


Encoding a m-notifyresp-ind PDU
+++++++++++++++++++++++++++++++

In order to send a m-notifyresp-ind, you will need to know the transaction
id of the MMS you want to acknowledge, once you have that you just need
to::

    mms = MMSMessage()
    mms.headers['Transaction-Id'] = 'T2132112322'
    mms.headers['Message-Type'] = 'm-notifyresp-ind'
    mms.headers['Status'] = 'Retrieved'

    payload = mms.encode()

And POST the resulting payload to the :term:`MMSC` proxy using the very same
code used for sending a MMS.


Decoding
========

Decoding from binary data
+++++++++++++++++++++++++

Decoding a MMS could not be any easier, once you have the binary data of the
MMS, you just need to::

    from messaging.mms.message import MMSMessage

    # data is an array.array("B") instance
    mms = MMSMessage.from_data(data)

    print mms.headers['Message-Type']  # m-send-req
    print mms.headers['To']            # '+34231342234/TYPE=PLMN'


Decoding from a file
++++++++++++++++++++

Decoding a MMS serialised to a file is pretty straightforward too, you just
need the path to the file and::

    from messaging.mms.message import MMSMessage

    path = '/tmp/binary-mms.bin'
    mms = MMSMessage.from_file(path)

    print mms.headers['Message-Type']  # m-send-req
    print mms.headers['To']            # '+34231342234/TYPE=PLMN'


Obtaining a MMS from a WAP push notification
++++++++++++++++++++++++++++++++++++++++++++

A WAP push notification conveys all the necessary information to retrieve
the MMS from the MMSC. Once you have the different PDUs of the WAP push,
you need to decode it and obtain the `Content-Location` value of the
headers::

    from messaging.sms import SmsDeliver
    from messaging.sms.wap import extract_push_notification

    pdus = [
        "0791447758100650400E80885810000000810004016082415464408C0C08049F8E020105040B8423F00106226170706C69636174696F6E2F766E642E7761702E6D6D732D6D65737361676500AF848C82984E4F4B3543694B636F544D595347344D4253774141734B7631344655484141414141414141008D908919802B3434373738353334323734392F545950453D504C4D4E008A808E0274008805810301194083687474703A2F",
        "0791447758100650440E8088581000000081000401608241547440440C08049F8E020205040B8423F02F70726F6D6D732F736572766C6574732F4E4F4B3543694B636F544D595347344D4253774141734B763134465548414141414141414100",
    ]
    data = ""

    sms = SmsDeliver(pdus[0])
    data += sms.text

    sms = SmsDeliver(pdus[1])
    data += sms.text

    mms = extract_push_notification(data)
    url = mms.headers['Content-Location']
    print url


Once you have the content location, you need to do a HTTP GET to retrieve
the MMS payload::

    import socket
    from cStringIO import StringIO

    from messaging.mms.message import MMSMessage

    gw_host, gw_port = "212.11.23.23", 7899
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((gw_host, gw_port))
    s.send("GET %s HTTP/1.0\r\n\r\n" % url)

    buf = StringIO()

    while True:
        data = s.recv(4096)
        if not data:
            break

        buf.write(data)

    s.close()
    data = buf.getvalue()
    buf.close()

    mms = MMSMessage.from_data(data)
    print mms
