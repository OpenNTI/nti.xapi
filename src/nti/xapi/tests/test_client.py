#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import os

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that

import codecs
import unittest

import fudge

from nti.xapi.client import LRSClient

from nti.xapi.tests import SharedConfiguringTestLayer


class TestClient(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def get_client(self):
        client = LRSClient("https://lrs.io")
        return client

    @property
    def about_file(self):
        path = os.path.join(os.path.dirname(__file__),
                            "data", "about.json")
        return path

    @fudge.patch('requests.Session.get')
    def test_get_accounts(self, mock_ss):
        with codecs.open(self.about_file, "r", "UTF-8") as fp:
            data = fp.read()

        # success
        data = fudge.Fake().has_attr(text=data).has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        client = self.get_client()
        about = client.about()
        assert_that(about, is_not(none()))

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=403)
        mock_ss.is_callable().returns(data)

        about = client.about()
        assert_that(about, is_(none()))
