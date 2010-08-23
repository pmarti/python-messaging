============
SMS tutorial
============

Features
++++++++

python-messaging contains in :mod:`messaging.sms` a full featured
:term:`SMS` encoder/decoder that should fulfill your needs. Some of
its features:

 - 7bit/8bit/16bit encoding/decoding: Decode messages from your Chinese
   friends, decode a :term:`WAP` PUSH notification or encode a UCS2
   message with a `Haiku`_ for your Japanese relatives.
 - Encode/decode `concatenated SMS`_
 - Set SMS validity: (relative, absolute)
 - Set SMS class: (0-3)
 - Encode/decode read reports
 - Decode alphanumeric senders
 - Pythonic API: We have strived to design an API that will make feel
   Pythonistas right at home!

.. _Haiku: http://en.wikipedia.org/wiki/Haiku
.. _concatenated SMS: http://en.wikipedia.org/wiki/Concatenated_SMS

Encoding
++++++++

Single part vs Multipart
~~~~~~~~~~~~~~~~~~~~~~~~

How to encode a single part SMS ready to be sent::

    from messaging.sms import SmsSubmit

    sms = SmsSubmit("+44123231231", "hey how's it going?")
    pdu = sms.to_pdu()[0]

    print pdu.length, pdu.pdu


How to encode a concatenated SMS ready to be sent::

    from messaging.sms import SmsSubmit

    sms = SmsSubmit("+44123231231", "hey " * 50)
    for pdu in sms.to_pdu():
        print pdu.length, pdu.pdu


Setting class
~~~~~~~~~~~~~

Setting the SMS class (0-3) is a no brainer::

    from messaging.sms import SmsSubmit

    sms = SmsSubmit("+44123231231", "hey how's it going?")
    sms.class = 0
    pdu = sms.to_pdu()[0]

    print pdu.length, pdu.pdu


Setting validity
~~~~~~~~~~~~~~~~

Validity can be either absolute, or relative. In order to provide
a pythonic API, we are using :class:`datetime.datetime` and
:class:`datetime.timedelta` objects respectively.

Setting absolute validity::

    from datetime import datetime
    from messaging.sms import SmsSubmit

    sms = SmsSubmit("+44123231231", "this SMS will auto-destroy in 4 months)
    sms.validity = datetime(2010, 12, 31, 23, 59, 59)
    pdu = sms.to_pdu()[0]

    print pdu.length, pdu.pdu


Setting relative validity::

    from datetime import timedelta
    from messaging.sms import SmsSubmit

    sms = SmsSubmit("+44123231231", "this SMS will auto-destroy in 5 hours")
    sms.validity = timedelta(hours=5)
    pdu = sms.to_pdu()[0]

    print pdu.length, pdu.pdu


Decoding
++++++++

term:`PDU` decoding is really simple with :class:`~messaging.sms.SmsDeliver`::

    from messaging.sms import SmsDeliver

    pdu = "0791447758100650040C914497726247010000909010711423400A2050EC468B81C4733A"
    sms = SmsDeliver(pdu)

    print sms.data
    # {'csca': '+447785016005', 'type': None,
    #  'date': datetime.datetime(2009, 9, 1, 16, 41, 32),
    #  'text': u'  1741 bst', 'fmt': 0, 'pid': 0,
    #  'dcs': 0, 'number': '+447927267410'}

Apart from the pdu, the :py:meth:`messaging.sms.SmsDeliver.__init__` accepts a
second parameter (`strict`, which defaults to True). If False, it will decode
incomplete (odd size) PDUs.

Sending
+++++++

This is how you would send a SMS with a modem or a 3G device on Linux, the
following code assumes that the device is already authenticated and
registered::

    import serial

    from messaging.sms import SmsSubmit

    def send_text(number, text, path='/dev/ttyUSB0'):
        # encode the SMS
        # note how I get the first returned element, this does
        # not deal with concatenated SMS.
        pdu = SmsSubmit(number, text).to_pdu()[0]
        # open the modem port (assumes Linux)
        ser = serial.Serial(path, timeout=1)
        # write the PDU length and wait 1 second till the
        # prompt appears (a more robust implementation
        # would wait till the prompt appeared)
        ser.write('AT+CMGS=%d\r' % pdu.length)
        print ser.readlines()
        # write the PDU and send a Ctrl+z escape
        ser.write('%s\x1a' % pdu.pdu)
        ser.close()

    send_text('655234567', 'hey how are you?')
