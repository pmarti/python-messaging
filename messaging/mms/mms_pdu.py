# This library is free software.
#
# It was originally distributed under the terms of the GNU Lesser
# General Public License Version 2.
#
# python-messaging opts to apply the terms of the ordinary GNU
# General Public License v2, as permitted by section 3 of the LGPL
# v2.1. This re-licensing allows the entirety of python-messaging to
# be distributed according to the terms of GPL-2.
#
# See the COPYING file included in this archive
"""MMS Data Unit structure encoding and decoding classes"""

from __future__ import with_statement
import array
import os
import random

from messaging.utils import debug
from messaging.mms import message, wsp_pdu
from messaging.mms.iterator import PreviewIterator


def flatten_list(x):
    """Flattens ``x`` into a single list"""
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten_list(el))
        else:
            result.append(el)
    return result


mms_field_names = {
    0x01: ('Bcc', 'encoded_string_value'),
    0x02: ('Cc', 'encoded_string_value'),
    0x03: ('Content-Location', 'uri_value'),
    0x04: ('Content-Type', 'content_type_value'),
    0x05: ('Date', 'date_value'),
    0x06: ('Delivery-Report', 'boolean_value'),
    0x07: ('Delivery-Time', 'delivery_time_value'),
    0x08: ('Expiry', 'expiry_value'),
    0x09: ('From', 'from_value'),
    0x0a: ('Message-Class', 'message_class_value'),
    0x0b: ('Message-ID', 'text_string'),
    0x0c: ('Message-Type', 'message_type_value'),
    0x0d: ('MMS-Version', 'version_value'),
    0x0e: ('Message-Size', 'long_integer'),
    0x0f: ('Priority', 'priority_value'),
    0x10: ('Read-Reply', 'boolean_value'),
    0x11: ('Report-Allowed', 'boolean_value'),
    0x12: ('Response-Status', 'response_status_value'),
    0x13: ('Response-Text', 'encoded_string_value'),
    0x14: ('Sender-Visibility', 'sender_visibility_value'),
    0x15: ('Status', 'status_value'),
    0x16: ('Subject', 'encoded_string_value'),
    0x17: ('To', 'encoded_string_value'),
    0x18: ('Transaction-Id', 'text_string'),
}


