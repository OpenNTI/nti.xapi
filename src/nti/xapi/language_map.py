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

from nti.xapi.datastructures import MappingIO

from nti.xapi.interfaces import ILanguageMap

from nti.xapi.mapping import ValidatingMutableMapping

logger = __import__('logging').getLogger(__name__)


def _check_lang_value(value):
    if not isinstance(value, six.string_types):
        raise TypeError("Value must be of type basestring")


@interface.implementer(ILanguageMap)
class LanguageMap(ValidatingMutableMapping):

    __external_can_create__ = True

    def _validate_key_value(self, key, value):
        _check_lang_value(value)


class LanguageMapIO(MappingIO):
    pass
