#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_
from hamcrest import instance_of
from hamcrest import contains

import unittest

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IAbout
from ..interfaces import Version

from ..about import About

from ..extensions import Extensions

class TestAbout(unittest.TestCase):
    
    def test_defaults(self):
        a = About()
        assert_that(a.version, contains(Version.latest))

    def test_version_init(self):
        about = About(version=['1.0.1', '1.0.0'])
        assert_that(about.version, contains('1.0.1', '1.0.0'))

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
        pass

    def test_to_external_object(self):
        about = About(version=['1.0.0'])
        about.extensions = Extensions(self.data['extensions'])

        external = to_external_object(about)
        assert_that(external, is_(self.data))
