# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 2.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net

""" WSP Data Unit structure encoding and decoding classes

Throughout the classes defined in this module, the following "primitive data
type" terminology applies, as specified in [5], section 8.1.1::

    Data Type     Definition
    bit           1 bit of data
    octet         8 bits of opaque data
    uint8         8-bit unsigned integer
    uint16        16-bit unsigned integer
    uint32        32-bit unsigned integer
    uintvar       variable length unsigned integer

This Encoder and Decoder classes provided in this module firstly provides
public methods for decoding and encoding each of these data primitives (where
needed).

Next, they provide methods encapsulating the basic WSP Header encoding rules
as defined in section 8.4.2.1 of [5].

Finally, the classes defined here provide methods for decoding/parsing
specific WSP header fields.

@author: Francois Aucamp C{<faucamp@csir.co.za>}
@license:  GNU Lesser General Public License, version 2
@note: This is part of the PyMMS library

@note: References used in the code and this document:
    5. Wap Forum/Open Mobile Alliance, "WAP-230 Wireless Session Protocol Specification"
    U{http://www.openmobilealliance.org/tech/affiliates/LicenseAgreement.asp?DocName=/wap/wap-230-wsp-20010705-a.pdf}
"""

import array
from datetime import datetime

from messaging.utils import debug
from messaging.mms.iterator import PreviewIterator


class WSPEncodingAssignments:
    """ Static class containing the constant values defined in [5] for
    well-known content types, parameter names, etc.

    It also defines some function for combining assigned number-tables for
    specific WSP encoding versions, where appropriate.

    This is used by both the Encoder and Decoder classes during well-known
    assigned number lookups (usually these functions have the string
    C{WellKnown} in their names).

        - Assigned parameters are stored in a dictionary,
          C{well_known_parameters}, containing all assigned values for WSP
          encoding versions 1.1 - 1.4, in the format:
          C{{<int>assigned number: (<str>name, <str>expected value type)}}
          A "encoding versioned"-version of this dictionary can be retrieved
          by calling the C{wellKnowParameters()} function with an appropriate
          WSP encoding version as parameter.
        - Assigned content types are stored in a list, C{wkContentTypes},
          in order; thus, their index in the list is equal to their
          assigned value.
    """
    wsp_pdu_types = {
        0x01: 'Connect',
        0x02: 'ConnectReply',
        0x03: 'Redirect',
        0x04: 'Reply',
        0x05: 'Disconnect',
        0x06: 'Push',
        0x07: 'ConfirmedPush',
        0x08: 'Suspend',
        0x09: 'Resume',
        0x40: 'Get',
        0x60: 'Post',
    }

    # Well-known parameter assignments ([5], table 38)
    well_known_parameters = {
        0x00: ('Q', 'QValue'),
        0x01: ('Charset', 'WellKnownCharset'),
        0x02: ('Level', 'VersionValue'),
        0x03: ('Type', 'IntegerValue'),
        0x05: ('Name', 'TextString'),
        0x06: ('Filename', 'TextString'),
        0x07: ('Differences', 'Field-name'),
        0x08: ('Padding', 'ShortInteger'),
        0x09: ('Type', 'ConstrainedEncoding'),  # encoding version 1.2
        0x0a: ('Start', 'TextString'),
        0x0b: ('Start-info', 'TextString'),
        0x0c: ('Comment', 'TextString'),   # encoding version 1.3
        0x0d: ('Domain', 'TextString'),
        0x0e: ('Max-Age', 'DeltaSecondsValue'),
        0x0f: ('Path', 'TextString'),
        0x10: ('Secure', 'NoValue'),
        0x11: ('SEC', 'ShortInteger'),  # encoding version 1.4
        0x12: ('MAC', 'TextValue'),
        0x13: ('Creation-date', 'DateValue'),
        0x14: ('Modification-date', 'DateValue'),
        0x15: ('Read-date', 'DateValue'),
        0x16: ('Size', 'IntegerValue'),
        0x17: ('Name', 'TextValue'),
        0x18: ('Filename', 'TextValue'),
        0x19: ('Start', 'TextValue'),
        0x1a: ('Start-info', 'TextValue'),
        0x1b: ('Comment', 'TextValue'),
        0x1c: ('Domain', 'TextValue'),
        0x1d: ('Path', 'TextValue'),
    }

    # Content type assignments ([5], table 40)
    wkContentTypes = [
        '*/*', 'text/*', 'text/html', 'text/plain',
        'text/x-hdml', 'text/x-ttml', 'text/x-vCalendar',
        'text/x-vCard', 'text/vnd.wap.wml',
        'text/vnd.wap.wmlscript', 'text/vnd.wap.wta-event',
        'multipart/*', 'multipart/mixed', 'multipart/form-data',
        'multipart/byterantes', 'multipart/alternative',
        'application/*', 'application/java-vm',
        'application/x-www-form-urlencoded',
        'application/x-hdmlc', 'application/vnd.wap.wmlc',
        'application/vnd.wap.wmlscriptc',
        'application/vnd.wap.wta-eventc',
        'application/vnd.wap.uaprof',
        'application/vnd.wap.wtls-ca-certificate',
        'application/vnd.wap.wtls-user-certificate',
        'application/x-x509-ca-cert',
        'application/x-x509-user-cert',
        'image/*', 'image/gif', 'image/jpeg', 'image/tiff',
        'image/png', 'image/vnd.wap.wbmp',
        'application/vnd.wap.multipart.*',
        'application/vnd.wap.multipart.mixed',
        'application/vnd.wap.multipart.form-data',
        'application/vnd.wap.multipart.byteranges',
        'application/vnd.wap.multipart.alternative',
        'application/xml', 'text/xml',
        'application/vnd.wap.wbxml',
        'application/x-x968-cross-cert',
        'application/x-x968-ca-cert',
        'application/x-x968-user-cert',
        'text/vnd.wap.si',
        'application/vnd.wap.sic',
        'text/vnd.wap.sl',
        'application/vnd.wap.slc',
        'text/vnd.wap.co',
        'application/vnd.wap.coc',
        'application/vnd.wap.multipart.related',
        'application/vnd.wap.sia',
        'text/vnd.wap.connectivity-xml',
        'application/vnd.wap.connectivity-wbxml',
        'application/pkcs7-mime',
        'application/vnd.wap.hashed-certificate',
        'application/vnd.wap.signed-certificate',
        'application/vnd.wap.cert-response',
        'application/xhtml+xml',
        'application/wml+xml',
        'text/css',
        'application/vnd.wap.mms-message',
        'application/vnd.wap.rollover-certificate',
        'application/vnd.wap.locc+wbxml',
        'application/vnd.wap.loc+xml',
        'application/vnd.syncml.dm+wbxml',
        'application/vnd.syncml.dm+xml',
        'application/vnd.syncml.notification',
        'application/vnd.wap.xhtml+xml',
        'application/vnd.wv.csp.cir',
        'application/vnd.oma.dd+xml',
        'application/vnd.oma.drm.message',
        'application/vnd.oma.drm.content',
        'application/vnd.oma.drm.rights+xml',
        'application/vnd.oma.drm.rights+wbxml',
    ]

    # Well-known character sets (table 42 of [5])
    # Format {<assinged_number> : <charset>}
    # Note that the assigned number is the same as the IANA MIBEnum value
    # "gsm-default-alphabet" is not included, as it is not assigned any
    # value in [5]. Also note, this is by no means a complete list
    wkCharSets = {
        0x07EA: 'big5',
        0x03E8: 'iso-10646-ucs-2',
        0x04: 'iso-8859-1',
        0x05: 'iso-8859-2',
        0x06: 'iso-8859-3',
        0x07: 'iso-8859-4',
        0x08: 'iso-8859-5',
        0x09: 'iso-8859-6',
        0x0A: 'iso-8859-7',
        0x0B: 'iso-8859-8',
        0x0C: 'iso-8859-9',
        0x11: 'shift_JIS',
        0x03: 'us-ascii',
        0x6A: 'utf-8',
    }

    # Header Field Name assignments ([5], table 39)
    hdrFieldNames = [
        'Accept', 'Accept-Charset', 'Accept-Encoding',
        'Accept-Language', 'Accept-Ranges', 'Age',
        'Allow', 'Authorization', 'Cache-Control',
        'Connection', 'Content-Base', 'Content-Encoding',
        'Content-Language', 'Content-Length',
        'Content-Location', 'Content-MD5', 'Content-Range',
        'Content-Type', 'Date', 'Etag', 'Expires', 'From',
        'Host', 'If-Modified-Since', 'If-Match',
        'If-None-Match', 'If-Range', 'If-Unmodified-Since',
        'Location', 'Last-Modified', 'Max-Forwards', 'Pragma',
        'Proxy-Authenticate', 'Proxy-Authorization', 'Public',
        'Range', 'Referer', 'Retry-After', 'Server',
        'Transfer-Encoding', 'Upgrade', 'User-Agent',
        'Vary', 'Via', 'Warning', 'WWW-Authenticate',
        'Content-Disposition',
        # encoding version 1.2
        'X-Wap-Application-Id', 'X-Wap-Content-URI',
        'X-Wap-Initiator-URI', 'Accept-Application',
        'Bearer-Indication', 'Push-Flag', 'Profile',
        'Profile-Diff', 'Profile-Warning',
        # encoding version 1.3
        'Expect', 'TE', 'Trailer', 'Accept-Charset',
        'Accept-Encoding', 'Cache-Control',
        'Content-Range', 'X-Wap-Tod', 'Content-ID',
        'Set-Cookie', 'Cookie', 'Encoding-Version',
        # encoding version 1.4
        'Profile-Warning', 'Content-Disposition',
        'X-WAP-Security', 'Cache-Control',
    ]

    # TODO: combine this dict with the hdrFieldNames table (same as well
    # known parameter assignments)
    # Temporary fix to allow different types of header field values to be
    # dynamically decoded
    hdrFieldEncodings = {'Accept': 'AcceptValue', 'Pragma': 'PragmaValue'}

    @staticmethod
    def wellKnownParameters(version='1.2'):
        """ Formats list of assigned values for well-known parameter names,
        for the specified WSP encoding version.

        @param version: The WSP encoding version to use. This defaults
                                to "1.2", but may be "1.1", "1.2", "1.3" or
                                "1.4" (see table 38 in [5] for details).
        @type version: str

        @raise ValueError: The specified encoding version is invalid.

        @return: A dictionary containing the well-known parameters with
                 assigned numbers for the specified encoding version (and
                 lower). Entries in this dict follow the format:
                 C{{<int:assigned_number> : (<str:param_name>, <str:expected_type>)}}
        @rtype: dict
        """
        if version not in ('1.1', '1.2', '1.3', '1.4'):
            raise ValueError('version must be "1.1",'
                             '"1.2", "1.3" or "1.4"')
        else:
            version = int(version.split('.')[1])

        versioned_params = dict(WSPEncodingAssignments.well_known_parameters)
        if version <= 3:
            for assigned_number in range(0x11, 0x1e):
                del versioned_params[assigned_number]

        if version <= 2:
            for assigned_number in range(0x0c, 0x11):
                del versioned_params[assigned_number]

        if version == 1:
            for assigned_number in range(0x09, 0x0c):
                del versioned_params[assigned_number]

        return versioned_params

    @staticmethod
    def header_field_names(version='1.2'):
        """ Formats list of assigned values for header field names, for the
        specified WSP encoding version.

        @param version: The WSP encoding version to use. This defaults
                                to "1.2", but may be "1.1", "1.2", "1.3" or
                                "1.4" (see table 39 in [5] for details).
        @type version: str

        @raise ValueError: The specified encoding version is invalid.

        @return: A list containing the WSP header field names with assigned
                 numbers for the specified encoding version (and lower).
        @rtype: list
        """
        if version not in ('1.1', '1.2', '1.3', '1.4'):
            raise ValueError('version must be "1.1",'
                             '"1.2", "1.3" or "1.4"')

        version = int(version.split('.')[1])

        versioned_field_names = list(WSPEncodingAssignments.hdrFieldNames)
        if version == 3:
            versioned_field_names = versioned_field_names[:0x44]
        elif version == 2:
            versioned_field_names = versioned_field_names[:0x38]
        elif version == 1:
            versioned_field_names = versioned_field_names[:0x2f]

        return versioned_field_names


