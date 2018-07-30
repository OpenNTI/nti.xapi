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

from nti.xapi.activity import Activity

from nti.xapi.entities import Agent
from nti.xapi.entities import _group_factory

from nti.xapi.datastructures import XAPIBaseIO

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import IGroup
from nti.xapi.interfaces import IActivity
from nti.xapi.interfaces import IStatement
from nti.xapi.interfaces import IStatementRef
from nti.xapi.interfaces import ISubStatement
from nti.xapi.interfaces import IStatementBase
from nti.xapi.interfaces import IStatementResult

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IStatementRef)
class StatementRef(SchemaConfigured):

    __external_can_create__= True

    createDirectFieldProperties(IStatementRef)

    objectType = 'StatementRef'


@interface.implementer(IStatementBase)
class StatementBase(object):

    __external_can_create__ = True

    createDirectFieldProperties(IStatementBase)


@interface.implementer(ISubStatement)
class SubStatement(SchemaConfigured, StatementBase):

    createDirectFieldProperties(ISubStatement)

    objectType = 'SubStatement'


@interface.implementer(IStatement)
class Statement(SchemaConfigured, StatementBase):

    createDirectFieldProperties(IStatement)


@interface.implementer(IStatementResult)
class StatementResult(SchemaConfigured):

    __external_can_create__ = True

    createDirectFieldProperties(IStatementResult)

    def __iter__(self):
        # pylint: disable=no-member
        return iter(self.statements or ())


OBJECT_FACTORIES = {
    'Agent': lambda x: Agent(),
    'Group': _group_factory,
    'Activity': lambda x: Activity(),
    'Statement': lambda x: Statement(),
    'StatementRef': lambda x: StatementRef(),
    'SubStatement': lambda x: SubStatement(),
}

def _statement_object_factory(ext):
    object_type = ext.get('objectType', 'Activity')
    return OBJECT_FACTORIES.get(object_type, None)(ext)
