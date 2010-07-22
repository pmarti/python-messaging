# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 2.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net
"""
PyMMS library: Iterator with "value preview" capability.

@version: 0.1
@author: Francois Aucamp C{<faucamp@csir.co.za>}
@license: GNU Lesser General Public License, version 2
"""


class PreviewIterator(object):
    """ An C{iter} wrapper class providing a "previewable" iterator.

    This "preview" functionality allows the iterator to return successive
    values from its C{iterable} object, without actually mvoving forward
    itself. This is very usefuly if the next item(s) in an iterator must
    be used for something, after which the iterator should "undo" those
    read operations, so that they can be read again by another function.

    From the user point of view, this class supersedes the builtin iter()
    function: like iter(), it is called as PreviewIter(iterable).
    """
    def __init__(self, data):
        self._it = iter(data)
        self._cached_values = []
        self._preview_pos = 0

    def __iter__(self):
        return self

    def next(self):
        self.reset_preview()
        if len(self._cached_values) > 0:
            return self._cached_values.pop(0)
        else:
            return self._it.next()

    def preview(self):
        """ Return the next item in the C{iteratable} object, but do not modify
        the actual iterator (i.e. do not intefere with C{iter.next()}.

        Successive calls to C{preview()} will return successive values from
        the C{iterable} object, exactly in the same way C{iter.next()} does.

        However, C{preview()} will always return the next item from
        C{iterable} after the item returned by the previous C{preview()} or
        C{next()} call, whichever was called the most recently.
        To force the "preview() iterator" to synchronize with the "next()
        iterator" (without calling C{next()}), use C{reset_preview()}.
        """
        if self._preview_pos < len(self._cached_values):
            value = self._cached_values[self._preview_pos]
        else:
            value = self._it.next()
            self._cached_values.append(value)

        self._preview_pos += 1
        return value

    def reset_preview(self):
        self._preview_pos = 0
