#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_entries
from hamcrest import has_entry
from hamcrest import has_key
from hamcrest import is_not
does_not = is_not


import unittest

from zope.schema.interfaces import ValidationError

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IActivity
from ..interfaces import IActivityDefinition

from ..activity import Activity
from ..activity import ActivityDefinition
       
class TestActivityDefinition(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def setUp(self):

        self.data = {
            "extensions": {
                "http://example.com/profiles/meetings/activitydefinitionextensions/room": {"name": "Kilby", "id" : "http://example.com/rooms/342"}
            },
            "name": {
                "en-GB": "example meeting",
                "en-US": "example meeting"
            },
            "description": {
                "en-GB": "An example meeting that happened on a specific occasion with certain people present.",
                "en-US": "An example meeting that happened on a specific occasion with certain people present."
            },
            "type": "http://adlnet.gov/expapi/activities/meeting",
            "moreInfo": "http://virtualmeeting.example.com/345256"
        }

        self.ad = IActivityDefinition(self.data)

    def validate_ad(self, ad):
        assert_that(ad, verifiably_provides(IActivityDefinition))
        assert_that(ad.type, is_('http://adlnet.gov/expapi/activities/meeting'))
        assert_that(ad.moreInfo, is_('http://virtualmeeting.example.com/345256'))
        assert_that(ad.name, has_entries("en-GB", "example meeting",
                                         "en-US", "example meeting"))
        assert_that(ad.description, has_entries("en-GB",
                                                "An example meeting that happened on a specific occasion with certain people present.",
                                                "en-US",
                                                "An example meeting that happened on a specific occasion with certain people present."))

        assert_that(ad.extensions, has_entry("http://example.com/profiles/meetings/activitydefinitionextensions/room",
                                             has_entries("name", "Kilby",
                                                         "id" , "http://example.com/rooms/342")))

    def test_creation(self):
        self.validate_ad(self.ad)

    def test_externalization(self):
        assert_that(to_external_object(self.ad), is_(self.data))

    def test_internalization(self):
        ad = ActivityDefinition()
        update_from_external_object(ad, self.data)

        self.validate_ad(self.ad)


class TestActivity(TestActivityDefinition):

    layer = SharedConfiguringTestLayer

    def setUp(self):

        self.data = {
            "id": "http://www.example.com/meetings/occurances/34534",
            "definition": {
                "extensions": {
                    "http://example.com/profiles/meetings/activitydefinitionextensions/room": {"name": "Kilby", "id" : "http://example.com/rooms/342"}
                },
                "name": {
                    "en-GB": "example meeting",
                    "en-US": "example meeting"
                },
                "description": {
                    "en-GB": "An example meeting that happened on a specific occasion with certain people present.",
                    "en-US": "An example meeting that happened on a specific occasion with certain people present."
                },
                "type": "http://adlnet.gov/expapi/activities/meeting",
                "moreInfo": "http://virtualmeeting.example.com/345256"
            },
            "objectType": "Activity"
        }

        self.activity = IActivity(self.data)

    def validate_activity(self, activity):
        assert_that(activity, verifiably_provides(IActivity))
        assert_that(activity.id, is_('http://www.example.com/meetings/occurances/34534'))
        assert_that(activity.objectType, is_('Activity'))
        self.validate_ad(activity.definition)

    def test_creation(self):
        self.validate_activity(self.activity)

    def test_externalization(self):
        assert_that(to_external_object(self.activity), is_(self.data))

    def test_internalization(self):
        activity = Activity()
        update_from_external_object(activity, self.data)

        self.validate_activity(self.activity)

    def test_ntiid_based_id(self):
        activity = Activity(id='tag:nextthought.com,2011-10:system-OID-0x3b07:5573657273:PeNxy42MYYR')
        external = to_external_object(activity)

        assert_that(external, has_entry('id', 'tag:nextthought.com,2011-10:system-OID-0x3b07:5573657273:PeNxy42MYYR'))
        assert_that(external, does_not(has_key('ID')))
        assert_that(external, does_not(has_key('OID')))
        assert_that(external, does_not(has_key('NTIID')))