class MMSDecoder(wsp_pdu.Decoder):
    """A decoder for MMS messages"""

    def __init__(self, filename=None):
        """
        :param filename: If specified, decode the content of the MMS
                         message file with this name
        :type filename: str
        """
        self._mms_data = array.array('B')
        self._mms_message = message.MMSMessage()
        self._parts = []

    def decode_file(self, filename):
        """
        Load the data contained in the specified ``filename``, and decode it.

        :param filename: The name of the MMS message file to open
        :type filename: str

        :raise OSError: The filename is invalid

        :return: The decoded MMS data
        :rtype: MMSMessage
        """
        num_bytes = os.stat(filename)[6]
        data = array.array('B')

        with open(filename, 'rb') as f:
            data.fromfile(f, num_bytes)

        return self.decode_data(data)

    def decode_data(self, data):
        """
        Decode the specified MMS message data

        :param data: The MMS message data to decode
        :type data: array.array('B')

        :return: The decoded MMS data
        :rtype: MMSMessage
        """
        self._mms_message = message.MMSMessage()
        self._mms_data = data
        body_iter = self.decode_message_header()
        self.decode_message_body(body_iter)
        return self._mms_message

    def decode_message_header(self):
        """
        Decodes the (full) MMS header data

        This must be called before :func:`_decodeBody`, as it sets
        certain internal variables relating to data lengths, etc.
        """
        data_iter = PreviewIterator(self._mms_data)

        # First 3  headers (in order
        ############################
        # - X-Mms-Message-Type
        # - X-Mms-Transaction-ID
        # - X-Mms-Version
        # TODO: reimplement strictness - currently we allow these 3 headers
        #       to be mixed with any of the other headers (this allows the
        #       decoding of "broken" MMSs, but is technically incorrect)

        # Misc headers
        ##############
        # The next few headers will not be in a specific order, except for
        # "Content-Type", which should be the last header
        # According to [4], MMS header field names will be short integers
        content_type_found = False
        header = ''
        while content_type_found == False:
            try:
                header, value = self.decode_header(data_iter)
            except StopIteration:
                break

            if header == mms_field_names[0x04][0]:
                content_type_found = True
            else:
                self._mms_message.headers[header] = value

        if header == 'Content-Type':
            # Otherwise it might break Content-Location
            # content_type, params = value
            self._mms_message.headers[header] = value

        return data_iter

    def decode_message_body(self, data_iter):
        """
        Decodes the MMS message body

        :param data_iter: an iterator over the sequence of bytes of the MMS
                          body
        :type data_iter: iter
        """
        ######### MMS body: headers ###########
        # Get the number of data parts in the MMS body
        try:
            num_entries = self.decode_uint_var(data_iter)
        except StopIteration:
            return

        #print 'Number of data entries (parts) in MMS body:', num_entries

        ########## MMS body: entries ##########
        # For every data "part", we have to read the following sequence:
        # <length of content-type + other possible headers>,
        # <length of data>,
        # <content-type + other possible headers>,
        # <data>
        for part_num in xrange(num_entries):
            #print '\nPart %d:\n------' % part_num
            headers_len = self.decode_uint_var(data_iter)
            data_len = self.decode_uint_var(data_iter)

            # Prepare to read content-type + other possible headers
            ct_field_bytes = []
            for i in xrange(headers_len):
                ct_field_bytes.append(data_iter.next())

            ct_iter = PreviewIterator(ct_field_bytes)
            # Get content type
            ctype, ct_parameters = self.decode_content_type_value(ct_iter)
            headers = {'Content-Type': (ctype, ct_parameters)}

            # Now read other possible headers until <headers_len> bytes
            # have been read
            while True:
                try:
                    hdr, value = self.decode_header(ct_iter)
                    headers[hdr] = value
                except StopIteration:
                    break

            # Data (note: this is not null-terminated)
            data = array.array('B')
            for i in xrange(data_len):
                data.append(data_iter.next())

            part = message.DataPart()
            part.set_data(data, ctype)
            part.content_type_parameters = ct_parameters
            part.headers = headers
            self._mms_message.add_data_part(part)

    @staticmethod
    def decode_header(byte_iter):
        """
        Decodes a header entry from an MMS message

        starting at the byte pointed to by :func:`byte_iter.next`

        From [4], section 7.1::

            Header = MMS-header | Application-header

        The return type of the "header value" depends on the header
        itself; it is thus up to the function calling this to determine
        what that type is (or at least compensate for possibly
        different return value types).

        :raise DecodeError: This uses :func:`decode_mms_header` and
                            :func:`decode_application_header`, and will raise this
                            exception under the same circumstances as
                            :func:`decode_application_header`. ``byte_iter`` will
                            not be modified in this case.

        :return: The decoded header entry from the MMS, in the format:
                 (<str:header name>, <str/int/float:header value>)
        :rtype: tuple
        """
        try:
            return MMSDecoder.decode_mms_header(byte_iter)
        except wsp_pdu.DecodeError:
            return wsp_pdu.Decoder.decode_header(byte_iter)

    @staticmethod
    def decode_mms_header(byte_iter):
        """
        Decodes the MMS header pointed by ``byte_iter``

        This method takes into account the assigned number values for MMS
        field names, as specified in [4], section 7.3, table 8.

        From [4], section 7.1::

            MMS-header = MMS-field-name MMS-value
            MMS-field-name = Short-integer
            MMS-value = Bcc-value | Cc-value | Content-location-value | Content-type-value | etc


        :raise wsp_pdu.DecodeError: The MMS field name could not be parsed.
                                    ``byte_iter`` will not be modified.

        :return: The decoded MMS header, in the format:
                 (<str:MMS-field-name>, <str:MMS-value>)
        :rtype: tuple
        """
        # Get the MMS-field-name
        mms_field_name = ''
        preview = byte_iter.preview()
        byte = wsp_pdu.Decoder.decode_short_integer_from_byte(preview)

        if byte in mms_field_names:
            byte_iter.next()
            mms_field_name = mms_field_names[byte][0]
        else:
            byte_iter.reset_preview()
            raise wsp_pdu.DecodeError('Invalid MMS Header: could '
                                      'not decode MMS field name')

        # Now get the MMS-value
        mms_value = ''
        try:
            name = mms_field_names[byte][1]
            mms_value = getattr(MMSDecoder, 'decode_%s' % name)(byte_iter)
        except wsp_pdu.DecodeError, msg:
            raise wsp_pdu.DecodeError('Invalid MMS Header: Could '
                                      'not decode MMS-value: %s' % msg)
        except:
            raise RuntimeError('A fatal error occurred, probably due to an '
                               'unimplemented decoding operation. Tried to '
                               'decode header: %s' % mms_field_name)

        return mms_field_name, mms_value

    @staticmethod
    def decode_encoded_string_value(byte_iter):
        """
        Decodes the encoded string value pointed by ``byte_iter``

        From [4], section 7.2.9::

            Encoded-string-value = Text-string | Value-length Char-set Text-string

        The Char-set values are registered by IANA as MIBEnum value.

        This function is not fully implemented, in that it does not
        have proper support for the Char-set values; it basically just
        reads over that sequence of bytes, and ignores it (see code for
        details) - any help with this will be greatly appreciated.

        :return: The decoded text string
        :rtype: str
        """
        try:
            # First try "Value-length Char-set Text-string"
            value_length = wsp_pdu.Decoder.decode_value_length(byte_iter)
            # TODO: add proper support for charsets...
            try:
                charset = wsp_pdu.Decoder.decode_well_known_charset(byte_iter)
            except wsp_pdu.DecodeError, msg:
                raise Exception('encoded_string_value decoding error - '
                                'Could not decode Charset value: %s' % msg)

            return wsp_pdu.Decoder.decode_text_string(byte_iter)
        except wsp_pdu.DecodeError:
            # Fall back on just "Text-string"
            return wsp_pdu.Decoder.decode_text_string(byte_iter)

    @staticmethod
    def decode_boolean_value(byte_iter):
        """
        Decodes the boolean value pointed by ``byte_iter``

        From [4], section 7.2.6::

           Delivery-report-value = Yes | No
           Yes = <Octet 128>
           No = <Octet 129>

        A lot of other yes/no fields use this encoding (read-reply,
        report-allowed, etc)

        :raise wsp_pdu.DecodeError: The boolean value could not be parsed.
                                    ``byte_iter`` will not be modified.

        :return: The value for the field
        :rtype: bool
        """
        byte = byte_iter.preview()
        if byte not in (128, 129):
            byte_iter.reset_preview()
            raise wsp_pdu.DecodeError('Error parsing boolean value '
                                      'for byte: %s' % hex(byte))
        byte = byte_iter.next()
        return byte == 128

    @staticmethod
    def decode_delivery_time_value(byte_iter):
        value_length = wsp_pdu.Decoder.decode_value_length(byte_iter)
        token = byte_iter.next()
        value = wsp_pdu.Decoder.decode_long_integer(byte_iter)
        if token == 128:
            token_type = 'absolute'
        elif token == 129:
            token_type = 'relative'
        else:
            raise wsp_pdu.DecodeError('Delivery-Time type token value is undefined'
                ' (%s), should be either 128 or 129' % token)
        return (token_type, value)

    @staticmethod
    def decode_from_value(byte_iter):
        """
        Decodes the "From" value pointed by ``byte_iter``

        From [4], section 7.2.11::

            From-value = Value-length (Address-present-token Encoded-string-value | Insert-address-token )
            Address-present-token = <Octet 128>
            Insert-address-token = <Octet 129>

        :return: The "From" address value
        :rtype: str
        """
        value_length = wsp_pdu.Decoder.decode_value_length(byte_iter)
        # See what token we have
        byte = byte_iter.next()
        if byte == 129:  # Insert-address-token
            return '<not inserted>'

        return MMSDecoder.decode_encoded_string_value(byte_iter)

    @staticmethod
    def decode_message_class_value(byte_iter):
        """
        Decodes the "Message-Class" value pointed by ``byte_iter``

        From [4], section 7.2.12::

            Message-class-value = Class-identifier | Token-text
            Class-identifier = Personal | Advertisement | Informational | Auto
            Personal = <Octet 128>
            Advertisement = <Octet 129>
            Informational = <Octet 130>
            Auto = <Octet 131>

        The token-text is an extension method to the message class.

        :return: The decoded message class
        :rtype: str
        """
        class_identifiers = {
            128: 'Personal',
            129: 'Advertisement',
            130: 'Informational',
            131: 'Auto',
        }
        byte = byte_iter.preview()
        if byte in class_identifiers:
            byte_iter.next()
            return class_identifiers[byte]

        byte_iter.reset_preview()
        return wsp_pdu.Decoder.decode_token_text(byte_iter)

    @staticmethod
    def decode_message_type_value(byte_iter):
        """
        Decodes the "Message-Type" value pointed by ``byte_iter``

        Defined in [4], section 7.2.14.

        :return: The decoded message type, or '<unknown>'
        :rtype: str
        """
        message_types = {
            0x80: 'm-send-req',
            0x81: 'm-send-conf',
            0x82: 'm-notification-ind',
            0x83: 'm-notifyresp-ind',
            0x84: 'm-retrieve-conf',
            0x85: 'm-acknowledge-ind',
            0x86: 'm-delivery-ind',
        }

        byte = byte_iter.preview()
        if byte in message_types:
            byte_iter.next()
            return message_types[byte]

        byte_iter.reset_preview()
        return '<unknown>'

    @staticmethod
    def decode_priority_value(byte_iter):
        """
        Decode the "Priority" value pointed by ``byte_iter``

        Defined in [4], section 7.2.17

        :raise wsp_pdu.DecodeError: The priority value could not be decoded;
                                    ``byte_iter`` is not modified in this case.

        :return: The decoded priority value
        :rtype: str
        """
        priorities = {128: 'Low', 129: 'Normal', 130: 'High'}

        byte = byte_iter.preview()
        if byte in priorities:
            byte = byte_iter.next()
            return priorities[byte]

        byte_iter.reset_preview()
        raise wsp_pdu.DecodeError('Error parsing Priority value '
                                  'for byte: %s' % byte)

    @staticmethod
    def decode_sender_visibility_value(byte_iter):
        """
        Decodes the sender visibility value pointed by ``byte_iter``

        Defined in [4], section 7.2.22::

           Sender-visibility-value = Hide | Show
           Hide = <Octet 128>
           Show = <Octet 129>

        :raise wsp_pdu.DecodeError: The sender visibility value could not be
                                    parsed. ``byte_iter`` will not be modified
                                    in this case.

        :return: The sender visibility: 'Hide' or 'Show'
        :rtype: str
        """
        byte = byte_iter.preview()
        if byte not in (128, 129):
            byte_iter.reset_preview()
            raise wsp_pdu.DecodeError('Error parsing sender visibility '
                                      'value for byte: %s' % hex(byte))

        byte = byte_iter.next()
        value = 'Hide' if byte == 128 else 'Show'
        return value

    @staticmethod
    def decode_response_status_value(byte_iter):
        """
        Decodes the "Response Status" value pointed by ``byte_iter``

        Defined in [4], section 7.2.20


        :raise wsp_pdu.DecodeError: The sender visibility value could not be
                                parsed. ``byte_iter`` will not be modified in
                                this case.

        :return: The decoded Response-status-value
        :rtype: str
        """
        response_status_values = {
            0x80: 'Ok',
            0x81: 'Error-unspecified',
            0x82: 'Error-service-denied',
            0x83: 'Error-message-format-corrupt',
            0x84: 'Error-sending-address-unresolved',
            0x85: 'Error-message-not-found',
            0x86: 'Error-network-problem',
            0x87: 'Error-content-not-accepted',
            0x88: 'Error-unsupported-message',
        }
        byte = byte_iter.preview()
        byte_iter.next()
        # Return error unspecified if it couldn't be decoded
        return response_status_values.get(byte, 0x81)

    @staticmethod
    def decode_status_value(byte_iter):
        """
        Used to decode the "Status" MMS header.

        Defined in [4], section 7.2.23

        :raise wsp_pdu.DecodeError: The sender visibility value could not be
                                    parsed. ``byte_iter`` will not be
                                    modified in this case.

        :return: The decoded Status-value
        :rtype: str
        """
        status_values = {
            0x80: 'Expired',
            0x81: 'Retrieved',
            0x82: 'Rejected',
            0x83: 'Deferred',
            0x84: 'Unrecognised',
        }

        byte = byte_iter.next()
        # Return an unrecognised state if it couldn't be decoded
        return status_values.get(byte, 0x84)

    @staticmethod
    def decode_expiry_value(byte_iter):
        """
        Used to decode the "Expiry" MMS header.

        From [4], section 7.2.10::

            Expiry-value = Value-length (Absolute-token Date-value | Relative-token Delta-seconds-value)
            Absolute-token = <Octet 128>
            Relative-token = <Octet 129>

        :raise wsp_pdu.DecodeError: The Expiry-value could not be decoded

        :return: The decoded Expiry-value, either as a date, or as a delta-seconds value
        :rtype: str or int
        """
        value_length = MMSDecoder.decode_value_length(byte_iter)
        token = byte_iter.next()

        if token == 0x80:    # Absolute-token
            return MMSDecoder.decode_date_value(byte_iter)
        elif token == 0x81:  # Relative-token
            return MMSDecoder.decode_delta_seconds_value(byte_iter)

        raise wsp_pdu.DecodeError('Unrecognized token value: %s' % hex(token))


