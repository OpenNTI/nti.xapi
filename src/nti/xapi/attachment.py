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


@component.adapter(dict)
@interface.implementer(IAttachment)
def _attachment_factory(ext):
    attachment = Attachment()
    update_from_external_object(attachment, ext)
    return attachment


@interface.implementer(IAttachment)
class Attachment(SchemaConfigured):
    createDirectFieldProperties(IAttachment)
