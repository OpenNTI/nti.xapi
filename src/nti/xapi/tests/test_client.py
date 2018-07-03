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

    @fudge.patch('requests.Session.get',
                 'nti.xapi.client.update_from_external_object')
    def test_get_about(self, mock_ss, mock_in):
        with codecs.open(self.about_file, "r", "UTF-8") as fp:
            data = fp.read()

        mock_in.is_callable().returns_fake()
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

    @property
    def statement_file(self):
        path = os.path.join(os.path.dirname(__file__),
                            "data", "statement.json")
        return path

    @property
    def statement_result_file(self):
        path = os.path.join(os.path.dirname(__file__),
                            "data", "statement_result.json")
        return path

    @fudge.patch('requests.Session.get')
    def test_get_statement(self, mock_ss):
        with codecs.open(self.statement_file, "r", "UTF-8") as fp:
            data = fp.read()

        # success
        data = fudge.Fake().has_attr(text=data).has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        client = self.get_client()
        result = client.get_statement("86187498f16f")
        assert_that(result, is_not(none()))

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=404)
        mock_ss.is_callable().returns(data)

        result = client.get_statement("notfound")
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.get')
    def test_get_voided_statement(self, mock_ss):
        with codecs.open(self.statement_file, "r", "UTF-8") as fp:
            data = fp.read()

        # success
        data = fudge.Fake().has_attr(text=data).has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        client = self.get_client()
        result = client.get_voided_statement("86187498f16f")
        assert_that(result, is_not(none()))

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=404)
        mock_ss.is_callable().returns(data)

        result = client.get_voided_statement("notfound")
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.put',
                 'nti.xapi.client.to_external_object',
                 'nti.xapi.client.update_from_external_object')
    def test_save_statement(self, mock_ss, mock_ex, mock_in):
        mock_ex.is_callable().returns_fake()
        mock_in.is_callable().returns_fake()

        # success
        data = fudge.Fake().has_attr(text=b'').has_attr(status_code=204)
        mock_ss.is_callable().returns(data)

        statement = fudge.Fake().has_attr(id=b'xxx')
        client = self.get_client()
        result = client.save_statement(statement)
        assert_that(result, is_not(none()))

        data = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.save_statement(statement)
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.post',
                 'nti.xapi.client.to_external_object',
                 'nti.xapi.client.update_from_external_object')
    def test_save_statements(self, mock_ss, mock_ex, mock_in):
        mock_ex.is_callable().returns_fake()
        mock_in.is_callable().returns_fake()

        # success
        data = fudge.Fake().has_attr(text=b'["xxx"]').has_attr(status_code=204)
        mock_ss.is_callable().returns(data)

        statement = fudge.Fake().has_attr(id=b'yyy')
        client = self.get_client()
        result = client.save_statements([statement])
        assert_that(result, is_not(none()))

        data = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.save_statements([statement])
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.get',
                 'nti.xapi.client.to_external_object')
    def test_query_statements(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        with codecs.open(self.statement_result_file, "r", "UTF-8") as fp:
            data = fp.read()

        # success
        data = fudge.Fake().has_attr(text=data).has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        query = {'verb': 1, 'agent': 1, 'ascending': False}
        client = self.get_client()
        result = client.query_statements(query)
        assert_that(result, is_not(none()))

        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.query_statements(query)
        assert_that(result, is_(none()))
