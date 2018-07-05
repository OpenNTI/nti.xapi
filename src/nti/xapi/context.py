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

from nti.xapi.interfaces import IContext
from nti.xapi.interfaces import IContextActivities

logger = __import__('logging').getLogger(__name__)


@component.adapter(dict)
@interface.implementer(IContextActivities)
def _context_activity_factory(ext):
    cas = ContextActivities()
    update_from_external_object(cas, ext)
    return cas


@interface.implementer(IContextActivities)
class ContextActivities(SchemaConfigured):
    createDirectFieldProperties(IContextActivities)


@component.adapter(dict)
@interface.implementer(IContext)
def _context_factory(ext):
    context = Context()
    update_from_external_object(context, ext)
    return context


@interface.implementer(IContext)
class Context(SchemaConfigured):
    createDirectFieldProperties(IContext)
