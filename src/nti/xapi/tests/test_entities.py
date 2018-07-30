#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import has_length
from hamcrest import is_
from hamcrest import none


import unittest

from zope.schema.interfaces import ValidationError

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IAgent
from ..interfaces import IAgentAccount
from ..interfaces import IIdentifiedGroup
from ..interfaces import IAnonymousGroup

from ..entities import Agent
from ..entities import AgentAccount
from ..entities import _group_factory
from ..entities import _entity_factory


class TestAgentAccount(unittest.TestCase):

    def test_iface(self):
        account = AgentAccount()
        assert_that(account, verifiably_provides(IAgentAccount))

    def test_init(self):
        account = AgentAccount(name='foo', homePage='http://google.com')
        assert_that(account.name, is_('foo'))
        assert_that(account.homePage, is_('http://google.com'))

    def test_required(self):
        account = AgentAccount()
        with self.assertRaises(ValidationError):
            account.name = None

        with self.assertRaises(ValidationError):
            account.homePage = None

    def test_name_length(self):
        account = AgentAccount()
        with self.assertRaises(ValidationError):
            account.name = ''

    def test_valid_homepage(self):
        account = AgentAccount()
        with self.assertRaises(ValidationError):
            account.homePage = 'foo'


class TestAgentAccountIO(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def data(self):
        return {
            "homePage": "http://www.example.com",
            "name": "1625378"
        }

    def test_to_external_object(self):
        account = AgentAccount(**self.data)
        assert_that(to_external_object(account), self.data)

    def test_update_from_external(self):
        account = AgentAccount()
        update_from_external_object(account, self.data)

        assert_that(account.name, is_(self.data['name']))
        assert_that(account.homePage, is_(self.data['homePage']))


class TestAgent(unittest.TestCase):

    def test_iface(self):
        agent = Agent()
        assert_that(agent, verifiably_provides(IAgent))

    def test_object_type(self):
        agent = Agent()
        assert_that(agent.objectType, is_('Agent'))

    def test_init(self):
        agent = Agent(name='test', mbox='mailto:test@test.com', mbox_sha1sum='test', openid='http://toby.openid.example.org/',
                      account=AgentAccount(name="test", homePage="http://test.com"))

        assert_that(agent.objectType, is_('Agent'))
        assert_that(agent.name,  is_('test'))
        assert_that(agent.mbox,  is_('mailto:test@test.com'))
        assert_that(agent.mbox_sha1sum,  is_('test'))
        assert_that(agent.openid,  is_('http://toby.openid.example.org/'))

        assert_that(agent.account.name, is_('test'))
        assert_that(agent.account.homePage, is_('http://test.com'))

    def test_empty_name_raises(self):
        with self.assertRaises(ValidationError):
            Agent(name='')

    def test_empty_mbox_raises(self):
        with self.assertRaises(ValidationError):
            Agent(name='test', mbox='')

    def test_empty_sha_raises(self):
        with self.assertRaises(ValidationError):
            Agent(name='test', mbox='mailto:test@test.com', mbox_sha1sum='')

    def test_empty_open_id(self):
        with self.assertRaises(ValidationError):
            Agent(name='test', mbox='mailto:test@test.com', mbox_sha1sum='test', openid='')


class TestAgentIO(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def basic_agent(self):
        return {
	    "objectType": "Agent",
	    "mbox":"mailto:test@example.com"
        }

    @property
    def account_agent(self):
        return {
	    "objectType": "Agent",
	    "account": {
	        "homePage": "http://www.example.com",
	        "name": "1625378"
	    }
        }


    def test_basic_external(self):
        agent = Agent()
        update_from_external_object(agent, self.basic_agent)
        assert_that(to_external_object(agent), is_(self.basic_agent))

    def test_basic_internalization(self):
        agent = Agent()
        update_from_external_object(agent, self.basic_agent)
        assert_that(agent.mbox, is_(self.basic_agent['mbox']))

    def test_nested_externaliation(self):
        agent = Agent()
        update_from_external_object(agent, self.account_agent)
        assert_that(to_external_object(agent), is_(self.account_agent))

    def test_nested_internalization(self):
        agent = Agent()
        update_from_external_object(agent, self.account_agent)

        assert_that(agent.account, verifiably_provides(IAgentAccount))
        assert_that(agent.account.name, is_('1625378'))
        assert_that(agent.account.homePage, is_('http://www.example.com'))

    def test_as_entity(self):
        agent = _entity_factory(self.basic_agent)
        update_from_external_object(agent, self.basic_agent)
        assert_that(agent, verifiably_provides(IAgent))
        assert_that(to_external_object(agent), is_(self.basic_agent))


class TestGroup(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def identified_group(self):
        return {
            "name": "Team PB",
            "mbox": "mailto:teampb@example.com",
            "member": [
                {
                    "name": "Andrew Downes",
                    "account": {
                        "homePage": "http://www.example.com",
                        "name": "13936749"
                    },
                    "objectType": "Agent"
                },
                {
                    "name": "Toby Nichols",
                    "openid": "http://toby.openid.example.org/",
                    "objectType": "Agent"
                },
                {
                    "name": "Ena Hills",
                    "mbox_sha1sum": "ebd31e95054c018b10727ccffd2ef2ec3a016ee9",
                    "objectType": "Agent"
                }
            ],
            "objectType": "Group"
        }

    @property
    def anon_group(self):

        return {
	    "objectType" : "Group",
	    "member": [
		{
		    "account": {
			"homePage":"http://example.com/xAPI/OAuth/Token",
			"name":"oauth_consumer_x75db"
		    },
                    "objectType": "Agent"
		},
		{
		    "mbox":"mailto:bob@example.com",
                    "objectType": "Agent"
		}
	    ]
        }



    def test_as_group(self):
        ig = _group_factory(self.identified_group)
        update_from_external_object(ig, self.identified_group)
        assert_that(ig, verifiably_provides(IIdentifiedGroup))

        ag = _group_factory(self.anon_group)
        update_from_external_object(ig, self.identified_group)
        assert_that(ag, verifiably_provides(IAnonymousGroup))

    def test_as_entity(self):
        ig = _entity_factory(self.identified_group)
        update_from_external_object(ig, self.identified_group)
        assert_that(ig, verifiably_provides(IIdentifiedGroup))

        ag = _entity_factory(self.anon_group)
        update_from_external_object(ig, self.identified_group)
        assert_that(ag, verifiably_provides(IAnonymousGroup))

    def test_identified_io(self):
        ig = _entity_factory(self.identified_group)
        update_from_external_object(ig, self.identified_group)
        assert_that(to_external_object(ig), is_(self.identified_group))

        assert_that(ig.name, is_(self.identified_group['name']))
        assert_that(ig.mbox, is_(self.identified_group['mbox']))
        assert_that(ig.member, has_length(3))

        for member in ig.member:
            assert_that(member, verifiably_provides(IAgent))

        assert_that(ig.member[0].name, is_('Andrew Downes'))

    def test_anonymous_io(self):
        ag = _entity_factory(self.anon_group)
        update_from_external_object(ag, self.anon_group)
        assert_that(to_external_object(ag), is_(self.anon_group))

        assert_that(ag.name, is_(none()))
        assert_that(ag.member, has_length(2))

        for member in ag.member:
            assert_that(member, verifiably_provides(IAgent))

        assert_that(ag.member[0].account.name, is_('oauth_consumer_x75db'))
