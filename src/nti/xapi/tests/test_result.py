#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_

import isodate

import unittest

from zope.schema.interfaces import ValidationError

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IResult
from ..interfaces import IScore

from ..result import Result
from ..result import Score

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
        assert_that(score.scaled, is_(.95))
        assert_that(score.raw, is_(95))
        assert_that(score.min, is_(0))
        assert_that(score.max, is_(100))
                
    def test_creation(self):
        self.validate_score(self.score)

    def test_externalization(self):
        assert_that(to_external_object(self.score), is_(self.data))

    def test_internalization(self):
        score = Score()
        update_from_external_object(score, self.data)

        self.validate_score(score)

class TestResult(TestScore):

    layer = SharedConfiguringTestLayer

    def setUp(self):
        self.data = {
	    "score":{
	        "scaled": 0.95,
                "raw": 95,
                "min": 0,
                "max": 100
	    },
	    "success": True,
	    "completion": True,
	    "duration": "PT1234S"
	}
        self.result = IResult(dict(self.data))

    def validate_result(self, result):
        assert_that(result, verifiably_provides(IResult))
        assert_that(result.success, is_(True))
        assert_that(result.completion, is_(True))
        assert_that(result.duration, is_(isodate.parse_duration('PT1234S')))

        self.validate_score(result.score)

    def test_creation(self):
        self.validate_result(self.result)

    def test_externalization(self):
        expected = dict(self.data)
        expected_duration = expected.pop('duration')

        external = to_external_object(self.result)
        external_duration = external.pop('duration')

        assert_that(isodate.parse_duration(external_duration), is_(isodate.parse_duration(expected_duration)))
    
        assert_that(external, is_(expected))

    def test_internalization(self):
        result = Result()
        update_from_external_object(result, self.data)

        self.validate_result(result)