class DecodeError(Exception):
    """ The decoding operation failed; most probably due to an invalid byte in
    the sequence provided for decoding """


class EncodeError(Exception):
    """ The encoding operation failed; most probably due to an invalid value
    provided for encoding """


class Decoder:
    """A WSP Data unit decoder"""

    @staticmethod
    def decodeUint8(byte_iter):
        """ Decodes an 8-bit unsigned integer from the byte pointed to by
        C{byte_iter.next()}

        @note: this function will move the iterator passed as C{byte_iter} one
               byte forward.

        @param byte_iter: an iterator over a sequence of bytes
        @type byte_iter: iter

        @return: the decoded 8-bit unsigned integer
        @rtype: int
        """
        # Make the byte unsigned
        return byte_iter.next() & 0xf

    @staticmethod
    def decodeUintvar(byte_iter):
        """ Decodes the variable-length unsigned integer starting at the
        byte pointed to by C{byte_iter.next()}

        See C{wsp.Encoder.encodeUintvar()} for a detailed description of the
        encoding scheme used for C{Uintvar} sequences.

        @note: this function will move the iterator passed as C{byte_iter} to
               the last octet in the uintvar sequence; thus, after calling
               this, that iterator's C{next()} function will return the first
               byte B{after}the uintvar sequence.

        @param byte_iter: an iterator over a sequence of bytes
        @type byte_iter: iter

        @return: the decoded unsigned integer
        @rtype: int
        """
        uint = 0
        byte = byte_iter.next()
        while (byte >> 7) == 0x01:
            uint = uint << 7
            uint |= byte & 0x7f
            byte = byte_iter.next()

        uint = uint << 7
        uint |= byte & 0x7f
        return uint

    @staticmethod
    def decodeShortInteger(byte_iter):
        """ Decodes the short-integer value starting at the byte pointed to
        by C{byte_iter.next()}.

        The encoding for a long integer is specified in [5], section 8.4.2.1:
        C{Short-integer = OCTET
        Integers in range 0-127 shall be encoded as a one octet value with
        the most significant bit set to one (1xxx xxxx) and with the value
        in the remaining least significant bits.}

        @raise DecodeError: Not a valid short-integer; the most significant
                            isn't set to 1.
                            C{byte_iter} will not be modified if this is raised

        @return: The decoded short integer
        @rtype: int
        """
        byte = byte_iter.preview()
        if not byte & 0x80:
            byte_iter.reset_preview()
            raise DecodeError('Not a valid short-integer: MSB not set')

        byte = byte_iter.next()
        return byte & 0x7f

    @staticmethod
    def decodeShortIntegerFromByte(byte):
        """
        Decodes the short-integer value contained in the specified byte value

        @param byte: the byte value to decode
        @type byte: int

        @raise DecodeError: Not a valid short-integer; the most significant
                            isn't set to 1.
        @return: The decoded short integer
        @rtype: int
        """
        if not byte & 0x80:
            raise DecodeError('Not a valid short-integer: MSB not set')

        return byte & 0x7f

    @staticmethod
    def decodeLongInteger(byte_iter):
        """ Decodes the long integer value starting at the byte pointed to
        by C{byte_iter.next()}.

        The encoding for a long integer is specified in [5], section 8.4.2.1,
        and follows the form::

         Long-integer = [Short-length] [Multi-octet-integer]
                            ^^^^^^     ^^^^^^^^^^^^^^^^^^^^^
                            1 byte     <Short-length> bytes

         The Short-length indicates the length of the Multi-octet-integer.

        @raise DecodeError: The byte pointed to by C{byte_iter.next()} does
                            not indicate the start of a valid long-integer
                            sequence (short-length is invalid). If this is
                            raised, the iterator passed as C{byte_iter} will
                            not be modified.

        @note: If this function returns successfully, it will move the
               iterator passed as C{byte_iter} to the last octet in the encoded
               long integer sequence; thus, after calling this, that
               iterator's C{next()} function will return the first byte
               B{after}the encoded long integer sequence.

        @param byte_iter: an iterator over a sequence of bytes
        @type byte_iter: iter

        @return: The decoded long integer
        @rtype: int
        """
        try:
            shortLength = Decoder.decodeShortLength(byte_iter)
        except DecodeError:
            raise DecodeError('short-length byte is invalid')

        longInt = 0
        # Decode the Multi-octect-integer
        for i in range(shortLength):
            longInt = longInt << 8
            longInt |= byte_iter.next()

        return longInt

    @staticmethod
    def decodeTextString(byte_iter):
        """ Decodes the null-terminated, binary-encoded string value starting
        at the byte pointed to by C{dataIter.next()}.

        This follows the basic encoding rules specified in [5], section
        8.4.2.1

        @note: this function will move the iterator passed as C{byte_iter} to
               the last octet in the encoded string sequence; thus, after
               calling this, that iterator's C{next()} function will return
               the first byte B{after}the encoded string sequence.

        @param byte_iter: an iterator over a sequence of bytes
        @type byte_iter: iter

        @return: The decoded text string
        @rtype: str
        """
        decodedString = ''
        byte = byte_iter.next()
        # Remove Quote character (octet 127), if present
        if byte == 127:
            byte = byte_iter.next()

        while byte != 0x00:
            decodedString += chr(byte)
            byte = byte_iter.next()

        return decodedString

    @staticmethod
    def decodeQuotedString(byte_iter):
        """ From [5], section 8.4.2.1:
        Quoted-string = <Octet 34> *TEXT End-of-string
        The TEXT encodes an RFC2616 Quoted-string with the enclosing
        quotation-marks <"> removed

        @return: The decoded text string
        @rtype: str
        """
        # look for the quote character
        byte = byte_iter.preview()
        if byte != 34:
            byte_iter.reset_preview()
            raise DecodeError('Invalid quoted string: must '
                              'start with <octect 34>')
        byte_iter.next()
        # CHECK: should the quotation chars be pre- and appended before
        # returning *technically* we should not check for quote characters.
        return Decoder.decodeTextString(byte_iter)

    @staticmethod
    def decodeTokenText(byte_iter):
        """ From [5], section 8.4.2.1:
        Token-text = Token End-of-string

        @raise DecodeError: invalid token; byte_iter is not modified

        @return: The token string if successful, otherwise the read byte
        @rtype: str or int
        """
        separators = (11, 32, 40, 41, 44, 47, 58, 59, 60, 61, 62, 63, 64, 91,
                      92, 93, 123, 125)
        token = ''
        byte = byte_iter.preview()
        if byte <= 31 or byte in separators:
            byte_iter.reset_preview()
            raise DecodeError('Invalid token')

        byte = byte_iter.next()
        while byte > 31 and byte not in separators:
            token += chr(byte)
            byte = byte_iter.next()

        return token

    @staticmethod
    def decodeExtensionMedia(byte_iter):
        """ From [5], section 8.4.2.1:
        Extension-media = *TEXT End-of-string
        This encoding is used for media values, which have no well-known
        binary encoding

        @raise DecodeError: The TEXT started with an invalid character.
                            C{byte_iter} is not modified if this happens.

        @return: The decoded media type value
        @rtype: str
        """
        media_value = ''
        byte = byte_iter.preview()
        if byte < 32 or byte == 127:
            byte_iter.reset_preview()
            raise DecodeError('Invalid Extension-media: TEXT '
                              'starts with invalid character: %d' % byte)

        byte = byte_iter.next()
        while byte != 0x00:
            media_value += chr(byte)
            byte = byte_iter.next()

        return media_value

    @staticmethod
    def decodeConstrainedEncoding(byte_iter):
        """Constrained-encoding = Extension-Media  --or--  Short-integer
        This encoding is used for token values, which have no well-known
        binary encoding, or when the assigned number of the well-known
        encoding is small enough to fit into Short-integer.

        @return: The decoding constrained-encoding token value
        @rtype: str or int
        """
        result = None
        try:
            # First try and see if this is just a short-integer
            result = Decoder.decodeShortInteger(byte_iter)
        except DecodeError, msg:
            # Ok, it should be Extension-Media then
            try:
                result = Decoder.decodeExtensionMedia(byte_iter)
            except DecodeError, msg:
                # Give up
                raise DecodeError('Not a valid Constrained-encoding sequence')

        return result

    @staticmethod
    def decodeShortLength(byte_iter):
        """ From [5], section 8.4.2.2:
        Short-length = <Any octet 0-30>

        @raise DecodeError: The byte is not a valid short-length value;
                            it is not in octet range 0-30. In this case, the
                            iterator passed as C{byte_iter} is not modified.

        @note: If this function returns successfully, the iterator passed as
               C{byte_iter} is moved one byte forward.

        @return: The decoded short-length
        @rtype: int
        """
        # Make sure it's a valid short-length
        byte = byte_iter.preview()
        if byte > 30:
            byte_iter.reset_preview()
            raise DecodeError('Not a valid short-length: '
                              'should be in octet range 0-30')

        return byte_iter.next()

    @staticmethod
    def decodeValueLength(byte_iter):
        """Decodes the value length indicator starting at the byte pointed to
        by C{byte_iter.next()}.

        "Value length" is used to indicate the length of a value to follow, as
        used in the C{Content-Type} header in the MMS body, for example.

        The encoding for a value length indicator is specified in [5],
        section 8.4.2.2, and follows the form::

         Value-length = [Short-length]  --or--  [Length-quote] [Length]
                            ^^^^^^                  ^^^^^^      ^^^^^^
                            1 byte                  1 byte      x bytes
                       <Any octet 0-30>          <Octet 31>   Uintvar-integer

        @raise DecodeError: The ValueLength could not be decoded. If this
                            happens, C{byte_iter} is not modified.

        @return: The decoded value length indicator
        @rtype: int
        """
        length_value = 0
        # Check for short-length
        try:
            length_value = Decoder.decodeShortLength(byte_iter)
        except DecodeError:
            byte = byte_iter.preview()
            # CHECK: this strictness MAY cause issues, but it is correct
            if byte == 31:
                byte_iter.next()  # skip past the length-quote
                length_value = Decoder.decodeUintvar(byte_iter)
            else:
                byte_iter.reset_preview()
                raise DecodeError('Invalid Value-length: not short-length, '
                                  'and no length-quote present')

        return length_value

    @staticmethod
    def decodeIntegerValue(byte_iter):
        """ From [5], section 8.4.2.3:
        Integer-Value = Short-integer | Long-integer

        @raise DecodeError: The sequence of bytes starting at
                            C{byte_iter.next()} does not contain a valid
                            integervalue. If this is raised, the iterator
                            passed as C{byte_iter} is not modified.

        @note: If successful, this function will move the iterator passed as
               C{byte_iter} to the last octet in the integer value sequence;
               thus, after calling this, that iterator's C{next()} function
               will return the first byte B{after}the integer value sequence.

        @return: The decoded integer value
        @rtype: int
        """
        integer = 0
        # First try and see if it's a short-integer
        try:
            integer = Decoder.decodeShortInteger(byte_iter)
        except DecodeError:
            try:
                integer = Decoder.decodeLongInteger(byte_iter)
            except DecodeError:
                raise DecodeError('Not a valid integer value')

        return integer

    @staticmethod
    def decodeContentTypeValue(byte_iter):
        """Decodes an encoded content type value.

        From [5], section 8.4.2.24:
        C{Content-type-value = Constrained-media | Content-general-form}

        The short form of the Content-type-value MUST only be used when the
        well-known media is in the range of 0-127 or a text string. In all
        other cases the general form MUST be used.

        @return: The media type (content type), and a dictionary of
                 parameters to this content type (which is empty if there
                 are no parameters). This parameter dictionary is in the
                 format:
                 C{{<str:parameter_name>: <str/int/float:parameter_value>}}.
                 The final returned tuple is in the format:
                 (<str:media_type>, <dict:parameter_dict>)
        @rtype: tuple
        """
        # First try do decode it as Constrained-media
        content_type = ''
        params = {}
        try:
            content_type = Decoder.decodeConstrainedMedia(byte_iter)
        except DecodeError:
            # Try the general form
            content_type, params = Decoder.decodeContentGeneralForm(byte_iter)

        return content_type, params

    @staticmethod
    def decodeWellKnownMedia(byte_iter):
        """ From [5], section 8.4.2.7:
        Well-known-media = Integer-value
        It is encoded using values from the "Content Type Assignments" table
        (see [5], table 40).

        @param byte_iter: an iterator over a sequence of bytes
        @type byte_iter: iter

        @raise DecodeError: This is raised if the integer value representing
                            the well-known media type cannot be decoded
                            correctly, or the well-known media type value
                            could not be found in the table of assigned
                            content types.
                            If this exception is raised, the iterator passed
                            as C{byte_iter} is not modified.

        @note: If successful, this function will move the iterator passed as
               C{byte_iter} to the last octet in the content type value
               sequence; thus, after calling this, that iterator's C{next()}
               function will return the first byte B{after}the content type
               value sequence.

        @return: the decoded MIME content type name
        @rtype: str
        """
        try:
            value = Decoder.decodeIntegerValue(byte_iter)
        except DecodeError:
            raise DecodeError('Invalid well-known media: could not read '
                              'integer value representing it')

        try:
            return WSPEncodingAssignments.wkContentTypes[value]
        except IndexError:
            raise DecodeError('Invalid well-known media: could not '
                              'find content type in table of assigned values')

    @staticmethod
    def decodeMediaType(byte_iter):
        """ From [5], section 8.2.4.24:
        Media-type = (Well-known-media | Extension-Media) *(Parameter)

        @param byte_iter: an iterator over a sequence of bytes
        @type byte_iter: iter

        @note: Used by C{decodeContentGeneralForm()}

        @return: The decoded media type
        @rtype: str
        """
        try:
            return Decoder.decodeWellKnownMedia(byte_iter)
        except DecodeError:
            return Decoder.decodeExtensionMedia(byte_iter)

    @staticmethod
    def decodeConstrainedMedia(byte_iter):
        """ From [5], section 8.4.2.7:
        Constrained-media = Constrained-encoding
        It is encoded using values from the "Content Type Assignments" table.

        @raise DecodeError: Invalid constrained media sequence

        @return: The decoded media type
        @rtype: str
        """
        try:
            media_value = Decoder.decodeConstrainedEncoding(byte_iter)
        except DecodeError, msg:
            raise DecodeError('Invalid Constrained-media: %s' % msg)

        if isinstance(media_value, int):
            try:
                return WSPEncodingAssignments.wkContentTypes[media_value]
            except IndexError:
                raise DecodeError('Invalid constrained media: could not '
                                  'find well-known content type')

        return media_value

    @staticmethod
    def decodeContentGeneralForm(byte_iter):
        """ From [5], section 8.4.2.24:
        Content-general-form = Value-length Media-type

        @note: Used in decoding Content-type fields and their parameters;
               see C{decodeContentTypeValue}

        @note: Used by C{decodeContentTypeValue()}

        @return: The media type (content type), and a dictionary of
                 parameters to this content type (which is empty if there
                 are no parameters). This parameter dictionary is in the
                 format:
                 C{{<str:parameter_name>: <str/int/float:parameter_value>}}.
                 The final returned tuple is in the format:
                 (<str:media_type>, <dict:parameter_dict>)
        @rtype: tuple
        """
        # This is the length of the (encoded) media-type and all parameters
        value_length = Decoder.decodeValueLength(byte_iter)

        # Read parameters, etc, until <value_length> is reached
        ct_field_bytes = array.array('B')
        for i in range(value_length):
            ct_field_bytes.append(byte_iter.next())

        ct_iter = PreviewIterator(ct_field_bytes)
        # Now, decode all the bytes read
        media_type = Decoder.decodeMediaType(ct_iter)
        # Decode the included paramaters (if any)
        parameters = {}
        while True:
            try:
                parameter, value = Decoder.decodeParameter(ct_iter)
                parameters[parameter] = value
            except StopIteration:
                break

        return media_type, parameters

    @staticmethod
    def decodeParameter(byte_iter):
        """ From [5], section 8.4.2.4:
        Parameter = Typed-parameter | Untyped-parameter

        @return: The name of the parameter, and its value, in the format:
                 (<parameter name>, <parameter value>)
        @rtype: tuple
        """
        try:
            return Decoder.decodeTypedParameter(byte_iter)
        except DecodeError:
            return Decoder.decodeUntypedParameter(byte_iter)

    @staticmethod
    def decodeTypedParameter(byte_iter):
        """ From [5], section 8.4.2.4:
        C{Typed-parameter = Well-known-parameter-token Typed-value}
        The actual expected type of the value is implied by the well-known
        parameter.

        @note: This is used in decoding parameters; see C{decodeParameter}

        @return: The name of the parameter, and its value, in the format:
                 (<parameter name>, <parameter value>)
        @rtype: tuple
        """
        token, value_type = Decoder.decodeWellKnownParameter(byte_iter)
        typed_value = ''
        try:
            typed_value = getattr(Decoder, 'decode%s' % value_type)(byte_iter)
        except DecodeError, msg:
            raise DecodeError('Could not decode Typed-parameter: %s' % msg)
        except:
            debug('A fatal error occurred, probably due to an '
                  'unimplemented decoding operation')
            raise

        return token, typed_value

    @staticmethod
    def decodeUntypedParameter(byte_iter):
        """ From [5], section 8.4.2.4:
        C{Untyped-parameter = Token-text Untyped-value}
        The type of the value is unknown, but it shall be encoded as an
        integer, if that is possible.

        @note: This is used in decoding parameters; see C{decodeParameter}

        @return: The name of the parameter, and its value, in the format:
                 (<parameter name>, <parameter value>)
        @rtype: tuple
        """
        token = Decoder.decodeTokenText(byte_iter)
        value = Decoder.decodeUntypedValue(byte_iter)
        return token, value

    @staticmethod
    def decodeUntypedValue(byte_iter):
        """ From [5], section 8.4.2.4:
        Untyped-value = Integer-value | Text-value

        @note: This is used in decoding parameter values; see
               C{decodeUntypedParameter}
        @return: The decoded untyped-value
        @rtype: int or str
        """
        try:
            return Decoder.decodeIntegerValue(byte_iter)
        except DecodeError:
            return Decoder.decodeTextValue(byte_iter)

    @staticmethod
    def decodeWellKnownParameter(byte_iter, version='1.2'):
        """ Decodes the name and expected value type of a parameter of (for
        example) a "Content-Type" header entry, taking into account the WSP
        short form (assigned numbers) of well-known parameter names, as
        specified in section 8.4.2.4 and table 38 of [5].

        From [5], section 8.4.2.4:
        Well-known-parameter-token = Integer-value
        The code values used for parameters are specified in [5], table 38

        @raise ValueError: The specified encoding version is invalid.

        @raise DecodeError: This is raised if the integer value representing
                            the well-known parameter name cannot be decoded
                            correctly, or the well-known paramter token value
                            could not be found in the table of assigned
                            content types.
                            If this exception is raised, the iterator passed
                            as C{byte_iter} is not modified.

        @param version: The WSP encoding version to use. This defaults
                        to "1.2", but may be "1.1", "1.2", "1.3" or
                        1.4" (see table 39 in [5] for details).
        @type version: str

        @return: the decoded parameter name, and its expected value type, in
                 the format (<parameter name>, <expected type>)
        @rtype: tuple
        """
        parameter_name = expected_value = ''
        try:
            parameter_value = Decoder.decodeIntegerValue(byte_iter)
        except DecodeError:
            raise DecodeError('Invalid well-known parameter token: could '
                              'not read integer value representing it')

        wk_params = WSPEncodingAssignments.wellKnownParameters(version)
        if parameter_value in wk_params:
            parameter_name, expected_value = wk_params[parameter_value]
        else:
            #If this is reached, the parameter isn't a WSP well-known one
            raise DecodeError('Invalid well-known parameter token: could '
                              'not find in table of assigned numbers '
                              '(encoding version %s)' % version)

        return parameter_name, expected_value

    #TODO: somehow this should be more dynamic; we need to know what type
    # is EXPECTED (hence the TYPED value)
    @staticmethod
    def decodeTypedValue(byte_iter):
        """ From [5], section 8.4.2.4:
        Typed-value = Compact-value | Text-value
        In addition to the expected type, there may be no value.
        If the value cannot be encoded using the expected type, it shall be
        encoded as text.

        @note: This is used in decoding parameters, see C{decodeParameter()}

        @return: The decoded Parameter Typed-value
        @rtype: str
        """
        typedValue = ''
        try:
            typedValue = Decoder.decodeCompactValue(byte_iter)
        except DecodeError:
            try:
                typedValue = Decoder.decodeTextValue(byte_iter)
            except DecodeError:
                raise DecodeError('Could not decode the Parameter Typed-value')

        return typedValue

    # TODO: somehow this should be more dynamic; we need to know what
    # type is EXPECTED
    @staticmethod
    def decodeCompactValue(byte_iter):
        """ From [5], section 8.4.2.4:
        Compact-value = Integer-value | Date-value | Delta-seconds-value
        | Q-value | Version-value | Uri-value

        @raise DecodeError: Failed to decode the Parameter Compact-value;
                            if this happens, C{byte_iter} is unmodified

        @note: This is used in decoding parameters, see C{decodeTypeValue()}

        @return: The decoded Compact-value (this is specific to the
                 parameter type
        @rtype: str or int
        """
        compact_value = None
        try:
            # First, see if it's an integer value
            # This solves the checks for: Integer-value, Date-value,
            # Delta-seconds-value, Q-value, Version-value
            compact_value = Decoder.decodeIntegerValue(byte_iter)
        except DecodeError:
            try:
                # Try parsing it as a Uri-value
                compact_value = Decoder.decodeUriValue(byte_iter)
            except DecodeError:
                raise DecodeError('Could not decode Parameter Compact-value')

        return compact_value

    @staticmethod
    def decodeDateValue(byte_iter):
        """ From [5], section 8.4.2.3:
        Date-value = Long-integer
        The encoding of dates shall be done in number of seconds from
        1970-01-01, 00:00:00 GMT.

        @raise DecodeError: This method uses C{decodeLongInteger}, and thus
                            raises this under the same conditions.

        @return: The date, in a format such as: C{Tue Nov 27 16:12:21 2007}
        @rtype: str
        """
        return datetime.fromtimestamp(Decoder.decodeLongInteger(byte_iter))

    @staticmethod
    def decodeDeltaSecondsValue(byte_iter):
        """ From [5], section 8.4.2.3:
        Delta-seconds-value = Integer-value
        @raise DecodeError: This method uses C{decodeIntegerValue}, and thus
                            raises this under the same conditions.
        @return: the decoded delta-seconds-value
        @rtype: int
        """
        return Decoder.decodeIntegerValue(byte_iter)

    @staticmethod
    def decodeQValue(byte_iter):
        """ From [5], section 8.4.2.1:
        The encoding is the same as in Uintvar-integer, but with restricted
        size. When quality factor 0 and quality factors with one or two
        decimal digits are encoded, they shall be multiplied by 100 and
        incremented by one, so that they encode as a one-octet value in
        range 1-100, ie, 0.1 is encoded as 11 (0x0B) and 0.99 encoded as
        100 (0x64). Three decimal quality factors shall be multiplied with
        1000 and incremented by 100, and the result shall be encoded as a
        one-octet or two-octet uintvar, eg, 0.333 shall be encoded as 0x83
        0x31. Quality factor 1 is the default value and shall never be sent.

        @return: The decode quality factor (Q-value)
        @rtype: float
        """
        q_value_int = Decoder.decodeUintvar(byte_iter)
        # TODO: limit the amount of decimal points
        if q_value_int > 100:
            return float(q_value_int - 100) / 1000.0

        return float(q_value_int - 1) / 100.0

    @staticmethod
    def decodeVersionValue(byte_iter):
        """ Decodes the version-value. From [5], section 8.4.2.3:
        Version-value = Short-integer | Text-string

        @return: the decoded version value in the format, usually in the
                 format: "<major_version>.<minor_version>"
        @rtype: str
        """
        try:
            byteValue = Decoder.decodeShortInteger(byte_iter)
            major = (byteValue & 0x70) >> 4
            minor = byteValue & 0x0f
            return '%d.%d' % (major, minor)
        except DecodeError:
            return Decoder.decodeTextString(byte_iter)

    @staticmethod
    def decodeUriValue(byte_iter):
        """
        Stub for Uri-value decoding; this is a wrapper to C{decodeTextString}
        """
        return Decoder.decodeTextString(byte_iter)

    @staticmethod
    def decodeTextValue(byte_iter):
        """Stub for Parameter Text-value decoding.
        From [5], section 8.4.2.3:
        Text-value = No-value | Token-text | Quoted-string

        This is used when decoding parameter values; see C{decodeTypedValue()}

        @return: The decoded Parameter Text-value
        @rtype: str
        """
        try:
            return Decoder.decodeTokenText(byte_iter)
        except DecodeError:
            try:
                return Decoder.decodeQuotedString(byte_iter)
            except DecodeError:
                # Ok, so it's a "No-value"
                return ''

    @staticmethod
    def decodeNoValue(byte_iter):
        """Basically verifies that the byte pointed to by C{byte_iter.next()}
        is 0x00.

        @note: If successful, this function will move C{byte_iter} one byte
               forward.

        @raise DecodeError: If 0x00 is not found; C{byte_iter} is not modified
                            if this is raised.

        @return: No-value, which is 0x00
        @rtype: int
        """
        byte_iter, local_iter = byte_iter.next()
        if local_iter.next() != 0x00:
            raise DecodeError('Expected No-value')

        byte_iter.next()
        return 0x00

    @staticmethod
    def decodeAcceptValue(byte_iter):
        """ From [5], section 8.4.2.7:
        Accept-value = Constrained-media | Accept-general-form
        Accept-general-form = Value-length Media-range [Accept-parameters]
        Media-range = (Well-known-media | Extension-Media) *(Parameter)
        Accept-parameters = Q-token Q-value *(Accept-extension)
        Accept-extension = Parameter
        Q-token = <Octet 128>

        @note: most of these things are currently decoded, but discarded (e.g
               accept-parameters); we only return the media type

        @raise DecodeError: The decoding failed. C{byte_iter} will not be
                            modified in this case.
        @return: the decoded Accept-value (media/content type)
        @rtype: str
        """
        accept_value = ''
        # Try to use Constrained-media encoding
        try:
            accept_value = Decoder.decodeConstrainedMedia(byte_iter)
        except DecodeError:
            # ...now try Accept-general-form
            value_length = Decoder.decodeValueLength(byte_iter)
            try:
                media = Decoder.decodeWellKnownMedia(byte_iter)
            except DecodeError:
                media = Decoder.decodeExtensionMedia(byte_iter)

            # Check for the Q-Token (to see if there are Accept-parameters)
            if byte_iter.preview() == 128:
                byte_iter.next()
                q_value = Decoder.decodeQValue(byte_iter)
                try:
                    accept_extension = Decoder.decodeParameter(byte_iter)
                except DecodeError:
                    # Just set an empty iterable
                    accept_extension = []

            byte_iter.reset_preview()
            accept_value = media

        return accept_value

    @staticmethod
    def decodePragmaValue(byte_iter):
        """ Defined in [5], section 8.4.2.38:
        Pragma-value = No-cache | (Value-length Parameter)

        From [5], section 8.4.2.15:
        No-cache = <Octet 128>

        @raise DecodeError: The decoding failed. C{byte_iter} will not be
                            modified in this case.
        @return: the decoded Pragma-value, in the format:
                 (<parameter name>, <parameter value>)
        @rtype: tuple
        """
        byte = byte_iter.preview()
        if byte == 0x80:  # No-cache
            byte_iter.next()
            # TODO: Not sure if this parameter name (or even usage) is correct
            parameter_name = 'Cache-control'
            parameter_value = 'No-cache'
        else:
            byte_iter.reset_preview()
            value_length = Decoder.decodeValueLength(byte_iter)
            parameter_name, parameter_value = Decoder.decodeParameter(byte_iter)

        return parameter_name, parameter_value

    @staticmethod
    def decodeWellKnownCharset(byte_iter):
        """ From [5], section 8.4.2.8:
        C{Well-known-charset = Any-charset | Integer-value}
        It is encoded using values from "Character Set Assignments" table.
        C{Any-charset = <Octet 128>}
        Equivalent to the special RFC2616 charset value "*"
        """
        decoded_charset = ''
        # Look for the Any-charset value
        byte = byte_iter.preview()
        byte_iter.reset_preview()
        if byte == 127:
            byte_iter.next()
            decoded_charset = '*'
        else:
            charset_value = Decoder.decodeIntegerValue(byte_iter)
            if charset_value in WSPEncodingAssignments.wkCharSets:
                decoded_charset = WSPEncodingAssignments.wkCharSets[charset_value]
            else:
                # This charset is not in our table... so just use the
                # value (at least for now)
                decoded_charset = str(charset_value)

        return decoded_charset

    @staticmethod
    def decodeWellKnownHeader(byte_iter):
        """ From [5], section 8.4.2.6:
        C{Well-known-header = Well-known-field-name Wap-value}
        C{Well-known-field-name = Short-integer}
        C{Wap-value = <many different headers value, most not implemented>}

        @todo: Currently, "Wap-value" is decoded as a Text-string in most cases

        @return: The header name, and its value, in the format:
                 (<str:header_name>, <str:header_value>)
        @rtype: tuple
        """
        field_value = Decoder.decodeShortInteger(byte_iter)
        hdr_fields = WSPEncodingAssignments.header_field_names()
        # TODO: *technically* this can fail, but then we have already
        # read a byte... should fix?
        if field_value not in range(len(hdr_fields)):
            raise DecodeError('Invalid Header Field value: %d' % field_value)

        field_name = hdr_fields[field_value]

        # TODO: make this flow better, and implement it in
        # decodeApplicationHeader also
        # Currently we decode most headers as TextStrings, except
        # where we have a specific decoding algorithm implemented
        header_field_encodings = WSPEncodingAssignments.hdrFieldEncodings
        if field_name in header_field_encodings:
            wap_value_type = header_field_encodings[field_name]
            try:
                decoded_value = getattr(Decoder,
                                       'decode%s' % wap_value_type)(byte_iter)
            except DecodeError, msg:
                raise DecodeError('Could not decode Wap-value: %s' % msg)
            except:
                debug('An error occurred, probably due to an '
                      'unimplemented decoding operation. Tried to '
                      'decode header: %s' % field_name)
                raise

        else:
            decoded_value = Decoder.decodeTextString(byte_iter)

        return field_name, decoded_value

    @staticmethod
    def decodeApplicationHeader(byte_iter):
        """ From [5], section 8.4.2.6:
        C{Application-header = Token-text Application-specific-value}

        From [4], section 7.1:
        C{Application-header = Token-text Application-specific-value}
        C{Application-specific-value = Text-string}

        @note: This is used when decoding generic WSP headers;
               see C{decode_header()}.
        @note: We follow [4], and decode the "Application-specific-value"
               as a Text-string

        @return: The application-header, and its value, in the format:
                 (<str:application_header>, <str:application_specific_value>)
        @rtype: tuple
        """
        try:
            app_header = Decoder.decodeTokenText(byte_iter)
        #FNA: added for brute-forcing
        except DecodeError:
            app_header = Decoder.decodeTextString(byte_iter)

        app_specific_value = Decoder.decodeTextString(byte_iter)
        return app_header, app_specific_value

    @staticmethod
    def decode_header(byte_iter):
        """Decodes a WSP header entry

        From [5], section 8.4.2.6:
        C{Header = Message-header | Shift-sequence}
        C{Message-header = Well-known-header | Application-header}
        C{Well-known-header = Well-known-field-name Wap-value}
        C{Application-header = Token-text Application-specific-value}

        @note: "Shift-sequence" encoding has not been implemented
        @note: Currently, almost all header values are treated as text-strings

        @return: The decoded headername, and its value, in the format:
                 (<str:header_name>, <str:header_value>)
        @rtype: tuple
        """
        # First try decoding the header as a well-known-header
        try:
            return Decoder.decodeWellKnownHeader(byte_iter)
        except DecodeError:
            # ...now try Application-header encoding
            return Decoder.decodeApplicationHeader(byte_iter)


