#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_entry


import unittest

from zope.schema.interfaces import ValidationError

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import ILanguageMap
from ..interfaces import IVerb

from ..verb import Verb
       
class TestVerb(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def setUp(self):

        self.data = {
	    "id":"http://adlnet.gov/expapi/verbs/voided",
	    "display":{
		"en-US":"voided"
	    }
	}

    def test_bad(self):
        with self.assertRaises(ValidationError):
            verb = IVerb({'id': 'foio', 'display': 1})

    def test_creation(self):
        verb = IVerb(self.data)

        assert_that(verb, verifiably_provides(IVerb))

        assert_that(verb.id, is_('http://adlnet.gov/expapi/verbs/voided'))
        assert_that(verb.display, verifiably_provides(ILanguageMap))

        assert_that(verb.display, has_entry('en-US', 'voided'))

    def test_externalization(self):
        verb = IVerb(self.data)
        assert_that(to_external_object(verb), is_(self.data))

    def test_internalization(self):
        verb = Verb()
        update_from_external_object(verb, self.data)
        assert_that(verb.id, is_('http://adlnet.gov/expapi/verbs/voided'))
        assert_that(verb.display, verifiably_provides(ILanguageMap))

        assert_that(verb.display, has_entry('en-US', 'voided'))
