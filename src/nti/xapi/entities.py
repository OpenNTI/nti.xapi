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

from zope.schema.fieldproperty import createFieldProperties

from nti.externalization.internalization import update_from_external_object

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import schemadict
from nti.schema.schema import SchemaConfigured

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import IGroup
from nti.xapi.interfaces import IIFIEntity
from nti.xapi.interfaces import INamedEntity
from nti.xapi.interfaces import IAgentAccount
from nti.xapi.interfaces import IAnonymousGroup
from nti.xapi.interfaces import IIdentifiedGroup

logger = __import__('logging').getLogger(__name__)


@component.adapter(dict)
@interface.implementer(IAgentAccount)
def _account_factory(ext):
    account = AgentAccount()
    update_from_external_object(account, ext)
    return account


@interface.implementer(IAgentAccount)
class AgentAccount(SchemaConfigured):
    createDirectFieldProperties(IAgentAccount)


class IFIMixin(object):
    pass


@component.adapter(dict)
@interface.implementer(IAgent)
def _agent_factory(ext):
    agent = Agent()
    update_from_external_object(agent, ext)
    return agent


@interface.implementer(IAgent)
class Agent(SchemaConfigured, IFIMixin):
    createFieldProperties(IAgent)

    objectType = 'Agent'


def _is_ifientity(ext):
    schema = schemadict(IIFIEntity)
    for attr in schema:
        if ext.get(attr, None) is not None:
            return True
    return False


@component.adapter(dict)
@interface.implementer(IGroup)
def _group_factory(ext):
    factory = AnonymousGroup
    if _is_ifientity(ext):
        factory = IdentifiedGroup
    group = factory()
    update_from_external_object(group, ext)
    return group


class GroupBase(object):
    objectType = 'Group'


@interface.implementer(IAnonymousGroup)
class AnonymousGroup(GroupBase, SchemaConfigured):
    createFieldProperties(IAnonymousGroup)


@interface.implementer(IIdentifiedGroup)
class IdentifiedGroup(GroupBase, SchemaConfigured, IFIMixin):
    createFieldProperties(IIdentifiedGroup)


ENTITY_IFACE_MAP = {
    'Agent': IAgent,
    'Group': IGroup
}


@component.adapter(dict)
@interface.implementer(INamedEntity)
def _entity_factory(ext):
    object_type = ext.get('objectType', None)
    if object_type in ENTITY_IFACE_MAP:
        return ENTITY_IFACE_MAP[object_type](ext)
