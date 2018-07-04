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

from nti.xapi.interfaces import ILanguageMap

from nti.xapi.io_datastructures import MappingIO

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


class LanguageMapIO(MappingIO):
    pass
