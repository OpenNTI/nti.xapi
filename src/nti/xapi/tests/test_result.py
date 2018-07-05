#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import has_property

from nti.testing.matchers import verifiably_provides

import unittest

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from nti.xapi.interfaces import IScore
from nti.xapi.interfaces import IResult

from nti.xapi.result import Score
from nti.xapi.result import Result

from nti.xapi.tests import SharedConfiguringTestLayer


class TestScore(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def setUp(self):
        self.data = {
            "scaled": 0.95,
            "raw": 95,
            "min": 0,
            "max": 100
        }
        self.score = IScore(self.data)

    def validate_score(self, score):
        assert_that(score, verifiably_provides(IScore))
        assert_that(score,
                    has_property('scaled', is_(.95)))
        assert_that(score,
                    has_property('raw', is_(95)))
        assert_that(score,
                    has_property('min', is_(0)))
        assert_that(score,
                    has_property('max', is_(100)))

    def test_creation(self):
        self.validate_score(self.score)

    def test_externalization(self):
        assert_that(to_external_object(self.score), is_(self.data))

    def test_internalization(self):
        score = Score()
        update_from_external_object(score, self.data)
        self.validate_score(self.score)


class TestResult(TestScore):

    layer = SharedConfiguringTestLayer

    def setUp(self):
        self.data = {
            "score": {
                "scaled": 0.95,
                "raw": 95,
                "min": 0,
                "max": 100
            },
            "success": True,
            "completion": True,
            "duration": "PT20M34S"
        }
        self.result = IResult(dict(self.data))

    def validate_result(self, result):
        assert_that(result, verifiably_provides(IResult))
        self.validate_score(result.score)

    def test_creation(self):
        self.validate_result(self.result)

    def test_externalization(self):
        assert_that(to_external_object(self.result), is_(self.data))

    def test_internalization(self):
        result = Result()
        update_from_external_object(result, dict(self.data))
        self.validate_result(self.result)
