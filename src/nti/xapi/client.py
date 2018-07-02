#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from requests import Session

import simplejson as json

import six
from six.moves import urllib_parse

from nti.xapi.interfaces import Version

logger = __import__('logging').getLogger(__name__)


class LRSClient(object):

    def __init__(self, endpoint, username=None, password=None,
                 version=Version.latest):
        """
        LRSClient Constructor

        :param endpoint: lrs endpoint
        :type endpoint: str | unicode
        :param version: Version used for lrs communication
        :type version: str
        :param username: Username for lrs. Used to build the authentication string.
        :type username: str
        :param password: Password for lrs. Used to build the authentication string.
        :type password: str
        """
        self.version = version
        self.endpoint = endpoint
        self.username = username
        self.password = password
        assert (username and password) or (not username and not password)

    @property
    def auth(self):
        return (self.username, self.password) if self.username else None

    def session(self):
        return Session()

    @classmethod
    def prepare_json_text(cls, data):
        if isinstance(data, six.binary_type):
            data = data.decode("utf-8")
        return data

    # about

    def about(self, modeled=True):
        """
        Gets about response from LRS

        :return: The returned About object
        :rtype: :class:`nti.xapi.interfaces.IAbout`
        """
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "about")
            # pylint: disable=too-many-function-args
            response = session.get(session, url, auth=self.auth)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_about(data) if modeled else json.loads(data)
            else:
                logger.error("Invalid server response [%s] while getting about.",
                             response.status_code)
            return result

    def read_about(self, data):
        return data

    # statements

    def get_statement(self, statement_id, modeled=True):
        """
        Retrieve a statement from the server from its id

        :param statement_id: The UUID of the desired statement
        :type statement_id: str
        :return: LRS Response object with the retrieved statement as content
        :rtype: :class:`tincan.lrs_response.LRSResponse`
        """
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "about")
            # pylint: disable=too-many-function-args
            payload = {"statementId": statement_id}
            response = session.get(session, url, auth=self.auth,
                                   params=payload)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_statement(data) if modeled else json.loads(data)
            else:
                logger.error("Invalid server response [%s] while getting statement %s",
                             response.status_code, statement_id)
            return result
    statement = retrieve_statement = get_statement

    def read_statement(self, data):
        return data


client = LRSClient
