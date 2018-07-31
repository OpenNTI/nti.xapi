#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import has_property

from nti.testing.matchers import verifiably_provides

import unittest

from zope.schema.interfaces import ValidationError

from nti.externalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from nti.xapi.interfaces import IVerb
from nti.xapi.interfaces import ILanguageMap

from nti.xapi.tests import SharedConfiguringTestLayer

from nti.xapi.verb import Verb


class TestVerb(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def data(self):
        return {
            "id": "http://adlnet.gov/expapi/verbs/voided",
            "display": {
                "en-US": "voided"
            }
        }

    def setUp(self):
        self.verb = Verb()
        update_from_external_object(self.verb, self.data)

    def test_bad(self):
        with self.assertRaises(ValidationError):
            verb = Verb()
            update_from_external_object(verb, {'id': 'foio', 'display': 1})

    def test_creation(self):
        verb = self.verb
        assert_that(verb, verifiably_provides(IVerb))
        assert_that(verb,
                    has_property('id', is_('http://adlnet.gov/expapi/verbs/voided')))
        assert_that(verb,
                    has_property('display', verifiably_provides(ILanguageMap)))
        assert_that(verb,
                    has_property('display', has_entry('en-US', 'voided')))

    def test_externalization(self):
        verb = self.verb
        assert_that(to_external_object(verb), is_(self.data))

    def test_internalization(self):
        verb = self.verb
        assert_that(verb,
                    has_property('id', is_('http://adlnet.gov/expapi/verbs/voided')))
        assert_that(verb,
                    has_property('display', verifiably_provides(ILanguageMap)))
        assert_that(verb,
                    has_property('display', has_entry('en-US', 'voided')))
