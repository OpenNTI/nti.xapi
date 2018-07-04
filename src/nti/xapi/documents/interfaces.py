#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from nti.schema.field import Object
from nti.schema.field import ValidBytes
from nti.schema.field import ValidDatetime
from nti.schema.field import DecodingValidTextLine as ValidTextLine

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import IActivity


class IDocument(interface.Interface):
    """
    Document interface
    """
    id = ValidTextLine(title=u'document id',
                       required=False)

    content = ValidBytes(title=u'The content of this document',
                         required=False)

    content_type = ValidTextLine(title=u'The content type.',
                                 required=False)

    etag = ValidTextLine(title=u'The document etag.',
                         required=False)

    timestamp = ValidDatetime(title=u'A document timestamp.',
                              required=False)


class IStateDocument(IDocument):
    """
    StateDocument interface
    """

    agent = Object(IAgent,
                   title=u'The document agent',
                   required=False)

    activity = Object(IActivity,
                      title=u'The document activity',
                      required=False)

    registration = ValidTextLine(title=u'The document registration.',
                                 required=False)
