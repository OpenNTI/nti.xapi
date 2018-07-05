#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.externalization.internalization import update_from_external_object

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IContext
from .interfaces import IContextActivities


def _context_activity_factory(ext):
    cas = ContextActivities()
    update_from_external_object(cas, ext)
    return cas


@interface.implementer(IContextActivities)
class ContextActivities(SchemaConfigured):

    createDirectFieldProperties(IContextActivities)


def _context_factory(ext):
    context = Context()
    update_from_external_object(context, ext)
    return context


@interface.implementer(IContext)
class Context(SchemaConfigured):

    createDirectFieldProperties(IContext)
