#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.externalization.interfaces import IInternalObjectIO

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IAbout


@interface.implementer(IAbout)
class About(SchemaConfigured):

    createDirectFieldProperties(IAbout)
        
