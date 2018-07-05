#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.externalization.datastructures import InterfaceObjectIO
from nti.externalization.datastructures import ExternalizableInstanceDict

from nti.externalization.interfaces import StandardExternalFields

from nti.xapi.interfaces import IXAPIBase

CLASS = StandardExternalFields.CLASS

logger = __import__('logging').getLogger(__name__)


class MappingIO(ExternalizableInstanceDict):

    def __init__(self, replacement):
        ExternalizableInstanceDict.__init__(self)
        self._ext_self = replacement

    def _ext_setattr(self, ext_self, k, v):  # pylint: disable: arguments-differ
        ext_self[k] = v

    def _ext_getattr(self, ext_self, k):
        return ext_self.get(k)

    def _ext_accept_update_key(self, k, unused_ext_self, unused_ext_keys):
        return not k.startswith('_')

    def _ext_replacement(self):
        return self._ext_self

    def toExternalObject(self, *unused_args, **unused_kwargs):  # pylint: disable: arguments-differ
        return {
            k: self._ext_getattr(self._ext_self, k)
            for k in self._ext_self if not k.startswith('_')
        }


class XAPIBaseIO(InterfaceObjectIO):

    _ext_iface_upper_bound = IXAPIBase
    _excluded_out_ivars_ = {}
    _excluded_in_ivars_ = {}

    _ext_pop_none = True

    def toExternalObject(self, *args, **kwargs):  # pylint: disable: arguments-differ
        ext = super(XAPIBaseIO, self).toExternalObject(*args, **kwargs)
        ext.pop(CLASS, None)
        # set object type
        object_type = getattr(self._ext_self, 'objectType', None)
        if object_type is not None:
            ext['objectType'] = object_type
        # pop empty values
        if self._ext_pop_none:
            for k in list(ext.keys()):
                if ext[k] is None:
                    ext.pop(k)
        return ext
