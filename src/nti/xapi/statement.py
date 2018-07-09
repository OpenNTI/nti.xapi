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

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import IGroup
from nti.xapi.interfaces import IActivity
from nti.xapi.interfaces import IStatement
from nti.xapi.interfaces import IStatementRef
from nti.xapi.interfaces import ISubStatement
from nti.xapi.interfaces import IStatementBase
from nti.xapi.interfaces import IStatementResult

from nti.xapi.io_datastructures import XAPIBaseIO

logger = __import__('logging').getLogger(__name__)


@component.adapter(dict)
@interface.implementer(IStatementRef)
def _statement_ref_factory(ext):
    ref = StatementRef()
    update_from_external_object(ref, ext)
    return ref


@interface.implementer(IStatementRef)
class StatementRef(SchemaConfigured):
    createDirectFieldProperties(IStatementRef)

    objectType = 'StatementRef'


@interface.implementer(IStatementBase)
class StatementBase(object):
    createDirectFieldProperties(IStatementBase)


@component.adapter(dict)
@interface.implementer(ISubStatement)
def _sub_statement_factory(ext):
    sub_stmt = SubStatement()
    update_from_external_object(sub_stmt, ext)
    return sub_stmt


@interface.implementer(ISubStatement)
class SubStatement(SchemaConfigured, StatementBase):
    createDirectFieldProperties(ISubStatement)

    objectType = 'SubStatement'


@component.adapter(dict)
@interface.implementer(IStatement)
def _statement_factory(ext):
    stmt = Statement()
    update_from_external_object(stmt, ext)
    return stmt


@interface.implementer(IStatement)
class Statement(SchemaConfigured, StatementBase):
    createDirectFieldProperties(IStatement)


@component.adapter(dict)
@interface.implementer(IStatementResult)
def _statement_result_factory(ext):
    result = StatementResult()
    update_from_external_object(result, ext)
    return result


@interface.implementer(IStatementResult)
class StatementResult(SchemaConfigured):
    createDirectFieldProperties(IStatementResult)

    def __iter__(self):
        # pylint: disable=no-member
        return iter(self.statements or ())


OBJECT_IFACE_MAP = {
    'Agent': IAgent,
    'Group': IGroup,
    'Activity': IActivity,
    'Statement': IStatement,
    'StatementRef': IStatementRef,
    'SubStatement': ISubStatement,
}


class StatementIO(XAPIBaseIO):

    def updateFromExternalObject(self, parsed, *args, **kwargs):  # pylint: disable: arguments-differ
        modified = False
        if 'object' in parsed:
            obj = parsed.pop('object')
            if obj is not None:
                object_type = obj.get('objectType', 'Activity')
                factory = OBJECT_IFACE_MAP.get(object_type, None)
                obj = factory(obj) if factory else obj
            self._ext_setattr(self._ext_self, 'object', obj)
            modified = True
        if 'actor' in parsed:
            if 'objectType' not in parsed['actor']:
                parsed['actor']['objectType'] = 'Agent'
        return super(StatementIO, self).updateFromExternalObject(parsed, *args, **kwargs) or modified