class MMSEncoder(wsp_pdu.Encoder):
    """MMS Encoder"""

    def __init__(self):
        self._mms_message = message.MMSMessage()

    def encode(self, mms_message):
        """
        Encodes the specified MMS message ``mms_message``

        :param mms_message: The MMS message to encode
        :type mms_message: MMSMessage

        :return: The binary-encoded MMS data, as a sequence of bytes
        :rtype: array.array('B')
        """
        self._mms_message = mms_message
        msg_data = self.encode_message_header()
        msg_data.extend(self.encode_message_body())
        return msg_data

    def encode_message_header(self):
        """
        Binary-encodes the MMS header data.

        The encoding used for the MMS header is specified in [4].
        All "constant" encoded values found/used in this method
        are also defined in [4]. For a good example, see [2].

        :return: the MMS PDU header, as an array of bytes
        :rtype: array.array('B')
        """
        # See [4], chapter 8 for info on how to use these
        # from_types = {'Address-present-token': 0x80,
        #               'Insert-address-token': 0x81}

        # content_types = {'application/vnd.wap.multipart.related': 0xb3}

        # Create an array of 8-bit values
        message_header = array.array('B')

        headers_to_encode = self._mms_message.headers

        # If the user added any of these to the message manually
        # (X- prefix) use those instead
        for hdr in ('X-Mms-Message-Type', 'X-Mms-Transaction-Id',
                    'X-Mms-Version'):
            if hdr in headers_to_encode:
                if hdr == 'X-Mms-Version':
                    clean_header = 'MMS-Version'
                else:
                    clean_header = hdr.replace('X-Mms-', '', 1)

                headers_to_encode[clean_header] = headers_to_encode[hdr]
                del headers_to_encode[hdr]

         # First 3  headers (in order), according to [4]:
        ################################################
        # - X-Mms-Message-Type
        # - X-Mms-Transaction-ID
        # - X-Mms-Version

        ### Start of Message-Type verification
        if 'Message-Type' not in headers_to_encode:
            # Default to 'm-retrieve-conf'; we don't need a To/CC field for
            # this (see WAP-209, section 6.3, table 5)
            headers_to_encode['Message-Type'] = 'm-retrieve-conf'

        # See if the chosen message type is valid, given the message's
        # other headers. NOTE: we only distinguish between 'm-send-req'
        # (requires a destination number) and 'm-retrieve-conf'
        # (requires no destination number) - if "Message-Type" is
        # something else, we assume the message creator knows
        # what she is doing
        if headers_to_encode['Message-Type'] == 'm-send-req':
            found_dest_address = False
            for address_type in ('To', 'Cc', 'Bc'):
                if address_type in headers_to_encode:
                    found_dest_address = True
                    break

            if not found_dest_address:
                headers_to_encode['Message-Type'] = 'm-retrieve-conf'
        ### End of Message-Type verification

        ### Start of Transaction-Id verification
        if 'Transaction-Id' not in headers_to_encode:
            trans_id = str(random.randint(1000, 9999))
            headers_to_encode['Transaction-Id'] = trans_id
        ### End of Transaction-Id verification

        ### Start of MMS-Version verification
        if 'MMS-Version' not in headers_to_encode:
            headers_to_encode['MMS-Version'] = '1.0'

        # Encode the first three headers, in correct order
        for hdr in ('Message-Type', 'Transaction-Id', 'MMS-Version'):
            message_header.extend(
                MMSEncoder.encode_header(hdr, headers_to_encode[hdr]))
            del headers_to_encode[hdr]

        # Encode all remaining MMS message headers, except "Content-Type"
        # -- this needs to be added last, according [2] and [4]
        for hdr in headers_to_encode:
            if hdr != 'Content-Type':
                message_header.extend(
                    MMSEncoder.encode_header(hdr, headers_to_encode[hdr]))

        # Ok, now only "Content-type" should be left
        content_type, ct_parameters = headers_to_encode['Content-Type']
        message_header.extend(MMSEncoder.encode_mms_field_name('Content-Type'))
        ret = MMSEncoder.encode_content_type_value(content_type, ct_parameters)
        message_header.extend(flatten_list(ret))

        return message_header

    def encode_message_body(self):
        """
        Binary-encodes the MMS body data

        The MMS body's header should not be confused with the actual
        MMS header, as returned by :func:`encode_header`.

        The encoding used for the MMS body is specified in [5],
        section 8.5. It is only referenced in [4], however [2]
        provides a good example of how this ties in with the MMS
        header encoding.

        The MMS body is of type `application/vnd.wap.multipart` ``mixed``
        or ``related``. As such, its structure is divided into a header, and
        the data entries/parts::

            [ header ][ entries ]
            ^^^^^^^^^^^^^^^^^^^^^
                  MMS Body

        The MMS Body header consists of one entry[5]::

            name             type           purpose
            -------          -------        -----------
            num_entries      uint_var        num of entries in the multipart entity

        The MMS body's multipart entries structure::

            name             type                   purpose
            -------          -----                  -----------
            HeadersLen       uint_var                length of the ContentType and
                                                    Headers fields combined
            DataLen          uint_var                length of the Data field
            ContentType      Multiple octets        the content type of the data
            Headers          (<HeadersLen>
                              - length of
                             <ContentType>) octets  the part's headers
            Data             <DataLen> octets       the part's data

        :return: The binary-encoded MMS PDU body, as an array of bytes
        :rtype: array.array('B')
        """
        message_body = array.array('B')

        #TODO: enable encoding of MMSs without SMIL file
        ########## MMS body: header ##########
        # Parts: SMIL file + <number of data elements in each slide>
        num_entries = 1
        for page in self._mms_message._pages:
            num_entries += page.number_of_parts()

        for data_part in self._mms_message._data_parts:
            num_entries += 1

        message_body.extend(self.encode_uint_var(num_entries))

        ########## MMS body: entries ##########
        # For every data "part", we have to add the following sequence:
        # <length of content-type + other possible headers>,
        # <length of data>,
        # <content-type + other possible headers>,
        # <data>.

        # Gather the data parts, adding the MMS message's SMIL file
        smil_part = message.DataPart()
        smil = self._mms_message.smil()
        smil_part.set_data(smil, 'application/smil')
        #TODO: make this dynamic....
        smil_part.headers['Content-ID'] = '<0000>'
        parts = [smil_part]
        for slide in self._mms_message._pages:
            for part_tuple in (slide.image, slide.audio, slide.text):
                if part_tuple is not None:
                    parts.append(part_tuple[0])

        for part in parts:
            name, val_type = part.headers['Content-Type']
            part_content_type = self.encode_content_type_value(name, val_type)

            encoded_part_headers = []
            for hdr in part.headers:
                if hdr == 'Content-Type':
                    continue
                encoded_part_headers.extend(
                        wsp_pdu.Encoder.encode_header(hdr, part.headers[hdr]))

            # HeadersLen entry (length of the ContentType and
            #  Headers fields combined)
            headers_len = len(part_content_type) + len(encoded_part_headers)
            message_body.extend(self.encode_uint_var(headers_len))
            # DataLen entry (length of the Data field)
            message_body.extend(self.encode_uint_var(len(part)))
            # ContentType entry
            message_body.extend(part_content_type)
            # Headers
            message_body.extend(encoded_part_headers)
            # Data (note: we do not null-terminate this)
            for char in part.data:
                message_body.append(ord(char))

        return message_body

    @staticmethod
    def encode_header(header_field_name, header_value):
        """
        Encodes a header entry for an MMS message

        The return type of the "header value" depends on the header
        itself; it is thus up to the function calling this to determine
        what that type is (or at least compensate for possibly different
        return value types).

        From [4], section 7.1::

            Header = MMS-header | Application-header
            MMS-header = MMS-field-name MMS-value
            MMS-field-name = Short-integer
            MMS-value = Bcc-value | Cc-value | Content-location-value | Content-type-value | etc

        :raise DecodeError: This uses :func:`decode_mms_header` and
                            :func:`decode_application_header`, and will raise this
                            exception under the same circumstances as
                            :func:`decode_application_header`. ``byte_iter`` will
                            not be modified in this case.

        :return: The decoded header entry from the MMS, in the format:
                 (<str:header name>, <str/int/float:header value>)
        :rtype: tuple
        """
        encoded_header = []
        # First try encoding the header as a "MMS-header"...
        for assigned_number in mms_field_names:
            header = mms_field_names[assigned_number][0]
            if header == header_field_name:
                encoded_header.extend(
                    wsp_pdu.Encoder.encode_short_integer(assigned_number))
                # Now encode the value
                expected_type = mms_field_names[assigned_number][1]
                try:
                    ret = getattr(MMSEncoder,
                                  'encode_%s' % expected_type)(header_value)
                    encoded_header.extend(ret)
                except wsp_pdu.EncodeError, msg:
                    raise wsp_pdu.EncodeError('Error encoding parameter '
                                              'value: %s' % msg)
                except:
                    debug('A fatal error occurred, probably due to an '
                          'unimplemented encoding operation')
                    raise

                break

        # See if the "MMS-header" encoding worked
        if not len(encoded_header):
            # ...it didn't. Use "Application-header" encoding
            header_name = wsp_pdu.Encoder.encode_token_text(header_field_name)
            encoded_header.extend(header_name)
            # Now add the value
            encoded_header.extend(
                    wsp_pdu.Encoder.encode_text_string(header_value))

        return encoded_header

    @staticmethod
    def encode_mms_field_name(field_name):
        """
        Encodes an MMS header field name

        From [4], section 7.1::

            MMS-field-name = Short-integer

        :raise EncodeError: The specified header field name is not a
                            well-known MMS header.

        :param field_name: The header field name to encode
        :type field_name: str

        :return: The encoded header field name, as a sequence of bytes
        :rtype: list
        """
        encoded_mms_field_name = []

        for assigned_number in mms_field_names:
            if mms_field_names[assigned_number][0] == field_name:
                encoded_mms_field_name.extend(
                        wsp_pdu.Encoder.encode_short_integer(assigned_number))
                break

        if not len(encoded_mms_field_name):
            raise wsp_pdu.EncodeError('The specified header field name is not '
                                      'a well-known MMS header field name')

        return encoded_mms_field_name

    @staticmethod
    def encode_from_value(from_value=''):
        """
        Encodes the "From" address value

        From [4], section 7.2.11::

            From-value = Value-length (Address-present-token Encoded-string-value | Insert-address-token )
            Address-present-token = <Octet 128>
            Insert-address-token = <Octet 129>

        :param from_value: The "originator" of the MMS message. This may be an
                          empty string, in which case a token will be encoded
                          informing the MMSC to insert the address of the
                          device that sent this message (default).
        :type from_value: str

        :return: The encoded "From" address value, as a sequence of bytes
        :rtype: list
        """
        encoded_from_value = []
        if len(from_value) == 0:
            value_length = wsp_pdu.Encoder.encode_value_length(1)
            encoded_from_value.extend(value_length)
            encoded_from_value.append(129)  # Insert-address-token
        else:
            encoded_address = MMSEncoder.encode_encoded_string_value(from_value)
            # the "+1" is for the Address-present-token
            length = len(encoded_address) + 1
            value_length = wsp_pdu.Encoder.encode_value_length(length)
            encoded_from_value.extend(value_length)
            encoded_from_value.append(128)  # Address-present-token
            encoded_from_value.extend(encoded_address)

        return encoded_from_value

    @staticmethod
    def encode_encoded_string_value(string_value):
        """
        Encodes ``string_value``

        This is a simple wrapper to :func:`encode_text_string`

        From [4], section 7.2.9::

            Encoded-string-value = Text-string | Value-length Char-set Text-string

        The Char-set values are registered by IANA as MIBEnum value.

        :param string_value: The text string to encode
        :type string_value: str

        :return: The encoded string value, as a sequence of bytes
        :rtype: list
        """
        return wsp_pdu.Encoder.encode_text_string(string_value)

    @staticmethod
    def encode_message_type_value(message_type):
        """
        Encodes the Message-Type value ``message_type``

        Unknown message types are discarded; thus they will be encoded
        as 0x80 ("m-send-req") by this function

        Defined in [4], section 7.2.14.

        :param message_type: The MMS message type to encode
        :type message_type: str

        :return: The encoded message type, as a sequence of bytes
        :rtype: list
        """
        message_types = {
            'm-send-req': 0x80,
            'm-send-conf': 0x81,
            'm-notification-ind': 0x82,
            'm-notifyresp-ind': 0x83,
            'm-retrieve-conf': 0x84,
            'm-acknowledge-ind': 0x85,
            'm-delivery-ind': 0x86,
        }

        return [message_types.get(message_type, 0x80)]

    @staticmethod
    def encode_status_value(status_value):
        status_values = {
            'Expired': 0x80,
            'Retrieved': 0x81,
            'Rejected': 0x82,
            'Deferred': 0x83,
            'Unrecognised': 0x84,
        }

        # Return an unrecognised state if it couldn't be decoded
        return [status_values.get(status_value, 'Unrecognised')]
