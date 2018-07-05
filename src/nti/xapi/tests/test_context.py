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
from hamcrest import has_length
from hamcrest import none


import unittest

from zope.schema.interfaces import ValidationError

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IActivity
from ..interfaces import IContext
from ..interfaces import IContextActivities

from ..context import Context
from ..context import ContextActivities
       
class TestContextActivities(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def setUp(self):

        self.data = {
            "parent": [
                {
                    "id": "http://www.example.com/meetings/series/267",
                    "objectType": "Activity"
                }
            ],
            "category": [
                {
                    "id": "http://www.example.com/meetings/categories/teammeeting",
                    "objectType": "Activity",
                    "definition": {
			"name": {
			    "en": "team meeting"
			},
			"description": {
			    "en": "A category of meeting used for regular team meetings."
			},
			"type": "http://example.com/expapi/activities/meetingcategory"
		    }
                }
            ],
            "other": [
                {
                    "id": "http://www.example.com/meetings/occurances/34257",
                    "objectType": "Activity"
                },
                {
                    "id": "http://www.example.com/meetings/occurances/3425567",
                    "objectType": "Activity"
                }
            ]
        }

        self.ca = IContextActivities(self.data)

    def validate_context_activities(self, ca):
        assert_that(ca, verifiably_provides(IContextActivities))
        assert_that(ca.parent, has_length(1))
        assert_that(ca.category, has_length(1))
        assert_that(ca.other, has_length(2))
        assert_that(ca.grouping, none())

        for key in ('parent', 'category', 'other'):
            for activity in getattr(ca, key):
                assert_that(activity, verifiably_provides(IActivity))
        
    def test_creation(self):
        self.validate_context_activities(self.ca)

    def test_externalization(self):
        assert_that(to_external_object(self.ca), is_(self.data))

    def test_internalization(self):
        ca = ContextActivities()
        update_from_external_object(ca, self.data)

        self.validate_context_activities(self.ca)
