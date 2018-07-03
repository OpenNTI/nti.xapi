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

from nti.schema.field import ValidURI

from nti.xapi.interfaces import IExtensions

from nti.xapi.io_datastructures import MappingIO

logger = __import__('logging').getLogger(__name__)


KEY_VALIDATOR = ValidURI(required=True)

def _check_key(ext, key):
    bound_field = KEY_VALIDATOR.bind(ext)
    bound_field.validate(key)


@interface.implementer(IExtensions)
class Extensions(dict):

    def __init__(self, *args, **kwargs):
        """
        Initializes a LanguageMap with the given mapping
        This constructor will first check the arguments for flatness
        to avoid nested languagemaps (which are invalid) and then
        call the base dict constructor
        """
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
