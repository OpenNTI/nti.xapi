#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import instance_of
from hamcrest import has_entries

import unittest

from nti.testing.matchers import verifiably_provides

from nti.externalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from nti.xapi.interfaces import ILanguageMap

from nti.xapi.language_map import LanguageMap

from nti.xapi.tests import SharedConfiguringTestLayer


class TestLanguageMap(unittest.TestCase):

    def test_implements(self):
        assert_that(LanguageMap(), verifiably_provides(ILanguageMap))

    def test_InitNoArgs(self):
        lmap = LanguageMap()
        assert_that(lmap, is_({}))
        assert_that(lmap, instance_of(LanguageMap))

    def test_InitEmpty(self):
        lmap = LanguageMap({})
        assert_that(lmap, is_({}))
        assert_that(lmap, instance_of(LanguageMap))

    def test_InitExceptionNotMap(self):
        with self.assertRaises(ValueError):
            LanguageMap('not map')

    def test_InitExceptionBadMap(self):
        with self.assertRaises(ValueError):
            LanguageMap({"bad map"})

    def test_InitExceptionNestedObject(self):
        with self.assertRaises(TypeError):
            LanguageMap({"en-US": {"nested": "object"}})

    def test_InitDict(self):
        lmap = LanguageMap(
            {"en-US": "US-test", "fr-CA": "CA-test", "fr-FR": "FR-test"}
        )
        self.mapVerificationHelper(lmap)

    def test_InitLanguageMap(self):
        arg = LanguageMap(
            {"en-US": "US-test", "fr-CA": "CA-test", "fr-FR": "FR-test"}
        )
        lmap = LanguageMap(arg)
        self.mapVerificationHelper(lmap)

    def test_InitUnpack(self):
        obj = {"en-US": "US-test", "fr-CA": "CA-test", "fr-FR": "FR-test"}
        lmap = LanguageMap(**obj)
        self.mapVerificationHelper(lmap)

    def test_InitUnpackExceptionNestedObject(self):
        obj = {"en-US": {"nested": "object"}}
        with self.assertRaises(TypeError):
            LanguageMap(**obj)

    def test_getItemException(self):
        lmap = LanguageMap()
        with self.assertRaises(KeyError):
            _ = lmap['en-Anything']

    def test_setItem(self):
        lmap = LanguageMap()
        lmap['en-US'] = 'US-test'
        lmap['fr-CA'] = 'CA-test'
        lmap['fr-FR'] = 'FR-test'
        self.mapVerificationHelper(lmap)

    def test_setItemException(self):
        lmap = LanguageMap()
        with self.assertRaises(TypeError):
            lmap['en-US'] = {"test": "notstring"}
        assert_that(lmap, is_({}))

    def mapVerificationHelper(self, lmap):
        assert_that(lmap, instance_of(LanguageMap))
        assert_that(lmap, verifiably_provides(ILanguageMap))
        assert_that(len(lmap), 3)
        assert_that(lmap, has_entries('en-US', 'US-test',
                                      'fr-CA', 'CA-test',
                                      'fr-FR', 'FR-test'))


class TestLanguageMapIO(TestLanguageMap):

    layer = SharedConfiguringTestLayer

    def test_from_external_object(self):
        lm = LanguageMap()
        update_from_external_object(
            lm, {"en-US": "US-test", "fr-CA": "CA-test", "fr-FR": "FR-test"}
        )
        self.mapVerificationHelper(lm)

    def test_to_external_object(self):
        lm = LanguageMap(
            {"en-US": "US-test", "fr-CA": "CA-test", "fr-FR": "FR-test"}
        )
        ext = to_external_object(lm)
        assert_that(ext,
                    is_({"en-US": "US-test", "fr-CA": "CA-test", "fr-FR": "FR-test"}))
