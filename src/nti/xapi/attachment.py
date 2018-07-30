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

from nti.xapi.interfaces import IAttachment

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IAttachment)
class Attachment(SchemaConfigured):

    __external_can_create__ = True
    
    createDirectFieldProperties(IAttachment)
