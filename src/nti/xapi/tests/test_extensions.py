#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_entry
from hamcrest import has_length

import unittest

from zope.schema.interfaces import ValidationError

from nti.testing.matchers import verifiably_provides

from nti.externalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IExtensions

from ..extensions import Extensions


class TestExtensions(unittest.TestCase):

    def test_implements(self):
        assert_that(Extensions(), verifiably_provides(IExtensions))

    def test_extensions(self):
        exts = Extensions()
        assert_that(exts, has_length(0))

        exts['https://foo.com/a'] = 10
        assert_that(exts, has_length(1))
        assert_that(exts, has_entry('https://foo.com/a', 10))

    def test_invalid_key(self):
        exts = Extensions()
        with self.assertRaises(ValidationError):
            exts['1'] = 1

    def test_takes_dict(self):
        exts = Extensions({'https://foo.com/a': 10})
        assert_that(exts, has_entry('https://foo.com/a', 10))



class TestExtensionsIO(TestExtensions):

    layer = SharedConfiguringTestLayer

    def setUp(self):
        self.data = {
            'https://foo.com/string': 'bar',
            'https://foo.com/int': 10
        }

    def test_from_external_object(self):
        exts = Extensions()
        update_from_external_object(exts, self.data)

        assert_that(exts, has_entry('https://foo.com/string', 'bar'))
        assert_that(exts, has_entry('https://foo.com/int', 10))

    def test_to_external_object(self):
        exts = Extensions(self.data)
        external = to_external_object(exts)
        assert_that(external, is_(self.data))
