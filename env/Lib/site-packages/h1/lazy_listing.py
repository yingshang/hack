# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function, unicode_literals, division, absolute_import

import collections
import itertools
import threading

import six


# From itertools documentation
def _consume(iterator, n=None):
    """Advance the iterator n-steps ahead. If n is none, consume entirely."""
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(itertools.islice(iterator, n, n), None)


def _slice_required_len(slice_obj):
    """
    Calculate how many items must be in the collection to satisfy this slice

    returns `None` for slices may vary based on the length of the underlying collection
    such as `lst[-1]` or `lst[::]`
    """
    if slice_obj.step and slice_obj.step != 1:
        return None
    # (None, None, *) requires the entire list
    if slice_obj.start is None and slice_obj.stop is None:
        return None

    # Negative indexes are hard without knowing the collection length
    if slice_obj.start and slice_obj.start < 0:
        return None
    if slice_obj.stop and slice_obj.stop < 0:
        return None

    if slice_obj.stop:
        if slice_obj.start and slice_obj.start > slice_obj.stop:
            return 0
        return slice_obj.stop
    return slice_obj.start + 1


class LazyListing(object):
    def __init__(self, res_iter):
        self._items = []
        self._res_iter = iter(res_iter)
        self._res_lock = threading.RLock()

    def _ensure_elements_available(self, n=None):
        if self._res_iter:
            with self._res_lock:
                if not self._res_iter:
                    return
                if n is None or n > len(self._items):
                    _consume(self, n)

    def __iter__(self):
        if self._res_iter:
            with self._res_lock:
                # Are there still items left in the resource iterator?
                if self._res_iter:
                    # Yield any items we already have
                    for item in self._items:
                        yield item
                    # Start consuming items from the resource iterator
                    for item in self._res_iter:
                        self._items.append(item)
                        yield item
                    self._res_iter = None
                    return

        for item in self._items:
            yield item

    def __len__(self):
        self._ensure_elements_available()
        return len(self._items)

    def __getitem__(self, item):
        # Figure out how many items we need to have in self._items to satisfy this.
        # This ensures we don't need to consume the entire iterator to get a
        # slice of the first 2 elems, for ex.
        required_len = None
        if isinstance(item, slice):
            required_len = _slice_required_len(item)
        elif isinstance(item, six.integer_types):
            required_len = item + 1
            if required_len <= 0:
                required_len = None
        self._ensure_elements_available(required_len)
        return self._items[item]

    def __contains__(self, item):
        self._ensure_elements_available()
        return item in self._items

    def __json__(self):
        self._ensure_elements_available()
        return self._items
