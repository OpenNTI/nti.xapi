#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import has_property

from zope import component

from nti.xapi.interfaces import ILRSClient

import nti.testing.base

LRS_ZCML_STRING = u"""
<configure xmlns="http://namespaces.zope.org/zope"
	xmlns:zcml="http://namespaces.zope.org/zcml"
	xmlns:xapi="http://nextthought.com/ntp/xapi"
	i18n_domain='nti.dataserver'>
	<include package="zope.component" />
	
	<include package="." file="meta.zcml" />
	<xapi:registerLRSClient 
				endpoint="http://nextthought.com/lrs" 
				username="foo" 
				password="bar" />
</configure>
"""


class TestZcml(nti.testing.base.ConfiguringTestBase):

    def test_lrs(self):
        self.configure_string(LRS_ZCML_STRING)
        lrs_client = component.getUtility(ILRSClient)
        assert_that(lrs_client, 
					has_property('endpoint', 'http://nextthought.com/lrs'))
        assert_that(lrs_client, has_property('username', 'foo'))
        assert_that(lrs_client, has_property('password', 'bar'))
        assert_that(lrs_client, has_property('version', '1.0.3'))
