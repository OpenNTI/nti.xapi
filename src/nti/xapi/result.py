#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import isodate

from zope import interface

from nti.externalization.internalization import update_from_external_object

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

from .io_datastructures import XAPIBaseIO

from .interfaces import IResult
from .interfaces import IScore


def _score_factory(ext):
    score = Score()
    update_from_external_object(score, ext)
    return score


@interface.implementer(IScore)
class Score(SchemaConfigured):

    createDirectFieldProperties(IScore)


def _result_factory(ext):
    result = Result()
    update_from_external_object(result, ext)
    return result


@interface.implementer(IResult)
class Result(SchemaConfigured):

    createDirectFieldProperties(IResult)


class ResultIO(XAPIBaseIO):

    def updateFromExternalObject(self, parsed, *args, **kwargs):  # pylint: disable: arguments-differ
        duration = parsed.pop('duration', None)
        if duration:
            parsed['duration'] = isodate.parse_duration(duration)
        return super(ResultIO, self).updateFromExternalObject(parsed, *args, **kwargs)

    def toExternalObject(self, *args, **kwargs):
        duration = getattr(self._ext_self, 'duration', None)
        result = super(ResultIO, self).toExternalObject(*args, **kwargs)
        if duration:
            result['duration'] = isodate.duration_isoformat(duration)
        return result
