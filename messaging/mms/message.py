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
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net
"""High-level MMS message classes"""

from __future__ import with_statement
import array
import mimetypes
import os
import xml.dom.minidom


class MMSMessage:
    """
    I am an MMS message

    References used in this class: [1][2][3][4][5]
    """
    def __init__(self):
        self._pages = []
        self._data_parts = []
        self._metaTags = {}
        self._mms_message = None
        self.headers = {
            'Message-Type': 'm-send-req',
            'Transaction-Id': '1234',
            'MMS-Version': '1.0',
            'Content-Type': ('application/vnd.wap.multipart.mixed', {}),
        }
        self.width = 176
        self.height = 220
        self.transactionID = '12345'
        self.subject = 'test'

    @property
    def content_type(self):
        """
        Returns the Content-Type of this data part header

        No parameter information is returned; to get that, access the
        "Content-Type" header directly (which has a tuple value) from
        the message's ``headers`` attribute.

        This is equivalent to calling DataPart.headers['Content-Type'][0]
        """
        return self.headers['Content-Type'][0]

    def add_page(self, page):
        """
        Adds `page` to the message

        :type page: MMSMessagePage
        :param page: The message slide/page to add
        """
        if self.content_type != 'application/vnd.wap.multipart.related':
            value = ('application/vnd.wap.multipart.related', {})
            self.headers['Content-Type'] = value

        self._pages.append(page)

    @property
    def pages(self):
        """Returns a list of all the pages in this message"""
        return self._pages

    def add_data_part(self, data_part):
        """Adds a single data part (DataPart object) to the message, without
        connecting it to a specific slide/page in the message.

        A data part encapsulates some form of attachment, e.g. an image, audio
        etc. It is not necessary to explicitly add data parts to the message
        using this function if :func:`add_page` is used; this method is mainly
        useful if you want to create MMS messages without SMIL support,
        i.e. messages of type "application/vnd.wap.multipart.mixed"

        :param data_part: The data part to add
        :type data_part: DataPart
        """
        self._data_parts.append(data_part)

    @property
    def data_parts(self):
        """
        Returns a list of all the data parts in this message

        including data parts that were added to slides in this message"""
        parts = []
        if len(self._pages):
            parts.append(self.smil())
            for slide in self._mms_message._pages:
                parts.extend(slide.data_parts())

        parts.extend(self._data_parts)
        return parts

    def smil(self):
        """Returns the text of the message's SMIL file"""
        impl = xml.dom.minidom.getDOMImplementation()
        smil_doc = impl.createDocument(None, "smil", None)

        # Create the SMIL header
        head_node = smil_doc.createElement('head')
        # Add metadata to header
        for tag_name in self._metaTags:
            meta_node = smil_doc.createElement('meta')
            meta_node.setAttribute(tag_name, self._metaTags[tag_name])
            head_node.appendChild(meta_node)

        # Add layout info to header
        layout_node = smil_doc.createElement('layout')
        root_layout_node = smil_doc.createElement('root-layout')
        root_layout_node.setAttribute('width', str(self.width))
        root_layout_node.setAttribute('height', str(self.height))
        layout_node.appendChild(root_layout_node)

        areas = (('Image', '0', '0', '176', '144'),
                 ('Text', '176', '144', '176', '76'))

        for region_id, left, top, width, height in areas:
            region_node = smil_doc.createElement('region')
            region_node.setAttribute('id', region_id)
            region_node.setAttribute('left', left)
            region_node.setAttribute('top', top)
            region_node.setAttribute('width', width)
            region_node.setAttribute('height', height)
            layout_node.appendChild(region_node)

        head_node.appendChild(layout_node)
        smil_doc.documentElement.appendChild(head_node)

        # Create the SMIL body
        body_node = smil_doc.createElement('body')
        # Add pages to body
        for page in self._pages:
            par_node = smil_doc.createElement('par')
            par_node.setAttribute('duration', str(page.duration))
            # Add the page content information
            if page.image is not None:
                #TODO: catch unpack exception
                part, begin, end = page.image
                if 'Content-Location' in part.headers:
                    src = part.headers['Content-Location']
                elif 'Content-ID' in part.headers:
                    src = part.headers['Content-ID']
                else:
                    src = part.data

                image_node = smil_doc.createElement('img')
                image_node.setAttribute('src', src)
                image_node.setAttribute('region', 'Image')
                if begin > 0 or end > 0:
                    if end > page.duration:
                        end = page.duration

                    image_node.setAttribute('begin', str(begin))
                    image_node.setAttribute('end', str(end))

                par_node.appendChild(image_node)

            if page.text is not None:
                part, begin, end = page.text
                src = part.data
                text_node = smil_doc.createElement('text')
                text_node.setAttribute('src', src)
                text_node.setAttribute('region', 'Text')
                if begin > 0 or end > 0:
                    if end > page.duration:
                        end = page.duration

                    text_node.setAttribute('begin', str(begin))
                    text_node.setAttribute('end', str(end))

                par_node.appendChild(text_node)

            if page.audio is not None:
                part, begin, end = page.audio
                if 'Content-Location' in part.headers:
                    src = part.headers['Content-Location']
                elif 'Content-ID' in part.headers:
                    src = part.headers['Content-ID']
                else:
                    src = part.data

                audio_node = smil_doc.createElement('audio')
                audio_node.setAttribute('src', src)
                if begin > 0 or end > 0:
                    if end > page.duration:
                        end = page.duration

                    audio_node.setAttribute('begin', str(begin))
                    audio_node.setAttribute('end', str(end))

                par_node.appendChild(text_node)
                par_node.appendChild(audio_node)

            body_node.appendChild(par_node)

        smil_doc.documentElement.appendChild(body_node)
        return smil_doc.documentElement.toprettyxml()

    def encode(self):
        """
        Return a binary representation of this MMS message

        This uses the `~:class:messaging.mms.mms_pdu.MMSEncoder` internally

        :return: The binary-encoded MMS data, as an array of bytes
        :rtype: array.array('B')
        """
        from messaging.mms import mms_pdu
        encoder = mms_pdu.MMSEncoder()
        return encoder.encode(self)

    def to_file(self, filename):
        """
        Writes this MMS message to `filename` in binary-encoded form

        This uses the `~:class:messaging.mms.mms_pdu.MMSEncoder` internally

        :param filename: The path where to store the message data
        :type filename: str

        :rtype array.array('B')
        :return: The binary-encode MMS data, as an array of bytes
        """
        with open(filename, 'wb') as f:
            self.encode().tofile(f)

    @staticmethod
    def from_data(data):
        """
        Returns a new `:class:MMSMessage` out of ``data``

        This uses the `~:class:messaging.mms.mms_pdu.MMSEncoder` internally

        :param data: The data to load
        :type filename: array.array
        """
        from messaging.mms import mms_pdu
        decoder = mms_pdu.MMSDecoder()
        return decoder.decode_data(data)

    @staticmethod
    def from_file(filename):
        """
        Returns a new `:class:MMSMessage` out of file ``filename``

        This uses the `~:class:messaging.mms.mms_pdu.MMSEncoder` internally

        :param filename: The name of the file to load
        :type filename: str
        """
        from messaging.mms import mms_pdu
        decoder = mms_pdu.MMSDecoder()
        return decoder.decode_file(filename)


