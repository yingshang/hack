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

from collections import OrderedDict
import itertools
import json
import unittest

import requests_mock

from h1.client import encode_params, HackerOneClient
from h1.models import Report
from . import load_resource_blob


class TestParamEncoding(unittest.TestCase):

    def test_simple_val(self):
        # Make sure we use `OrderedDict` so we don't depend on
        # implementation-defined iteration order
        params = encode_params(OrderedDict((
            ("foo", "bar"),
            ("baz", "quux"),
        )))
        self.assertEqual("foo=bar&baz=quux", params)

    def test_list_val(self):
        params = encode_params(OrderedDict((
            ("foo", "bar"),
            ("baz", ("1", "2")),
        )))
        self.assertEqual("foo=bar&baz%5B%5D=1&baz%5B%5D=2", params)

    def test_dict_val(self):
        params = encode_params(OrderedDict((
            ("foo", "bar"),
            ("baz", OrderedDict((
                ("plugh", "foozy"),
                ("quuxy", "bazzy"),
            ))),
        )))
        self.assertEqual("foo=bar&baz%5Bplugh%5D=foozy&baz%5Bquuxy%5D=bazzy", params)


class TestHackerOneClient(unittest.TestCase):

    def test_request_json(self):
        report_blob = load_resource_blob("responses/report")
        client = HackerOneClient("a", "b")
        json_url = HackerOneClient.BASE_URL + "/reports/1"
        with requests_mock.mock() as m:
            m.get(json_url, text=json.dumps(report_blob))

            report_json = client.request_json("/reports/1")
            self.assertDictEqual(report_blob, report_json)
            # Make sure absolute URLs work as well
            report_json = client.request_json(json_url)
            self.assertDictEqual(report_blob, report_json)

    def test_get_resource(self):
        report_text = json.dumps(load_resource_blob("responses/report"))
        with requests_mock.mock() as m:
            m.get(HackerOneClient.BASE_URL + "/reports/1", text=report_text)

            client = HackerOneClient("a", "b")
            report = client.get_resource(Report, 1)
            self.assertEqual(report.title, "XSS in login form")

    def test_find_resources(self):
        listing_text = json.dumps(load_resource_blob("responses/report-list-onepage"))
        with requests_mock.mock() as m:
            filters = {"foo_gt": "bar"}
            filter_str = "filter%5Bprogram%5D%5B%5D=foo&filter%5Bfoo_gt%5D=bar"
            m.get(HackerOneClient.BASE_URL + "/reports?" + filter_str, text=listing_text)

            client = HackerOneClient("a", "b")
            listing = client.find_resources(Report, program=["foo"], **filters)

            # The listing should contain two reports
            self.assertEqual(len(listing), 2)
            self.assertTrue(all(isinstance(r, Report) for r in listing))

    def test_find_resources_yield_pages(self):
        page_one = json.dumps(load_resource_blob("responses/report-list-twopage-0"))
        page_two = json.dumps(load_resource_blob("responses/report-list-twopage-1"))
        with requests_mock.mock() as m:
            filter_str = "filter%5Bprogram%5D%5B%5D=foo"
            m.get(HackerOneClient.BASE_URL + "/reports?" + filter_str, text=page_one)
            m.get(HackerOneClient.BASE_URL + "/reports/nextpage", text=page_two)

            client = HackerOneClient("a", "b")
            listing = client.find_resources(Report, program=["foo"], yield_pages=True)

            # The listing should contain two pages each with one report
            self.assertEqual(len(listing), 2)
            # Flatten the pages into a single page
            all_items = list(itertools.chain(*listing))
            self.assertEqual(len(all_items), 2)
            self.assertTrue(all(isinstance(r, Report) for r in all_items))
