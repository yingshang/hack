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

from requests.auth import HTTPBasicAuth
from requests_futures.sessions import FuturesSession
from six.moves.urllib.parse import quote

from .models import hydrate_object, hydrate_objects
from .lazy_listing import LazyListing
from . import __version__


def encode_params(obj, keys=()):
    if isinstance(obj, dict):
        # key[bar]=1&key[baz]=2
        return "&".join(encode_params(val, keys + (key,)) for key, val in obj.items())
    # key[foo][]=1&key[foo][]=2
    elif isinstance(obj, (list, tuple)):
        return "&".join(encode_params(val, keys + ("",)) for val in obj)
    # `obj` is just a value, key=1
    else:
        encoded_keys = ""
        for depth, key in enumerate(keys):
            # All keys but top-level keys should be in brackets, i.e.
            # `key[foo]=1`, not `[key][foo]=1`
            encoded_keys += key if depth == 0 else "[" + key + "]"
        return quote(encoded_keys) + "=" + quote(obj)


class HackerOneClient(object):
    BASE_URL = "https://api.hackerone.com/v1"
    REQUEST_HEADERS = {
        "User-Agent": "HackerOne Python Client v" + __version__,
    }

    def __init__(self, identifier, token):
        self.identifier = identifier
        self.token = token
        self._init_session()

    def _init_session(self):
        self.s = FuturesSession()
        self.s.headers.update(self.REQUEST_HEADERS)
        self.s.auth = HTTPBasicAuth(self.identifier, self.token)

    def make_request(self, url, params=None, data=None, method=None):
        if method is None:
            method = "GET"
        if not url.startswith("http"):
            url = self.BASE_URL + url
        if isinstance(params, dict):
            params = encode_params(params)

        return self.s.request(method, url, params=params, data=data)

    def request_json(self, url, params=None, data=None, method=None):
        r = self.make_request(url, params, data, method).result()
        r.raise_for_status()
        return r.json()

    def request_object(self, url, params=None, data=None, method=None):
        data = self.request_json(url, params, data, method)["data"]
        # If we're fetching a single object make sure that consumers
        # know this is the canonical version
        data["_canonical"] = True
        return hydrate_object(data, self)

    def request_paginated_objects(self, url, params=None, yield_pages=False):
        future = self.make_request(url, params)
        res_iter = self._request_paginated_inner(url, future, yield_pages)
        return LazyListing(res_iter)

    def _request_paginated_inner(self, url, future, yield_pages):
        while url:
            resp = future.result()
            resp.raise_for_status()
            parsed = resp.json()
            url = parsed["links"].get('next')
            if url:
                future = self.make_request(url)

            hydrated_objs = hydrate_objects(parsed["data"], self)
            if yield_pages:
                yield hydrated_objs
            else:
                for obj in hydrated_objs:
                    yield obj

    def get_resource(self, rsrc_type, obj_id):
        return rsrc_type.get(self, obj_id)

    def find_resources(self, rsrc_type, sort=None, yield_pages=False, **kwargs):
        """Find instances of `rsrc_type` that match the filter in `**kwargs`"""
        return rsrc_type.find(self, sort=sort, yield_pages=yield_pages, **kwargs)
