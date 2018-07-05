#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.externalization.internalization import update_from_external_object

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IAttachment


def _attachment_factory(ext):
    attachment = Attachment()
    update_from_external_object(attachment, ext)
    return attachment


@interface.implementer(IAttachment)
class Attachment(SchemaConfigured):

    createDirectFieldProperties(IAttachment)
