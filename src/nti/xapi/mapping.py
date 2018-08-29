#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from collections import MutableMapping


class ValidatingMutableMapping(MutableMapping):
    """
    A MutableMapping backed by this objects __dict__
    that validates keys and values as they are set.

    Subclasses can override `_validate_key_value` to provide validation
    on update.
    """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def _validate_key_value(self, key, value):
        pass

    def __setitem__(self, key, value):
        self._validate_key_value(key, value)
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

