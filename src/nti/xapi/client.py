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

from nti.externalization.externalization import to_external_object

from nti.externalization.internalization import update_from_external_object

from nti.xapi.about import About

from nti.xapi.interfaces import Version
from nti.xapi.interfaces import IStatement 
from nti.xapi.interfaces import IStatementList
 
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
        result = About()
        data = json.loads(data, "utf-8")
        update_from_external_object(result, data)
        return result

    # statements

    def save_statement(self, statement):
        """
        Save statement to LRS and update statement id if necessary

        :param statement: Statement object to be saved
        :type statement: :class:`nti.xapi.interfaces.IStatement`
        :return: Tthe saved statement
        :rtype: :class:`nti.xapi.interfaces.IStatement`
        """
        statement = IStatement(statement, statement)
        with self.session() as session:
            sid = statement.id
            url = urllib_parse.urljoin(self.endpoint, "statements")
            method = session.put if sid else session.post
            params = {"statementId": sid} if sid else None
            payload = to_external_object(statement)
            # pylint: disable=too-many-function-args
            response = method(url, auth=self.auth,
                              data=payload, params=params)
            if (200 <= response.status_code < 300):
                data = self.prepare_json_text(response.text)
                update_from_external_object(statement, data)
            else:
                statement = None
                logger.error("Invalid server response [%s] while saving statement.",
                             response.status_code)
            return statement
    
    def save_statements(self, statements):
        """
        Save statements to LRS and update their statement id's

        :param statements: A list of statement objects to be saved
        :type statements: :class:`nti.xapi.interfaces.IStatementList`
        :return: The saved list of statements
        :rtype: :class:`nti.xapi.interfaces.IStatementList`
        """
        statements = IStatementList(statements, statements)
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "statements")
            payload = to_external_object(statements)
            # pylint: disable=too-many-function-args
            response = session.post(url, payload, auth=self.auth)
            if (200 <= response.status_code < 300):
                data = self.prepare_json_text(response.text)
                data = json.loads(data, "utf-8")
                for s, statement_id in zip(statements, data):
                    s.id = statement_id
            else:
                statements = None
                logger.error("Invalid server response [%s] while saving statements.",
                             response.status_code)
            return statements
    
    def get_statement(self, statement_id, modeled=True):
        """
        Retrieve a statement from the server from its id

        :param statement_id: The UUID of the desired statement
        :type statement_id: str
        :return: The retrieved statement
        :rtype: :class:`nti.xapi.interfaces.IStatement`
        """
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "statements")
            # pylint: disable=too-many-function-args
            payload = {"statementId": statement_id}
            response = session.get(url, auth=self.auth,
                                   params=payload)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_statement(data) if modeled else json.loads(data)
            else:
                logger.error("Invalid server response [%s] while getting statement %s",
                             response.status_code, statement_id)
            return result
    statement = retrieve_statement = get_statement

    def get_voided_statement(self, statement_id, modeled=True):
        """
        Retrieve a voided statement from the server from its id

        :param statement_id: The UUID of the desired voided statement
        :type statement_id: str
        :return: The retrieved voided statement
        :rtype: :class:`nti.xapi.interfaces.IStatement`
        """
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "statements")
            # pylint: disable=too-many-function-args
            payload = {"voidedStatementId": statement_id}
            response = session.get(url, auth=self.auth,
                                   params=payload)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_statement(data) if modeled else json.loads(data)
            else:
                logger.error("Invalid server response [%s] while getting voided statement %s",
                             response.status_code, statement_id)
            return result
    retrieve_voided_statement = get_voided_statement

    def query_statements(self, query, modeled=True):
        """
        Query the LRS for statements with specified parameters

        :param query: Dictionary of query parameters and their values
        :type query: dict
        :return: The returned StatementsResult object 
        :rtype: :class:`nti.xapi.interfaces.IStatementResult`

        .. note::
           Optional query parameters are\n
               **statementId:** (*str*) ID of the Statement to fetch
               **voidedStatementId:** (*str*) ID of the voided Statement to fetch
               **agent:** (*Agent* |*Group*) Filter to return Statements for which the
               specified Agent or Group is the Actor
               **verb:** (*Verb id IRI*) Filter to return Statements matching the verb id
               **activity:** (*Activity id IRI*) Filter to return Statements for which the
               specified Activity is the Object
               **registration:** (*UUID*) Filter to return Statements matching the specified registration ID
               **related_activities:** (*bool*) Include Statements for which the Object,
               Context Activities or any Sub-Statement
               properties match the specified Activity
               **related_agents:** (*bool*) Include Statements for which the Actor, Object,
               Authority, Instructor, Team, or any Sub-Statement properties match the specified Agent
               **since:** (*datetime*) Filter to return Statements stored since the specified datetime
               **until:** (*datetime*) Filter to return Statements stored at or before the specified datetime
               **limit:** (*positive int*) Allow <limit> Statements to be returned. 0 indicates the
               maximum supported by the LRS
               **format:** (*str* {"ids"|"exact"|"canonical"}) Manipulates how the LRS handles
               importing and returning the statements
               **attachments:** (*bool*) If true, the LRS will use multipart responses and include
               all attachment data per Statement returned.
               Otherwise, application/json is used and no attachment information will be returned
               **ascending:** (*bool*) If true, the LRS will return results in ascending order of
               stored time (oldest first)
        """
        params = {}
        param_keys = (
            "registration",
            "since",
            "until",
            "limit",
            "ascending",
            "related_activities",
            "related_agents",
            "format",
            "attachments",
        )
        # parase query data
        for k, v in query.items():
            if v is not None:
                if k == "verb" or k == "activity":
                    params[k] = getattr(v, 'id' , v)
                elif k in param_keys or k == 'agent':
                    params[k] = to_external_object(v)

        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "statements")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=query)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_statement_result(data) if modeled else json.loads(data)
            else:
                logger.error("Invalid server response [%s] while querying statements",
                             response.status_code)
            return result

    def more_statements(self, more_url, modeled=True):
        """
        Query the LRS for more statements

        :param more_url: URL from a StatementsResult object used to retrieve more statements
        :type more_url: str
        :return: The returned StatementsResult object
        :rtype: :class:`nti.xapi.interfaces.IStatementResult`
        """
        result = None
        more_url = getattr(more_url, "more", more_url)
        more_url = urllib_parse.urljoin(self.get_endpoint_server_root(), more_url)
        with self.session() as session:
            # pylint: disable=too-many-function-args
            response = session.get(more_url, auth=self.auth)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_statement_result(data) if modeled else json.loads(data)
            else:
                logger.error("Invalid server response [%s] while getting more statements",
                             response.status_code)
            return result

    def read_statement(self, data):
        data = json.loads(data, "utf-8")
        return data

    def read_statement_result(self, data):
        data = json.loads(data, "utf-8")
        return data

    def get_endpoint_server_root(self):
        """
        Parses RemoteLRS object's endpoint and returns its root

        :return: Root of the RemoteLRS object endpoint
        :rtype: str
        """
        parsed = urllib_parse.urlparse(self.endpoint)
        root = parsed.scheme + "://" + parsed.netloc
        return root
client = LRSClient
