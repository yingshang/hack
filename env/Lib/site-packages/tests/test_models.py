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

import datetime as dt
from decimal import Decimal
import json
import unittest

from h1.models import HackerOneEncoder, hydrate_object, Group, Report, list_model_types
from . import load_resource_blob


class TestModelEncoding(unittest.TestCase):

    def test_serialize_round_trip(self):
        # A model should deserialize to the same JSON as it was
        # originally serialized from
        group_blob = load_resource_blob("group")
        group = hydrate_object(group_blob)
        self.assertIsInstance(group, Group)
        round_trip_group_blob = json.loads(json.dumps(group, cls=HackerOneEncoder))
        self.assertDictEqual(round_trip_group_blob, group_blob)

    def test_serialize_round_trip_list(self):
        group_blob = load_resource_blob("group")
        group = hydrate_object(group_blob)
        group_list = [group, group]
        round_trip_group_list = json.loads(json.dumps(group_list, cls=HackerOneEncoder))
        self.assertEqual(len(round_trip_group_list), 2)
        self.assertDictEqual(round_trip_group_list[0], group_blob)


class TestModelHydration(unittest.TestCase):
    def test_type_mismatch_throws(self):
        with self.assertRaises(AssertionError):
            Report(None, load_resource_blob("group"))

    def test_report_properties(self):
        report = Report(None, load_resource_blob("report"))
        self.assertEqual(report.id, "1337")
        self.assertEqual(report.total_bounty, Decimal("1000.00"))
        self.assertEqual(report.total_payout, Decimal("1100.00"))
        self.assertEqual(report.html_url, "https://hackerone.com/reports/1337")
        self.assertEqual(report.time_to_first_response, dt.timedelta(days=1))
        self.assertEqual(report.time_to_closed, dt.timedelta(days=2))

    def test_hydrate_all_objects(self):
        # Try to hydrate every model we know about from the test resources
        for model_type in list_model_types():
            hydrate_object(load_resource_blob(model_type))


class TestModelSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        group_1_blob = load_resource_blob("group")
        cls.group_1a = hydrate_object(group_1_blob)
        cls.group_1b = hydrate_object(group_1_blob)
        group_2_blob = load_resource_blob("group")
        group_2_blob["id"] = "1338"
        cls.group_2 = hydrate_object(group_2_blob)
        cls.report = hydrate_object(load_resource_blob("report"))

    def test_same_id_equal(self):
        self.assertEqual(self.group_1a, self.group_1b)

    def test_different_id_not_equal(self):
        self.assertNotEqual(self.group_1a, self.group_2)

    def test_different_type_not_equal(self):
        self.assertNotEqual(self.group_1a, self.report)

    def test_different_none_not_equal(self):
        self.assertNotEqual(self.group_1a, None)
