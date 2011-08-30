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
# Copyright (C) 2007 Francois Aucamp <francois.aucamp@gmail.com>
#
"""
Multimedia Messaging Service (MMS) library

The :mod:`messaging.mms` module provides several classes for the creation
and manipulation of MMS messages (multimedia messages) used in mobile
devices such as cellular telephones.

Multimedia Messaging Service (MMS) is a messaging service for the mobile
environment standardized by the WAP Forum and 3GPP. To the end-user MMS is
very similar to the text-based Short Message Service (SMS): it provides
automatic immediate delivery for user-created content from device to device.

In addition to text, however, MMS messages can contain multimedia content such
as still images, audio clips and video clips, which are binded together
into a "mini presentation" (or slideshow) that controls for example, the order
in which images are to appear on the screen, how long they will be displayed,
when an audio clip should be played, etc. Furthermore, MMS messages do not have
the 160-character limit of SMS messages.

An MMS message is a multimedia presentation in one entity; it is not a text
file with attachments.

This library enables the creation of MMS messages with full support for
presentation layout, and multimedia data parts such as JPEG, GIF, AMR, MIDI,
3GP, etc. It also allows the decoding and unpacking of received MMS messages.

@version: 0.2
@author: Francois Aucamp C{<francois.aucamp@gmail.com>}
@license: GNU General Public License, version 2
@note: References used in the code and this document:

.. [1] MMS Conformance Document version 2.0.0, 6 February 2002
    U{www.bogor.net/idkf/bio2/mobile-docs/mms_conformance_v2_0_0.pdf}

.. [2] Forum Nokia, "How To Create MMS Services, Version 4.0"
    U{http://forum.nokia.com/info/sw.nokia.com/id/a57a4f20-b7f2-475b-b426-19eff18a5afb/How_To_Create_MMS_Services_v4_0_en2.pdf.html}

.. [3] Wap Forum/Open Mobile ALliance, "WAP-206 MMS Client Transactions"
    U{http://www.openmobilealliance.org/tech/affiliates/LicenseAgreement.asp?DocName=/wap/wap-206-mmsctr-20020115-a.pdf}

.. [4] Wap Forum/Open Mobile Alliance, "WAP-209 MMS Encapsulation Protocol"
    U{http://www.openmobilealliance.org/tech/affiliates/LicenseAgreement.asp?DocName=/wap/wap-209-mmsencapsulation-20020105-a.pdf}

.. [5] Wap Forum/Open Mobile Alliance, "WAP-230 Wireless Session Protocol Specification"
    U{http://www.openmobilealliance.org/tech/affiliates/LicenseAgreement.asp?DocName=/wap/wap-230-wsp-20010705-a.pdf}

.. [6] IANA: "Character Sets"
    U{http://www.iana.org/assignments/character-sets}
"""
