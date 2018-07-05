#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from nti.externalization.internalization import update_from_external_object

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

from nti.xapi.interfaces import IActivity
from nti.xapi.interfaces import IActivityDefinition

logger = __import__('logging').getLogger(__name__)


@component.adapter(dict)
@interface.implementer(IActivityDefinition)
def _activity_definition_factory(ext):
    activity_def = ActivityDefinition()
    update_from_external_object(activity_def, ext)
    return activity_def


@interface.implementer(IActivityDefinition)
class ActivityDefinition(SchemaConfigured):
    createDirectFieldProperties(IActivityDefinition)


@component.adapter(dict)
@interface.implementer(IActivity)
def _activity_factory(ext):
    activity = Activity()
    update_from_external_object(activity, ext)
    return activity


@interface.implementer(IActivity)
class Activity(SchemaConfigured):
    createDirectFieldProperties(IActivity)

    objectType = 'Activity'