class Encoder:
    """A WSP Data unit decoder"""

    @staticmethod
    def encodeUint8(uint):
        """ Encodes an 8-bit unsigned integer

        @param uint: The integer to encode
        @type byte_iter: int

        @return: the encoded Uint8, as a sequence of bytes
        @rtype: list
        """
        # Make the byte unsigned
        return [uint & 0xff]

    @staticmethod
    def encodeUintvar(uint):
        """ Variable Length Unsigned Integer encoding algorithm

        This binary-encodes the given unsigned integer number as specified
        in section 8.1.2 of [5]. Basically, each encoded byte has the
        following structure::

            [0][ Payload ]
             |   ^^^^^^^
             |   7 bits (actual data)
             |
            Continue bit

        The uint is split into 7-bit segments, and the "continue bit" of each
        used octet is set to '1' to indicate more is to follow; the last used
        octet's "continue bit" is set to 0.

        @return: the binary-encoded Uintvar, as a list of byte values
        @rtype: list
        """
        uint_var = [uint & 0x7f]
        # Since this is the lowest entry, we do not set the continue bit to 1
        uint = uint >> 7
        # ...but for the remaining octets, we have to
        while uint > 0:
            uint_var.insert(0, 0x80 | (uint & 0x7f))
            uint = uint >> 7

        return uint_var

    @staticmethod
    def encodeTextString(string):
        """ Encodes a "Text-string" value.

        This follows the basic encoding rules specified in [5], section
        8.4.2.1

        @param string: The text string to encode
        @type string: str

        @return: the null-terminated, binary-encoded version of the
                     specified Text-string, as a list of byte values
        @rtype: list
        """
        encoded_string = list(map(ord, string))
        encoded_string.append(0x00)
        return encoded_string

    @staticmethod
    def encodeShortInteger(integer):
        """ Encodes the specified short-integer value

        The encoding for a long integer is specified in [5], section 8.4.2.1:
        C{Short-integer = OCTET}
        Integers in range 0-127 shall be encoded as a one octet value with
        the most significant bit set to one (1xxx xxxx) and with the value
        in the remaining least significant bits.

        @param integer: The short-integer value to encode
        @type integer: int

        @raise EncodeError: Not a valid short-integer; the integer must be in
                            the range of 0-127

        @return: The encoded short integer, as a list of byte values
        @rtype: list
        """
        if integer < 0 or integer > 127:
            raise EncodeError('Short-integer value must be in '
                              'range 0-127: %d' % integer)

        # Make sure the MSB is set
        return [integer | 0x80]

    @staticmethod
    def encodeLongInteger(integer):
        """Encodes a Long-integer value

        The encoding for a long integer is specified in [5], section 8.4.2.1;
        for a description of this encoding scheme, see
        C{wsp.Decoder.decodeLongIntger()}.

        Basically:
        From [5], section 8.4.2.2:
        Long-integer = Short-length Multi-octet-integer
        Short-length = <Any octet 0-30>

        @raise EncodeError: <integer> is not of type "int"

        @param integer: The integer value to encode
        @type integer: int

        @return: The encoded Long-integer, as a sequence of byte values
        @rtype: list
        """
        if not isinstance(integer, int):
            raise EncodeError('<integer> must be of type "int"')

        encoded_long_int = []
        longInt = integer
        # Encode the Multi-octect-integer
        while longInt > 0:
            byte = 0xff & longInt
            encoded_long_int.append(byte)
            longInt = longInt >> 8

        # Now add the SHort-length value, and make sure it's ok
        shortLength = len(encoded_long_int)
        if shortLength > 30:
            raise EncodeError('Cannot encode Long-integer value: Short-length '
                              'is too long; should be in octet range 0-30')
        encoded_long_int.insert(0, shortLength)
        return encoded_long_int

    @staticmethod
    def encodeVersionValue(version):
        """ Encodes the version-value. From [5], section 8.4.2.3:
        Version-value = Short-integer | Text-string

        Example: An MMS version of "1.0" consists of a major version of 1 and a
        minor version of 0, and would be encoded as 0x90. However, a version
        of "1.2.4" would be encoded as the Text-string "1.2.4".

        @param version: The version number to encode, e.g. "1.0"
        @type version: str

        @raise TypeError: The specified version value was not of type C{str}

        @return: the encoded version value, as a list of byte values
        @rtype: list
        """
        if not isinstance(version, str):
            raise TypeError('Parameter must be of type "str"')

        encoded_version_val = []
        # First try short-integer encoding
        try:
            if len(version.split('.')) <= 2:
                major_version = int(version.split('.')[0])
                if major_version < 1 or major_version > 7:
                    raise ValueError('Major version must be in range 1-7')

                major = major_version << 4
                if len(version.split('.')) == 2:
                    minor_version = int(version.split('.')[1])
                    if minor_version < 0 or minor_version > 14:
                        raise ValueError('Minor version must be in range 0-14')
                else:
                    minor_version = 15

                minor = minor_version
                encoded_version_val = Encoder.encodeShortInteger(major | minor)
        except:
            # The value couldn't be encoded as a short-integer; use
            # a text-string instead
            encoded_version_val = Encoder.encodeTextString(version)

        return encoded_version_val

    @staticmethod
    def encodeMediaType(content_type):
        """Encodes the specified MIME content type ("Media-type" value)

        From [5], section 8.2.4.24:
        Media-type = (Well-known-media | Extension-Media) *(Parameter)

        "Well-known-media" takes into account the WSP short form of well-known
        content types, as specified in section 8.4.2.24 and table 40 of [5].

        @param content_type: The MIME content type to encode
        @type content_type: str

        @return: The binary-encoded content type, as a list of (integer) byte
                 values
        @rtype: list
        """
        if content_type in WSPEncodingAssignments.wkContentTypes:
            # Short-integer encoding
            val = Encoder.encodeShortInteger(
                    WSPEncodingAssignments.wkContentTypes.index(content_type))
        else:
            val = Encoder.encodeTextString(content_type)

        return [val]

    @staticmethod
    def encode_parameter(parameter_name, parameter_value, version='1.2'):
        """ Binary-encodes the name of a parameter of (for example) a
        "Content-Type" header entry, taking into account the WSP short form of
        well-known parameter names, as specified in section 8.4.2.4 and table
        38 of [5].

        From [5], section 8.4.2.4:
        C{Parameter = Typed-parameter | Untyped-parameter}
        C{Typed-parameter = Well-known-parameter-token Typed-value}
        C{Untyped-parameter = Token-text Untyped-value}
        C{Untyped-value = Integer-value | Text-value}

        @param parameter_name: The name of the parameter to encode
        @type parameter_name: str
        @param parameter_value: The value of the parameter
        @type parameter_value: str or int

        @param version: The WSP encoding version to use. This defaults
                        to "1.2", but may be "1.1", "1.2", "1.3" or
                        "1.4" (see table 38 in [5] for details).
        @type version: str

        @raise ValueError: The specified encoding version is invalid.

        @return: The binary-encoded parameter name, as a list of (integer)
                 byte values
        @rtype: list
        """
        wk_params = WSPEncodingAssignments.wellKnownParameters(version)
        encoded_parameter = []
        # Try to encode the parameter using a "Typed-parameter" value
        wkParamNumbers = wk_params.keys()
        wkParamNumbers.sort(reverse=True)
        for assigned_number in wkParamNumbers:
            if wk_params[assigned_number][0] == parameter_name:
                # Ok, it's a Typed-parameter; encode the parameter name
                encoded_parameter.extend(
                        Encoder.encodeShortInteger(assigned_number))
                # and now the value
                expected_type = wk_params[assigned_number][1]
                try:
                    ret = getattr(Encoder,
                                  'encode%s' % expected_type)(parameter_value)
                    encoded_parameter.extend(ret)
                except EncodeError, msg:
                    raise EncodeError('Error encoding param value: %s' % msg)
                except:
                    debug('A fatal error occurred, probably due to an '
                          'unimplemented encoding operation')
                    raise
                break

        # See if the "Typed-parameter" encoding worked
        if len(encoded_parameter) == 0:
            # it didn't. Use "Untyped-parameter" encoding
            encoded_parameter.extend(Encoder.encodeTokenText(parameter_name))
            value = []
            # First try to encode the untyped-value as an integer
            try:
                value = Encoder.encodeIntegerValue(parameter_value)
            except EncodeError:
                value = Encoder.encodeTextString(parameter_value)

            encoded_parameter.extend(value)

        return encoded_parameter

    # TODO: check up on the encoding/decoding of Token-text, in particular,
    # how does this differ from text-string? does it have 0x00 at the end?
    @staticmethod
    def encodeTokenText(text):
        """ From [5], section 8.4.2.1:
        Token-text = Token End-of-string

        @raise EncodeError: Specified text cannot be encoding as a token

        @return: The encoded token string, as a list of byte values
        @rtype: list
        """
        separators = (11, 32, 40, 41, 44, 47, 58, 59, 60, 61, 62, 63, 64,
                      91, 92, 93, 123, 125)
        # Sanity check
        for char in separators:
            if chr(char) in text:
                raise EncodeError('Char "%s" in text string; cannot '
                                  'encode as Token-text' % chr(char))

        return Encoder.encodeTextString(text)

    @staticmethod
    def encodeIntegerValue(integer):
        """ Encodes an integer value

        From [5], section 8.4.2.3:
        Integer-Value = Short-integer | Long-integer

        This function will first try to encode the specified integer value
        into a short-integer, and failing that, will encode into a
        long-integer value.

        @param integer: The integer to encode
        @type integer: int

        @raise EncodeError: The <integer> parameter is not of type C{int}

        @return: The encoded integer value, as a list of byte values
        @rtype: list
        """
        if not isinstance(integer, int):
            raise EncodeError('<integer> must be of type "int"')

        # First try and see if it's a short-integer
        try:
            return Encoder.encodeShortInteger(integer)
        except EncodeError:
            return Encoder.encodeLongInteger(integer)

    @staticmethod
    def encodeTextValue(text):
        """ Stub for encoding Text-values; this is equivalent to
        C{encodeTextString} """
        return Encoder.encodeTextString(text)

    @staticmethod
    def encodeNoValue(value=None):
        """ Encodes a No-value, which is 0x00

        @note: This function mainly exists for use by automatically-selected
               encoding routines (see C{encode_parameter()} for an example.

        @param value: This value is ignored; it is present so that this
                      method complies with the format of the other C{encode}
                      methods.

        @return: A list containing a single "No-value", which is 0x00
        @rtype: list
        """
        return [0x00]

    @staticmethod
    def encode_header(field_name, value):
        """ Encodes a WSP header entry, and its value

        From [5], section 8.4.2.6:
        C{Header = Message-header | Shift-sequence}
        C{Message-header = Well-known-header | Application-header}
        C{Well-known-header = Well-known-field-name Wap-value}
        C{Application-header = Token-text Application-specific-value}

        @note: "Shift-sequence" encoding has not been implemented
        @note: Currently, almost all header values are encoded as
               text-strings

        @return: The encoded header, and its value, as a sequence of
                 byte values
        @rtype: list
        """
        encoded_header = []
        # First try encoding the header name as a "well-known-header"...
        wkHdrFields = WSPEncodingAssignments.header_field_names()
        if field_name in wkHdrFields:
            header_field_value = Encoder.encodeShortInteger(
                                    wkHdrFields.index(field_name))
            encoded_header.extend(header_field_value)
        else:
            # otherwise, encode it as an "application header"
            encoded_header_name = Encoder.encodeTokenText(field_name)
            encoded_header.extend(encoded_header_name)

        # Now add the value
        # TODO: make this flow better (see also Decoder.decode_header)
        # most header values are encoded as TextStrings, except where we
        # have a specific Wap-value encoding implementation
        header_field_encodings = WSPEncodingAssignments.hdrFieldEncodings
        if field_name in header_field_encodings:
            wap_value_type = header_field_encodings[field_name]
            try:
                ret = getattr(Encoder, 'encode%s' % wap_value_type)(value)
                encoded_header.extend(ret)
            except EncodeError, msg:
                raise EncodeError('Error encoding Wap-value: %s' % msg)
            except:
                debug('A fatal error occurred, probably due to an '
                      'unimplemented encoding operation')
                raise
        else:
            encoded_header.extend(Encoder.encodeTextString(value))

        return encoded_header

    @staticmethod
    def encodeContentTypeValue(media_type, parameters):
        """ Encodes a content type, and its parameters

        From [5], section 8.4.2.24:
        C{Content-type-value = Constrained-media | Content-general-form}

        The short form of the Content-type-value MUST only be used when the
        well-known media is in the range of 0-127 or a text string. In all
        other cases the general form MUST be used.

        @return: The encoded Content-type-value (including parameters, if
                 any), as a sequence of bytes
        @rtype: list
        """
        # First try do encode it using Constrained-media encoding
        try:
            if len(parameters):
                raise EncodeError('Need to use '
                                  'Content-general-form for parameters')

            return Encoder.encodeConstrainedMedia(media_type)
        except EncodeError:
            # Try the general form
            return Encoder.encodeContentGeneralForm(media_type, parameters)

    @staticmethod
    def encodeConstrainedMedia(media_type):
        """ From [5], section 8.4.2.7:
        Constrained-media = Constrained-encoding
        It is encoded using values from the "Content Type Assignments" table.

        @param media_type: The media type to encode
        @type media_type: str

        @raise EncodeError: Media value is unsuitable for Constrained-encoding

        @return: The encoded media type, as a sequence of bytes
        @rtype: list
        """
        # See if this value is in the table of well-known content types
        if media_type in WSPEncodingAssignments.wkContentTypes:
            value = WSPEncodingAssignments.wkContentTypes.index(media_type)
        else:
            value = media_type

        return Encoder.encodeConstrainedEncoding(value)

    @staticmethod
    def encodeConstrainedEncoding(value):
        """ Constrained-encoding = Extension-Media  --or--  Short-integer
        This encoding is used for token values, which have no well-known
        binary encoding, or when the assigned number of the well-known
        encoding is small enough to fit into Short-integer.

        @param value: The value to encode
        @type value: int or str

        @raise EncodeError: <value> cannot be encoded as a
                            Constrained-encoding sequence

        @return: The encoded constrained-encoding token value, as a sequence
                 of bytes
        @rtype: list
        """
        encoded_value = None
        if isinstance(value, int):
            # First try and encode the value as a short-integer
            encoded_value = Encoder.encodeShortInteger(value)
        else:
            # Ok, it should be Extension-Media then
            try:
                encoded_value = Encoder.encodeExtensionMedia(value)
            except EncodeError:
                # Give up
                raise EncodeError('Cannot encode %s as a '
                                  'Constrained-encoding sequence' % str(value))

        return encoded_value

    @staticmethod
    def encodeExtensionMedia(media_value):
        """ From [5], section 8.4.2.1:
        Extension-media = *TEXT End-of-string
        This encoding is used for media values, which have no well-known
        binary encoding

        @param media_value: The media value (string) to encode
        @type media_value: str

        @raise EncodeError: The value cannot be encoded as TEXT; probably it
                            starts with/contains an invalid character

        @return: The encoded media type value, as a sequence of bytes
        @rtype: str
        """
        if not isinstance(media_value, basestring):
            try:
                media_value = str(media_value)
            except:
                raise EncodeError('Invalid Extension-media: Cannot convert '
                                  'value to text string')
        char = media_value[0]
        if ord(char) < 32 or ord(char) == 127:
            raise EncodeError('Invalid Extension-media: TEXT starts with '
                              'invalid character: %s' % ord(char))

        return Encoder.encodeTextString(media_value)

    @staticmethod
    def encodeContentGeneralForm(media_type, parameters):
        """ From [5], section 8.4.2.24:
        Content-general-form = Value-length Media-type

        @note: Used in decoding Content-type fields and their parameters;
               see C{decodeContentTypeValue}

        @note: Used by C{decodeContentTypeValue()}

        @return: The encoded Content-general-form, as a sequence of bytes
        @rtype: list
        """
        enconded_content_general_form = []
        encoded_media_type = []
        # Encode the actual content type
        encoded_media_type = Encoder.encodeMediaType(media_type)
        # Encode all parameters
        encoded_parameters = [Encoder.encode_parameter(name, parameters[name])
                                    for name in parameters]

        value_length = len(encoded_media_type) + len(encoded_parameters)
        encoded_value_length = Encoder.encodeValueLength(value_length)
        enconded_content_general_form.extend(encoded_value_length)
        enconded_content_general_form.extend(encoded_media_type)
        enconded_content_general_form.extend(encoded_parameters)

        return enconded_content_general_form

    @staticmethod
    def encodeValueLength(length):
        """ Encodes the specified length value as a value length indicator

        "Value length" is used to indicate the length of a value to follow, as
        used in the C{Content-Type} header in the MMS body, for example.

        The encoding for a value length indicator is specified in [5],
        section 8.4.2.2, and follows the form::

         Value-length = [Short-length]  --or--  [Length-quote] [Length]
                            ^^^^^^                  ^^^^^^      ^^^^^^
                            1 byte                  1 byte      x bytes
                       <Any octet 0-30>          <Octet 31>   Uintvar-integer

        @raise EncodeError: The ValueLength could not be encoded.

        @return: The encoded value length indicator, as a sequence of bytes
        @rtype: list
        """
        encoded_value_length = []
        # Try and encode it as a short-length
        try:
            encoded_value_length = Encoder.encodeShortLength(length)
        except EncodeError:
            # Encode it with a Length-quote and Uintvar
            encoded_value_length.append(31)  # Length-quote
            encoded_value_length.extend(Encoder.encodeUintvar(length))

        return encoded_value_length

    @staticmethod
    def encodeShortLength(length):
        """ From [5], section 8.4.2.2:
        Short-length = <Any octet 0-30>

        @raise EmcodeError: The specified <length> cannot be encoded as a
                            short-length value; it is not in octet range 0-30.

        @return: The encoded short-length, as a sequence of bytes
        @rtype: list
        """
        if length < 0 or length > 30:
            raise EncodeError('Cannot encode short-length; length should '
                              'be in the 0-30 range')

        return [length]

    @staticmethod
    def encodeAcceptValue(accept_value):
        """ From [5], section 8.4.2.7:
        Accept-value = Constrained-media | Accept-general-form
        Accept-general-form = Value-length Media-range [Accept-parameters]
        Media-range = (Well-known-media | Extension-Media) *(Parameter)
        Accept-parameters = Q-token Q-value *(Accept-extension)
        Accept-extension = Parameter
        Q-token = <Octet 128>

        @note: This implementation does not currently support encoding of
               "Accept-parameters".

        @param accept_value: The Accept-value to encode (media/content type)
        @type accept_value: str

        @raise EncodeError: The encoding failed.

        @return: The encoded Accept-value, as a sequence of bytes
        @rtype: list
        """
        encoded_accept_value = []
        # Try to use Constrained-media encoding
        try:
            encoded_accept_value = Encoder.encodeConstrainedMedia(accept_value)
        except EncodeError:
            # ...now try Accept-general-form
            try:
                encoded_media_range = Encoder.encodeMediaType(accept_value)
            except EncodeError, msg:
                raise EncodeError('Cannot encode Accept-value: %s' % msg)

            value_length = Encoder.encodeValueLength(len(encoded_media_range))
            encoded_accept_value = value_length
            encoded_accept_value.extend(encoded_media_range)

        return encoded_accept_value