class MMSMessagePage:
    """
    A single page/slide in an MMS Message.

    In order to ensure that the MMS message can be correctly displayed by most
    terminals, each page's content is limited to having 1 image, 1 audio clip
    and 1 block of text, as stated in [1].

    The default slide duration is set to 4 seconds; use :func:`set_duration`
    to change this.
    """
    def __init__(self):
        self.duration = 4000
        self.image = None
        self.audio = None
        self.text = None

    @property
    def data_parts(self):
        """Returns a list of the data parst in this slide"""
        return [part for part in (self.image, self.audio, self.text)
                    if part is not None]

    def number_of_parts(self):
        """
        Returns the number of data parts in this slide

        @rtype: int
        """
        num_parts = 0
        for item in (self.image, self.audio, self.text):
            if item is not None:
                num_parts += 1

        return num_parts

    #TODO: find out what the "ref" element in SMIL does
    #TODO: add support for "alt" element; also make sure what it does
    def add_image(self, filename, time_begin=0, time_end=0):
        """
        Adds an image to this slide.

        :param filename: The name of the image file to add. Supported formats
                         are JPEG, GIF and WBMP.
        :type filename: str
        :param time_begin: The time (in milliseconds) during the duration of
                          this slide to begin displaying the image. If this is
                          0 or less, the image will be displayed from the
                          moment the slide is opened.
        :type time_begin: int
        :param time_end: The time (in milliseconds) during the duration of this
                        slide at which to stop showing (i.e. hide) the image.
                        If this is 0 or less, or if it is greater than the
                        actual duration of this slide, it will be shown until
                        the next slide is accessed.
        :type time_end: int

        :raise TypeError: An inappropriate variable type was passed in of the
                          parameters
        """
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")

        if not isinstance(time_begin, int) or not isinstance(time_end, int):
            raise TypeError("time_begin and time_end must be ints")

        if not os.path.isfile(filename):
            raise OSError("filename must be a file")

        if time_end > 0 and time_end < time_begin:
            raise ValueError('time_end cannot be lower than time_begin')

        self.image = (DataPart(filename), time_begin, time_end)

    def add_audio(self, filename, time_begin=0, time_end=0):
        """
        Adds an audio clip to this slide.

        :param filename: The name of the audio file to add. Currently the only
                         supported format is AMR.
        :type filename: str
        :param time_begin: The time (in milliseconds) during the duration of
                          this slide to begin playback of the audio clip. If
                          this is 0 or less, the audio clip will be played the
                          moment the slide is opened.
        :type time_begin: int
        :param time_end: The time (in milliseconds) during the duration of this
                        slide at which to stop playing (i.e. mute) the audio
                        clip. If this is 0 or less, or if it is greater than
                        the actual duration of this slide, the entire audio
                        clip will be played, or until the next slide is
                        accessed.
        :type time_end: int
        :raise TypeError: An inappropriate variable type was passed in of the
                          parameters
        """
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")

        if not isinstance(time_begin, int) or not isinstance(time_end, int):
            raise TypeError("time_begin and time_end must be ints")

        if not os.path.isfile(filename):
            raise OSError("filename must be a file")

        if time_end > 0 and time_end < time_begin:
            raise ValueError('time_end cannot be lower than time_begin')

        self.audio = (DataPart(filename), time_begin, time_end)

    def add_text(self, text, time_begin=0, time_end=0):
        """
        Adds a block of text to this slide.

        :param text: The text to add to the slide.
        :type text: str
        :param time_begin: The time (in milliseconds) during the duration of
                          this slide to begin displaying the text. If this is
                          0 or less, the text will be displayed from the
                          moment the slide is opened.
        :type time_begin: int
        :param time_end: The time (in milliseconds) during the duration of this
                        slide at which to stop showing (i.e. hide) the text.
                        If this is 0 or less, or if it is greater than the
                        actual duration of this slide, it will be shown until
                        the next slide is accessed.
        :type time_end: int

        :raise TypeError: An inappropriate variable type was passed in of the
                          parameters
        """
        if not isinstance(text, str):
            raise TypeError("Text must be a string")

        if not isinstance(time_begin, int) or not isinstance(time_end, int):
            raise TypeError("time_begin and time_end must be ints")

        if time_end > 0 and time_end < time_begin:
            raise ValueError('time_end cannot be lower than time_begin')

        time_data = DataPart()
        time_data.set_text(text)
        self.text = (time_data, time_begin, time_end)

    def set_duration(self, duration):
        """ Sets the maximum duration of this slide (i.e. how long this slide
        should be displayed)

        @param duration: the maxium slide duration, in milliseconds
        @type duration: int

        @raise TypeError: <duration> must be an integer
        @raise ValueError: the requested duration is invalid (must be a
                           non-zero, positive integer)
        """
        if not isinstance(duration, int):
            raise TypeError("Duration must be an int")

        if duration < 1:
            raise ValueError('duration may not be 0 or negative')

        self.duration = duration


