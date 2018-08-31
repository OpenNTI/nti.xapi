#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.schema.field import ValidURI

from nti.xapi.datastructures import MappingIO

from nti.xapi.interfaces import IExtensions

from nti.xapi.mapping import ValidatingMutableMapping

KEY_VALIDATOR = ValidURI(required=True)

logger = __import__('logging').getLogger(__name__)


def _check_key(ext, key):
    bound_field = KEY_VALIDATOR.bind(ext)
    bound_field.validate(key)


@interface.implementer(IExtensions)
class Extensions(ValidatingMutableMapping):

    __external_can_create__ = True

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def _validate_key_value(self, key, value):
        _check_key(self, key)


class ExtensionsIO(MappingIO):
    pass


