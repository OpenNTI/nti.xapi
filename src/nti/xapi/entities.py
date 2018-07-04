#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.schema.fieldproperty import createFieldProperties

from nti.externalization.interfaces import IInternalObjectIO

from nti.externalization.internalization import update_from_external_object

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

from .interfaces import IAgentAccount
from .interfaces import IAgent
from .interfaces import IAnonymousGroup
from .interfaces import IGroup
from .interfaces import IIdentifiedGroup
from .interfaces import IIFIEntity


def _account_factory(ext):
    account = AgentAccount()
    update_from_external_object(account, ext)
    return account


@interface.implementer(IAgentAccount)
class AgentAccount(SchemaConfigured):

    createDirectFieldProperties(IAgentAccount)


class IFIMixin(object):
    pass


def _agent_factory(ext):
    agent = Agent()
    update_from_external_object(agent, ext)
    return agent


@interface.implementer(IAgent)
class Agent(SchemaConfigured, IFIMixin):

    objectType = 'Agent'

    createFieldProperties(IAgent)

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

def _entity_factory(ext):
    object_type = ext.get('objectType', None)
    if object_type not in ENTITY_IFACE_MAP:
        return None

    return ENTITY_IFACE_MAP[object_type](ext)