class DataPart(object):
    """
    I am a data entry in the MMS body

    A DataPart object encapsulates any data content that is to be added
    to the MMS (e.g. an image , raw image data, audio clips, text, etc).

    A DataPart object can be queried using the Python built-in :func:`len`
    function.

    This encapsulation allows custom header/parameter information to be set
    for each data entry in the MMS. Refer to [5] for more information on
    these.
    """
    def __init__(self, filename=None):
        """ @param srcFilename: If specified, load the content of the file
                                with this name
            @type srcFilename: str
        """
        super(DataPart, self).__init__()

        self.content_type_parameters = {}
        self.headers = {'Content-Type': ('application/octet-stream', {})}
        self._filename = None
        self._data = None

        if filename is not None:
            self.from_file(filename)

    def _get_content_type(self):
        """ Returns the string representation of this data part's
        "Content-Type" header. No parameter information is returned;
        to get that, access the "Content-Type" header directly (which has a
        tuple value)from this part's C{headers} attribute.

        This is equivalent to calling DataPart.headers['Content-Type'][0]
        """
        return self.headers['Content-Type'][0]

    def _set_content_type(self, value):
        """Sets the content type string, with no parameters """
        self.headers['Content-Type'] = value, {}

    content_type = property(_get_content_type, _set_content_type)

    def from_file(self, filename):
        """
        Load the data contained in the specified file

        This function clears any previously-set header entries.

        :param filename: The name of the file to open
        :type filename: str

        :raises OSError: The filename is invalid
        """
        if not os.path.isfile(filename):
            raise OSError('The file "%s" does not exist' % filename)

        # Clear any headers that are currently set
        self.headers = {}
        self._data = None
        self.headers['Content-Location'] = os.path.basename(filename)
        content_type = (mimetypes.guess_type(filename)[0]
                                or 'application/octet-stream', {})
        self.headers['Content-Type'] = content_type
        self._filename = filename

    def set_data(self, data, content_type, ct_parameters=None):
        """
        Explicitly set the data contained by this part

        This function clears any previously-set header entries.

        :param data: The data to hold
        :type data: str
        :param content_type: The MIME content type of the specified data
        :type content_type: str
        :param ct_parameters: Any content type header paramaters to add
        :type ct_parameters: dict
        """
        self.headers = {}
        self._filename = None
        self._data = data

        if ct_parameters is None:
            ct_parameters = {}

        self.headers['Content-Type'] = content_type, ct_parameters

    def set_text(self, text):
        """
        Convenience wrapper method for set_data()

        This method sets the :class:`DataPart` object to hold the
        specified text string, with MIME content type "text/plain".

        @param text: The text to hold
        @type text: str
        """
        self.set_data(text, 'text/plain')

    def __len__(self):
        """Provides the length of the data encapsulated by this object"""
        if self._filename is not None:
            return int(os.stat(self._filename)[6])
        else:
            return len(self.data)

    @property
    def data(self):
        """A buffer containing the binary data of this part"""
        if self._data is not None:
            if type(self._data) == array.array:
                self._data = self._data.tostring()
            return self._data

        elif self._filename is not None:
            with open(self._filename, 'r') as f:
                self._data = f.read()
            return self._data

        return ''
