#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import contains
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_property

import unittest

from nti.testing.matchers import verifiably_provides

from nti.externalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from nti.xapi.about import About

from nti.xapi.extensions import Extensions

from nti.xapi.interfaces import Version
from nti.xapi.interfaces import IExtensions

from nti.xapi.tests import SharedConfiguringTestLayer


class TestAbout(unittest.TestCase):

    def test_defaults(self):
        a = About()
        assert_that(a, has_property('version', contains(Version.latest)))

    def test_version_init(self):
        about = About(version=['1.0.1', '1.0.0'])
        assert_that(about, has_property('version', contains('1.0.1', '1.0.0')))

    def test_takes_exts(self):
        about = About(version=['1.0.1', '1.0.0'])
        about.extensions = Extensions({'https://foo.com/a': 1})
        assert_that(about.extensions, contains('https://foo.com/a'))


class TestAboutIO(TestAbout):

    layer = SharedConfiguringTestLayer

    def setUp(self):
        self.data = {
            'version': ['1.0.0'],
            'extensions': {
                'http://www.example.com/ext/a': 'a',
                'http://www.example.com/ext/b': 'b'
            },
        }

    def test_from_external_object(self):
        about = About()
        update_from_external_object(about, self.data)

        assert_that(about, has_property('version', contains('1.0.0')))
        assert_that(about.extensions, has_entries('http://www.example.com/ext/a', 'a',
                                                  'http://www.example.com/ext/b', 'b'))

        assert_that(about.extensions, verifiably_provides(IExtensions))

    def test_to_external_object(self):
        about = About(version=['1.0.0'])
        about.extensions = Extensions(self.data['extensions'])

        external = to_external_object(about)
        assert_that(external, is_(self.data))
