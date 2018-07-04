#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.externalization.internalization import update_from_external_object

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IActivity
from .interfaces import IActivityDefinition


def _activity_definition_factory(ext):
    activity_def = ActivityDefinition()
    update_from_external_object(activity_def, ext)
    return activity_def


@interface.implementer(IActivityDefinition)
class ActivityDefinition(SchemaConfigured):

    createDirectFieldProperties(IActivityDefinition)


def _activity_factory(ext):
    activity = Activity()
    update_from_external_object(activity, ext)
    return activity

@interface.implementer(IActivity)
class Activity(SchemaConfigured):

    objectType = 'Activity'

    createDirectFieldProperties(IActivity)
