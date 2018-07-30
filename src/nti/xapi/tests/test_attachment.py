#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_entry
from hamcrest import has_properties

import unittest

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IAttachment

from ..attachment import Attachment

class TestAttachment(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def data(self):
        return {
            "usageType": "http://adlnet.gov/expapi/attachments/signature",
            "display": { "en-US": "Signature" },
            "description": { "en-US": "A test signature" },
            "contentType": "application/octet-stream",
            "length": 4235,
            "sha2": "672fa5fa658017f1b72d65036f13379c6ab05d4ab3b6664908d8acf0b6a0c634"
        }

    def setUp(self):
        self.attachment = Attachment()
        update_from_external_object(self.attachment, self.data)

    def validate_attachment(self, attachment):
        assert_that(attachment, verifiably_provides(IAttachment))
        assert_that(attachment, has_properties('usageType', 'http://adlnet.gov/expapi/attachments/signature',
                                               'display', has_entry('en-US', 'Signature'),
                                               'description', has_entry('en-US', 'A test signature'),
                                               'length', 4235,
                                               'contentType', 'application/octet-stream',
                                               'sha2', '672fa5fa658017f1b72d65036f13379c6ab05d4ab3b6664908d8acf0b6a0c634'))

    def test_creation(self):
        self.validate_attachment(self.attachment)

    def test_externalization(self):
        assert_that(to_external_object(self.attachment), is_(self.data))

    def test_internalization(self):
        attachment = Attachment()
        update_from_external_object(attachment, self.data)

        self.validate_attachment(attachment)
