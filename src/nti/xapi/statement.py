#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.externalization.internalization import update_from_external_object

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IActivity
from .interfaces import IAgent
from .interfaces import IGroup
from .interfaces import IStatement
from .interfaces import IStatementBase
from .interfaces import IStatementRef
from .interfaces import ISubStatement

from .io_datastructures import XAPIBaseIO

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


def _sub_statement_factory(ext):
    sub_stmt = SubStatement()
    update_from_external_object(sub_stmt, ext)
    return sub_stmt


@interface.implementer(ISubStatement)
class SubStatement(SchemaConfigured, StatementBase):

    createDirectFieldProperties(ISubStatement)

    objectType = 'SubStatement'


def _statement_factory(ext):
    stmt = Statement()
    update_from_external_object(stmt, ext)
    return stmt


@interface.implementer(IStatement)
class Statement(SchemaConfigured, StatementBase):

    createDirectFieldProperties(IStatement)

    objectType = 'Statement'


OBJECT_IFACE_MAP = {
    'Agent': IAgent,
    'Group': IGroup,
    'SubStatement': ISubStatement,
    'StatementRef': IStatementRef,
    'Statement': IStatement,
    'Activity': IActivity
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
        return super(StatementIO, self).updateFromExternalObject(parsed, *args, **kwargs) or modified
            
