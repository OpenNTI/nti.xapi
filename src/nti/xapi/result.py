#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import isodate

from zope import component
from zope import interface

from nti.externalization.internalization import update_from_external_object

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

from nti.xapi.io_datastructures import XAPIBaseIO

from nti.xapi.interfaces import IScore
from nti.xapi.interfaces import IResult

logger = __import__('logging').getLogger(__name__)


@component.adapter(dict)
@interface.implementer(IScore)
def _score_factory(ext):
    score = Score()
    update_from_external_object(score, ext)
    return score


@interface.implementer(IScore)
class Score(SchemaConfigured):
    createDirectFieldProperties(IScore)


@component.adapter(dict)
@interface.implementer(IResult)
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
            try:
                parsed['duration'] = isodate.parse_duration(duration)
            except TypeError:
                # already a duration
                pass
        return super(ResultIO, self).updateFromExternalObject(parsed, *args, **kwargs)

    def toExternalObject(self, *args, **kwargs):
        duration = getattr(self._ext_self, 'duration', None)
        result = super(ResultIO, self).toExternalObject(*args, **kwargs)
        if duration:
            try:
                result['duration'] = isodate.duration_isoformat(duration)
            except TypeError:
                # not a duration
                result['duration'] = duration
        return result
