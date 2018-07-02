#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six

from zope import interface

from nti.externalization.datastructures import ExternalizableInstanceDict

from nti.xapi.interfaces import ILanguageMap

logger = __import__('logging').getLogger(__name__)


def _check_lang_value(value):
    if not isinstance(value, six.string_types):
        raise TypeError("Value must be of type basestring")


@interface.implementer(ILanguageMap)
class LanguageMap(dict):

    def __init__(self, *args, **kwargs):
        """
        Initializes a LanguageMap with the given mapping
        This constructor will first check the arguments for flatness
        to avoid nested languagemaps (which are invalid) and then
        call the base dict constructor
        """
        check_args = dict(*args, **kwargs)
        # validate values
        for value in check_args.values():
            _check_lang_value(value)
        super(LanguageMap, self).__init__(check_args)

    def __setitem__(self, key, value):
        _check_lang_value(value)
        super(LanguageMap, self).__setitem__(key, value)


class LanguageMapIO(ExternalizableInstanceDict):

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
