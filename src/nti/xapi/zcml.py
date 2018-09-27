#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from functools import partial

from zope import interface

from zope.component.zcml import utility

from zope.schema import URI
from zope.schema import TextLine

from nti.xapi.client import LRSClient

from nti.xapi.interfaces import Version
from nti.xapi.interfaces import ILRSClient

logger = __import__('logging').getLogger(__name__)


class IRegisterLRSClient(interface.Interface):

    endpoint = URI(title=u'The xAPI LRS endpoint',
                   required=True)

    username = TextLine(title=u'The xAPI LRS username.',
                        required=False)

    password = TextLine(title=u'client identifier',
                        required=False)

    version = TextLine(title=u'The SCORM Cloud service URL.',
                       required=False,
                       default=Version.latest)


def registerLRSClient(_context, endpoint=None, username=None, password=None,
                      version=Version.latest):
    factory = partial(LRSClient, endpoint, username=username,
                      password=password, version=version)
    utility(_context, provides=ILRSClient, factory=factory)
