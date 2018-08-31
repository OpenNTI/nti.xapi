#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.schema.fieldproperty import createFieldProperties

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import schemadict
from nti.schema.schema import SchemaConfigured

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import IIFIEntity
from nti.xapi.interfaces import IAgentAccount
from nti.xapi.interfaces import IAnonymousGroup
from nti.xapi.interfaces import IIdentifiedGroup

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IAgentAccount)
class AgentAccount(SchemaConfigured):

    __external_can_create__ = True

    createDirectFieldProperties(IAgentAccount)


class IFIMixin(object):
    pass


@interface.implementer(IAgent)
class Agent(SchemaConfigured, IFIMixin):

    __external_can_create__ = True

    createFieldProperties(IAgent)

    objectType = 'Agent'


def _is_ifientity(ext):
    schema = schemadict(IIFIEntity)
    for attr in schema:
        if ext.get(attr, None) is not None:
            return True
    return False


def _group_factory(ext):
    factory = AnonymousGroup
    if _is_ifientity(ext):
        factory = IdentifiedGroup
    return factory()


class GroupBase(object):

    __external_can_create__ = True

    objectType = 'Group'


@interface.implementer(IAnonymousGroup)
class AnonymousGroup(GroupBase, SchemaConfigured):
    createFieldProperties(IAnonymousGroup)


@interface.implementer(IIdentifiedGroup)
class IdentifiedGroup(GroupBase, SchemaConfigured, IFIMixin):
    createFieldProperties(IIdentifiedGroup)


# Callables returning a factory for the external value
ENTITY_FACTORIES = {
    'Agent': lambda x: Agent(),
    'Group': _group_factory
}


def _entity_factory(ext):
    object_type = ext.get('objectType', 'Agent')
    if object_type in ENTITY_FACTORIES:
        return ENTITY_FACTORIES[object_type](ext)
