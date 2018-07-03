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

from nti.xapi.documents.document import Document

from nti.xapi.documents.interfaces import IStateDocument

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IStateDocument)
class StateDocument(Document):
    createDirectFieldProperties(IStateDocument)
