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

    print mms.encode()


The above snippet binary encodes a MMS for '+34231342234' and subject 'Test
python-messaging.mms' with two slides. The first slide is just an static
image with some text, the second one has timing effects and will last 4.5s.

Encoding a m-notifyresp-ind PDU
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to send a m-notifyresp-ind, you will need to know the transaction
id of the MMS you want to acknowledge, once you have that you just need
to::

    mms = MMSMessage()
    mms.headers['Transaction-Id'] = 'T2132112322'
    mms.headers['Message-Type'] = 'm-notifyresp-ind'
    mms.headers['Status'] = 'Retrieved'

    print mms.encode()

And POST the resulting payload to the MMSC proxy using the above method
for sending a MMS.

Sending
~~~~~~~

In a WAP2.0 gateway, the binary message (payload) will be used as an argument
for a plain HTTP POST::

    from cStringIO import StringIO
    import socket

    host = "212.11.23.23"
    port = 7899

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
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

    print "RESPONSE", data


Decoding
========

Decoding a MMS could not be any easier, once you have the binary data of the
MMS, you just need to::

    from messaging.mms.message import MMSMessage

    # data is an array.array("B") instance
    mms = MMSMessage.from_data(data)

    print mms.headers['Message-Type']  # m-send-req
    print mms.headers['To']            # '+34231342234/TYPE=PLMN'
