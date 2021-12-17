#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import os

from hamcrest import calling
from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import raises

import codecs
import unittest
from datetime import datetime, timedelta

import fudge

from requests.structures import CaseInsensitiveDict

from nti.xapi.client import LRSClient
from nti.xapi.client import _parse_date as parse_date
from nti.xapi.client import UTC

from nti.xapi.activity import Activity

from nti.xapi.documents.document import StateDocument
from nti.xapi.documents.document import AgentProfileDocument
from nti.xapi.documents.document import ActivityProfileDocument

from nti.xapi.entities import Agent

from nti.xapi.tests import SharedConfiguringTestLayer

from nti.xapi.statement import Statement

from nti.xapi.attachment import Attachment

from nti.externalization import update_from_external_object

from io import StringIO

from requests import HTTPError

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

    def test_client(self):
        assert_that(LRSClient(None).endpoint, is_(None))
        assert_that(LRSClient('').endpoint, is_(''))
        assert_that(LRSClient('a').endpoint, is_('a/'))
        assert_that(LRSClient('a/').endpoint, is_('a/'))

        client = LRSClient(None)
        assert_that(client.endpoint, is_(None))
        assert_that(client.auth, is_(None))

        client = LRSClient('a', auth=('test', 'pwd',))
        assert_that(client.endpoint, is_('a/'))
        assert_that(client.auth, is_(('test', 'pwd')))

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

    # statements

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


    @property
    def attachment(self):
        data = {
            "usageType": "http://adlnet.gov/expapi/attachments/signature",
            "display": {"en-US": "Signature"},
            "description": {"en-US": "A test signature"},
            "contentType": "application/octet-stream",
            "length": 4235,
            "sha2": "672fa5fa658017f1b72d65036f13379c6ab05d4ab3b6664908d8acf0b6a0c634"
        }
        attachment = Attachment()
        update_from_external_object(attachment, data)
        return attachment

    @property
    def statement(self):
        stmt = Statement()
        stmt.id = "7ccd3322-e1a5-411a-a67d-6a735c76f119"
        return stmt


    @fudge.patch('requests.Session.send')
    def test_save_statement(self, mock_ss):

        # success
        data = fudge.Fake().has_attr(status_code=204, text=b'').provides('raise_for_status')
        mock_ss.is_callable().returns(data)
        client = self.get_client()
        stmt = self.statement
        result = client.save_statement(stmt)
        assert_that(result, is_not(none()))

        # success with attachment
        file_like = StringIO("Content for test_save_statements file.")
        attachment = self.attachment
        stmt.attachments = [attachment]
        result = client.save_statement(stmt, {attachment.sha2: file_like})
        assert_that(result, is_not(none()))

        # success with bad attachment
        file_like = StringIO("Content for test_save_statements file.")
        assert_that(calling(client.save_statement).with_args(stmt, {'xxx': file_like}), raises(ValueError))

        # failed
        data = fudge.Fake().has_attr(status_code=422, text=b'Unprocessable Entity')\
            .provides('raise_for_status').raises(HTTPError('website down.'))
        mock_ss.is_callable().returns(data)
        stmt = Statement()
        assert_that(client.save_statement(stmt), is_(none()))

    @fudge.patch('requests.Session.send')
    def test_save_statements(self, mock_ss):

        # success
        data = fudge.Fake().has_attr(text=b'["7ccd3322-e1a5-411a-a67d-6a735c76f119"]')\
            .has_attr(status_code=204).provides('raise_for_status')
        mock_ss.is_callable().returns(data)
        statement = Statement()
        client = self.get_client()
        result = client.save_statements([statement])
        assert_that(result, is_not(none()))

        # failed
        data = fudge.Fake().has_attr(status_code=422, text=b'Unprocessable Entity')\
            .provides('raise_for_status').raises(HTTPError('website down'))
        mock_ss.is_callable().returns(data)
        assert_that(client.save_statements([statement]), is_(none()))

        # failed with attachment
        file_like = StringIO("Content for test_save_statements file.")
        stmt = self.statement
        attachment = self.attachment
        stmt.attachments = [attachment]
        assert_that(client.save_statements([stmt], {attachment.sha2: file_like}), is_(none()))

        # success with bad attachment
        assert_that(calling(client.save_statement).with_args(stmt, {'xxx': file_like}), raises(ValueError))

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

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.query_statements(query)
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.get',)
    def test_more_statements(self, mock_ss):
        with codecs.open(self.statement_result_file, "r", "UTF-8") as fp:
            data = fp.read()

        # success
        data = fudge.Fake().has_attr(text=data).has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        client = self.get_client()
        result = client.more_statements("more/1234")
        assert_that(result, is_not(none()))

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.more_statements("more/1234")
        assert_that(result, is_(none()))

    # states

    @fudge.patch('requests.Session.get',
                 'nti.xapi.client.to_external_object')
    def test_retrieve_state_ids(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        activity = Activity(id='yyy')

        # success
        data = fudge.Fake().has_attr(text=b'["aaa"]').has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        client = self.get_client()
        result = client.retrieve_state_ids(activity, 1, "zzz", "20180522")
        assert_that(result, is_not(none()))

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.retrieve_state_ids(activity, 1, "zzz", "20180522")
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.get',
                 'nti.xapi.client.to_external_object')
    def test_retrieve_state(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')

        headers = CaseInsensitiveDict({
            'etag': 'xyz',
            'content-type': 'msword',
            'last-modified': 'Fri, 18 Jun 2021 22:21:11 GMT'
        })
        agent = Agent()
        activity = Activity(id="myact")

        # success
        response = fudge.Fake().has_attr(content=b'b').has_attr(ok=True).has_attr(headers=headers)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.get_state(activity, agent, 'uuid', 'reg')
        assert_that(result, is_not(none()))
        assert_that(result.content_type, is_('msword'))
        assert_that(result.timestamp.isoformat(), is_('2021-06-18T22:21:11+00:00'))

        # failed
        response = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.get_state(activity, agent, 'uuid')
        assert_that(result, is_(none()))

    # Date parsing lifted from webob.datetime_utils for dealing with http header to datetime conversions
    # https://github.com/Pylons/webob/blob/master/src/webob/datetime_utils.py
    # https://github.com/Pylons/webob/blob/master/tests/test_datetime_utils.py

    def test_UTC(self):
        """Test missing function in _UTC"""
        assert_that(UTC.tzname(datetime.now()), is_("UTC"))
        assert_that(UTC.dst(datetime.now()), is_(timedelta(0)))
        assert_that(UTC.utcoffset(datetime.now()), is_(timedelta(0)))
        assert_that(repr(UTC),is_("UTC"))

    def test_parse_date_invalid(self):
        class Uncooperative:
            def __str__(self):
                raise NotImplementedError

        for date in ["invalid_date", None, 1, "\xc3", Uncooperative()]:
            assert_that(parse_date(date), is_(none()))

    @fudge.patch('requests.Session.put',
                 'nti.xapi.client.to_external_object')
    def test_save_state(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        doc = StateDocument(id="1234",
                            content=b"bytes",
                            activity=Activity(id="act"),
                            agent=Agent(),
                            etag="xyz")

        # success
        response = fudge.Fake().has_attr(status_code=204)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.save_state(doc)
        assert_that(result, is_not(none()))

        # failed
        response = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.save_state(doc)
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.delete',
                 'nti.xapi.client.to_external_object')
    def test_delete_state(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        doc = StateDocument(id="1234",
                            content=b"bytes",
                            activity=Activity(id="act"),
                            agent=Agent(),
                            etag="xyz")

        # success
        response = fudge.Fake().has_attr(status_code=204)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.delete_state(doc)
        assert_that(result, is_(True))

        # failed
        response = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.delete_state(doc)
        assert_that(result, is_(False))

    @fudge.patch('requests.Session.delete',
                 'nti.xapi.client.to_external_object')
    def test_clear_state(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        agent = Agent()
        activity = Activity(id="act")
        # success
        response = fudge.Fake().has_attr(status_code=204)
        mock_ss.is_callable().returns(response)

        # failed
        client = self.get_client()
        result = client.clear_state(activity, agent, "xyz")
        assert_that(result, is_(True))

    # activity profiles

    @fudge.patch('requests.Session.get')
    def test_retrieve_activity_profile_ids(self, mock_ss):
        activity = Activity(id='yyy')
        # success
        data = fudge.Fake().has_attr(text=b'["aaa"]').has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        client = self.get_client()
        result = client.retrieve_activity_profile_ids(activity, "20180522")
        assert_that(result, is_not(none()))

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.retrieve_activity_profile_ids(activity, "20180522")
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.get')
    def test_retrieve_activity_profile(self, mock_ss):
        headers = CaseInsensitiveDict({
            'etag': 'xyz',
            'content-type': 'msword',
            'last-modified': 'Fri, 18 Jun 2021 22:21:11 GMT'
        })
        activity = Activity(id="myact")

        # success
        response = fudge.Fake().has_attr(content=b'b').has_attr(ok=True).has_attr(headers=headers)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.retrieve_activity_profile(activity, 'uuid')
        assert_that(result, is_not(none()))
        assert_that(result.content_type, is_('msword'))
        assert_that(result.timestamp.isoformat(), is_('2021-06-18T22:21:11+00:00'))

        # failed
        response = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.retrieve_activity_profile(activity, 'uuid')
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.put')
    def test_save_activity_profile(self, mock_ss):
        doc = ActivityProfileDocument(id="1234",
                                      content=b"bytes",
                                      activity=Activity(id="act"),
                                      etag="xyz")

        # success
        response = fudge.Fake().has_attr(status_code=204)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.save_activity_profile(doc)
        assert_that(result, is_(doc))

        # failed
        response = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.save_activity_profile(doc)
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.delete')
    def test_delete_activity_profile(self, mock_ss):
        doc = ActivityProfileDocument(id="1234",
                                      content=b"bytes",
                                      activity=Activity(id="act"),
                                      etag="xyz")

        # success
        response = fudge.Fake().has_attr(status_code=204)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.delete_activity_profile(doc)
        assert_that(result, is_(True))

        # failed
        response = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.delete_activity_profile(doc)
        assert_that(result, is_(False))

    # agent profiles

    @fudge.patch('requests.Session.get',
                 'nti.xapi.client.to_external_object')
    def test_retrieve_agent_profile_ids(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        agent = Agent()

        # success
        data = fudge.Fake().has_attr(text=b'["1234"]').has_attr(ok=True)
        mock_ss.is_callable().returns(data)

        client = self.get_client()
        result = client.retrieve_agent_profile_ids(agent, "20180522")
        assert_that(result, is_(list))

        # failed
        data = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(data)
        result = client.retrieve_agent_profile_ids(agent, "20180522")
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.get',
                 'nti.xapi.client.to_external_object')
    def test_retrieve_agent_profile(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')

        headers = CaseInsensitiveDict({
            'etag': 'xyz',
            'content-type': 'msword',
            'last-modified': 'Fri, 18 Jun 2021 22:21:11 GMT'
        })
        agent = Agent()

        # success
        response = fudge.Fake().has_attr(content=b'b').has_attr(ok=True).has_attr(headers=headers)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.retrieve_agent_profile(agent, 'uuid')
        assert_that(result, is_not(none()))
        assert_that(result.content_type, is_('msword'))
        assert_that(result.timestamp.isoformat(), is_('2021-06-18T22:21:11+00:00'))

        # failed
        response = fudge.Fake().has_attr(ok=False).has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.retrieve_agent_profile(agent, 'uuid')
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.put',
                 'nti.xapi.client.to_external_object')
    def test_save_agent_profile(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        doc = AgentProfileDocument(id="1234",
                                   content=b"bytes",
                                   agent=Agent(),
                                   etag="xyz")

        # success
        response = fudge.Fake().has_attr(status_code=204)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.save_agent_profile(doc)
        assert_that(result, is_not(none()))

        # failed
        response = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.save_agent_profile(doc)
        assert_that(result, is_(none()))

    @fudge.patch('requests.Session.delete',
                 'nti.xapi.client.to_external_object')
    def test_delete_agent_profile(self, mock_ss, mock_ex):
        mock_ex.is_callable().returns('ext')
        doc = AgentProfileDocument(id="1234",
                                   content=b"bytes",
                                   agent=Agent(),
                                   etag="xyz")

        # success
        response = fudge.Fake().has_attr(status_code=204)
        mock_ss.is_callable().returns(response)

        client = self.get_client()
        result = client.delete_agent_profile(doc)
        assert_that(result, is_(True))

        # failed
        response = fudge.Fake().has_attr(status_code=422)
        mock_ss.is_callable().returns(response)
        result = client.delete_agent_profile(doc)
        assert_that(result, is_(False))
