#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.externalization.interfaces import IInternalObjectIO
from nti.externalization.interfaces import IInternalObjectIOFinder

from nti.externalization.datastructures import InterfaceObjectIO
from nti.externalization.datastructures import ExternalizableInstanceDict

from nti.externalization.interfaces import StandardExternalFields

from nti.xapi.interfaces import IXAPIBase

ID = StandardExternalFields.ID
OID = StandardExternalFields.OID
CLASS = StandardExternalFields.CLASS
NTIID = StandardExternalFields.NTIID

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IInternalObjectIO)
class MappingIO(object):

    def __init__(self, context):
        self.context = context

    def toExternalObject(self, *unused_args, **unused_kwargs):  # pylint: disable: arguments-differ
        return {
            k: self.context[k]
            for k in self.context if not k.startswith('_')
        }

    def updateFromExternalObject(self, parsed):
        updated = False
        for k in parsed:
            if not k.startswith('_'):
                self.context[k] = parsed[k]
                updated = True
        return updated


class XAPIBaseIO(InterfaceObjectIO):

    _ext_iface_upper_bound = IXAPIBase
    _excluded_out_ivars_ = {}
    _excluded_in_ivars_ = {}

    _ext_pop_none = True

    def toExternalObject(self, *args, **kwargs):  # pylint: disable: arguments-differ
        ext = super(XAPIBaseIO, self).toExternalObject(*args, **kwargs)
        ext.pop(CLASS, None)
        # set object type
        try:
            ext['objectType'] = self._ext_getattr(self._ext_replacement(), 'objectType')
        except AttributeError:
            pass

        # pop empty values
        if self._ext_pop_none:
            for k in list(ext.keys()):
                if ext[k] is None:
                    ext.pop(k)
        ext.pop(ID, None)
        ext.pop(OID, None)
        ext.pop(NTIID, None)
        return ext
