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

import itertools
import unittest

import six.moves

from h1.lazy_listing import LazyListing


class TestLazyListing(unittest.TestCase):

    @staticmethod
    def _gen_lazy_listing():
        return LazyListing(six.moves.range(4))

    def test_iteration(self):
        listing = self._gen_lazy_listing()
        # `list()` implicitly calls `__iter__()`
        self.assertListEqual(list(listing), [0, 1, 2, 3])

    def test_partial_iteration(self):
        listing = self._gen_lazy_listing()
        # stop iterating after 2 item
        for i in itertools.islice(listing, 2):
            pass

        # Now restart iteration and make sure we get the whole list
        self.assertListEqual(list(listing), [0, 1, 2, 3])

    def test_contains(self):
        listing = self._gen_lazy_listing()
        self.assertFalse(5 in listing)
        self.assertTrue(1 in listing)

    def test_simple_index(self):
        listing = self._gen_lazy_listing()
        self.assertEqual(listing[1], 1)

    def test_negative_index(self):
        listing = self._gen_lazy_listing()
        self.assertEqual(listing[-1], 3)

    def test_slice_start(self):
        listing = self._gen_lazy_listing()
        self.assertEqual(listing[1::], [1])

    def test_slice_negative_start(self):
        listing = self._gen_lazy_listing()
        self.assertEqual(listing[-1::], [3])

    def test_slice_stop(self):
        listing = self._gen_lazy_listing()
        self.assertListEqual(listing[:2], [0, 1])

    def test_slice_negative_stop(self):
        listing = self._gen_lazy_listing()
        self.assertListEqual(listing[:-1], [0, 1, 2])

    def test_slice_start_stop(self):
        listing = self._gen_lazy_listing()
        self.assertListEqual(listing[1:2], [1])

    def test_slice_equal_start_stop(self):
        listing = self._gen_lazy_listing()
        self.assertListEqual(listing[1:1:1], [])

    def test_slice_copy(self):
        listing = self._gen_lazy_listing()
        self.assertListEqual(listing[::], [0, 1, 2, 3])

    def test_slice_reverse(self):
        listing = self._gen_lazy_listing()
        self.assertListEqual(listing[::-1], [3, 2, 1, 0])

    def test_len(self):
        listing = self._gen_lazy_listing()
        self.assertEqual(len(listing), 4)

    def test_json_serialization(self):
        listing = self._gen_lazy_listing()
        as_json = listing.__json__()
        self.assertListEqual(as_json, [0, 1, 2, 3])
        self.assertIsInstance(as_json, list)
