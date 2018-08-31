#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

from nti.xapi.interfaces import IContext
from nti.xapi.interfaces import IContextActivities

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IContextActivities)
class ContextActivities(SchemaConfigured):

    __external_can_create__ = True

    createDirectFieldProperties(IContextActivities)


@interface.implementer(IContext)
class Context(SchemaConfigured):

    __external_can_create__ = True

    createDirectFieldProperties(IContext)
