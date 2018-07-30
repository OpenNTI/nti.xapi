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

KEY_VALIDATOR = ValidURI(required=True)

logger = __import__('logging').getLogger(__name__)


def _check_key(ext, key):
    bound_field = KEY_VALIDATOR.bind(ext)
    bound_field.validate(key)


@interface.implementer(IExtensions)
class Extensions(dict):

    __external_can_create__ = True

    def __init__(self, *args, **kwargs):
        check_args = dict(*args, **kwargs)
        # validate values
        for key in check_args.keys():
            _check_key(self, key)
        super(Extensions, self).__init__(check_args)

    def __setitem__(self, key, value):
        _check_key(self, key)
        super(Extensions, self).__setitem__(key, value)


class ExtensionsIO(MappingIO):
    pass
