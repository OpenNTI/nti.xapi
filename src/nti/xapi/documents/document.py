#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.schema.eqhash import EqHash

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

from nti.xapi.documents.interfaces import IDocument
from nti.xapi.documents.interfaces import IStateDocument
from nti.xapi.documents.interfaces import IActivityProfileDocument

logger = __import__('logging').getLogger(__name__)


@EqHash('id')
@interface.implementer(IDocument)
class Document(SchemaConfigured):
    createDirectFieldProperties(IDocument)


@interface.implementer(IStateDocument)
class StateDocument(Document):
    createDirectFieldProperties(IStateDocument)


@interface.implementer(IActivityProfileDocument)
class ActivityProfileDocument(Document):
    createDirectFieldProperties(IActivityProfileDocument)