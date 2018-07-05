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

from zope.interface.common.idatetime import IDateTime

from nti.externalization.externalization import to_external_object

from nti.externalization.internalization import update_from_external_object

from nti.xapi.about import About

from nti.xapi.documents.document import StateDocument
from nti.xapi.documents.document import ActivityProfileDocument

from nti.xapi.documents.interfaces import IStateDocument

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import Version
from nti.xapi.interfaces import IActivity
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

    def about(self):
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
                result = self.read_about(data)
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

    def get_statement(self, statement_id):
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
                result = self.read_statement(data)
            else:
                logger.error("Invalid server response [%s] while getting statement %s",
                             response.status_code, statement_id)
            return result
    statement = retrieve_statement = get_statement

    def get_voided_statement(self, statement_id):
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
                result = self.read_statement(data)
            else:
                logger.error("Invalid server response [%s] while getting voided statement %s",
                             response.status_code, statement_id)
            return result
    retrieve_voided_statement = get_voided_statement

    def query_statements(self, query):
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
                    params[k] = getattr(v, 'id', v)
                elif k in param_keys:
                    params[k] = to_external_object(v)
                elif k == 'agent':
                    params[k] = json.dumps(to_external_object(v))

        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "statements")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=query)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_statement_result(data)
            else:
                logger.error("Invalid server response [%s] while querying statements",
                             response.status_code)
            return result

    def more_statements(self, more_url):
        """
        Query the LRS for more statements

        :param more_url: URL from a StatementsResult object used to retrieve more statements
        :type more_url: str
        :return: The returned StatementsResult object
        :rtype: :class:`nti.xapi.interfaces.IStatementResult`
        """
        result = None
        more_url = getattr(more_url, "more", more_url)
        more_url = urllib_parse.urljoin(self.get_endpoint_server_root(),
                                        more_url)
        with self.session() as session:
            # pylint: disable=too-many-function-args
            response = session.get(more_url, auth=self.auth)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = self.read_statement_result(data)
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

    # states

    def get_state_ids(self, activity, agent, registration=None, since=None):
        """
        Retrieve state id's from the LRS with the provided parameters

        :param activity: Activity object of desired states
        :type activity: :class:`nti.xapi.interfaces.IActivity`
        :param agent: Agent object of desired states
        :type agent: :class:`nti.xapi.interfaces.IAgent`
        :param registration: Registration UUID of desired states
        :type registration: str
        :param since: Retrieve state id's since this time
        :type since: str
        :return: The retrieved state id's
        """
        agent = IAgent(agent, agent)
        activity = IActivity(activity, activity)

        # set pararms
        params = {
            "activityId": activity.id,
            "agent": json.dumps(to_external_object(agent))
        }
        if registration is not None:
            params["registration"] = registration
        if since is not None:
            params["since"] = to_external_object(since)

        # query
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/state")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=params)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = json.loads(data)
            else:
                logger.error("Invalid server response [%s] while getting state ids",
                             response.status_code)
            return result
    retrieve_state_ids = get_state_ids

    def get_state(self, activity, agent, state_id, registration=None):
        """
        Retrieve state from LRS with the provided parameters

        :param activity: Activity object of desired state
        :type activity: :class:`nti.xapi.interfaces.IActivity`
        :param agent: Agent object of desired state
        :type agent: :class:`nti.xapi.interfaces.IAgent`
        :param state_id: UUID of desired state
        :type state_id: str
        :param registration: registration UUID of desired state
        :type registration: str 
        :return: State document
        :rtype: :class:`nti.xapi.document.interfaces.IStateDocument`
        """
        agent = IAgent(agent, agent)
        activity = IActivity(activity, activity)

        # set pararms
        params = {
            'stateId': state_id,
            "activityId": activity.id,
            "agent": json.dumps(to_external_object(agent))
        }
        if registration is not None:
            params["registration"] = registration

        # query
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/state")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=params)
            if response.ok:
                data = response.content
                result = StateDocument(id=state_id,
                                       content=data,
                                       activity=activity,
                                       agent=agent)
                headers = response.headers
                if headers.get("lastModified", None) is not None:
                    result.timestamp = IDateTime(headers['lastModified'])
                if headers.get("contentType", None) is not None:
                    result.content_type = headers["contentType"]
                if headers.get("etag", None) is not None:
                    result.content_type = headers["etag"]
            elif response.status_code != 404:
                logger.error("Invalid server response [%s] while getting state %s",
                             response.status_code, state_id)

            return result
    retrieve_state = get_state

    def save_state(self, state):
        """
        Save a state doc to the LRS

        :param state: State document to be saved
        :type state: :class:`tincan.documents.state_document.StateDocument`
        :return: LRS Response object with saved state as content
        :rtype: :class:`tincan.lrs_response.LRSResponse`
        """
        state = IStateDocument(state, state)
        # set pararms
        # pylint: disable=no-member
        params = {
            'stateId': state.id,
            "activityId": state.activity.id,
            "agent": json.dumps(to_external_object(state.agent))
        }
        headers = {
            "Content-Type": state.content_type or "application/octet-stream"
        }
        if state.etag is not None:
            headers["If-Match"] = state.etag

        result = state
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/state")
            # pylint: disable=too-many-function-args
            response = session.put(url, auth=self.auth, params=params,
                                   data=state.content, headers=headers)
            if not (200 <= response.status_code < 300):
                logger.error("Invalid server response [%s] while saving state %s",
                             response.status_code, state.id)
                result = None
        return result

    def _delete_state(self, activity, agent, state_id=None, registration=None, etag=None):
        """
        Private method to delete a specified state from the LRS

        :param activity: Activity object of state to be deleted
        :type activity: :class:`nti.xapi.interfaces.IActivity`
        :param agent: Agent object of state to be deleted
        :type agent: :class:`nti.xapi.interfaces.IAgent`
        :param state_id: UUID of state to be deleted
        :type state_id: str
        :param registration: registration UUID of state to be deleted
        :type registration: str
        :param etag: etag of state to be deleted
        :type etag: str
        :return: Deleted state
        """
        agent = IAgent(agent, agent)
        activity = IActivity(activity, activity)

        # set pararms
        # pylint: disable=no-member
        params = {
            "activityId": activity.id,
            "agent": json.dumps(to_external_object(agent))
        }
        if state_id is not None:
            params["stateId"] = state_id
        if registration is not None:
            params["registration"] = registration

        # headers
        headers = {"If-Match": etag} if etag else None

        result = True
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/state")
            # pylint: disable=too-many-function-args
            response = session.delete(url, auth=self.auth, params=params,
                                      headers=headers)
            if not (200 <= response.status_code < 300):
                logger.error("Invalid server response [%s] while deleting state %s",
                             response.status_code, state_id)
                result = False
        return result

    def delete_state(self, state):
        """
        Delete a specified state from the LRS

        :param state: State document to be deleted
        :type state: :class:`nti.xapi.documents.interfaces.IStateDocument`
        :return: True if the state was deleted
        :rtype: bool
        """
        return self._delete_state(
            activity=state.activity,
            agent=state.agent,
            state_id=state.id,
            etag=state.etag
        )

    def clear_state(self, activity, agent, registration=None):
        """
        Clear state(s) with specified activity and agent

        :param activity: Activity object of state(s) to be deleted
        :type activity: :class:`nti.xapi.interfaces.IActivity`
        :param agent: Agent object of state(s) to be deleted
        :type agent: :class:`nti.xapi.interfaces.IAgent`
        :param registration: registration UUID of state(s) to be deleted
        :type registration: str
        :return: True if the state was cleared
        :rtype: bool
        """
        return self._delete_state(
            activity=activity,
            agent=agent,
            registration=registration
        )

    # profiles
    
    def retrieve_activity_profile_ids(self, activity, since=None):
        """
        Retrieve activity profile id(s) with the specified parameters

        :param activity: Activity object of desired activity profiles
        :type activity: :class:`nti.xapi.interfaces.IActivity`
        :param since: Retrieve activity profile id's since this time
        :type since: str 
        :return: List of retrieved activity profile ids
        """
        activity = IActivity(activity, activity)
        
        # set pararms
        # pylint: disable=no-member
        params = {
            "activityId": activity.id,
        }
        if since is not None:
            params["since"] = since
         
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/profile")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=params)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = json.loads(data)
            else:
                logger.error("Invalid server response [%s] while activity profile ids",
                             response.status_code)
        return result

    def retrieve_activity_profile(self, activity, profile_id):
        """
        Retrieve activity profile with the specified parameters

        :param activity: Activity object of the desired activity profile
        :type activity: :class:`tincan.activity.Activity`
        :param profile_id: UUID of the desired profile
        :type profile_id: str | unicode
        :return: LRS Response object with an activity profile doc as content
        :rtype: :class:`tincan.lrs_response.LRSResponse`
        """
        activity = IActivity(activity, activity)
        # set pararms
        # pylint: disable=no-member
        params = {
            "profileId": profile_id,
            "activityId": activity.id,
        }

        # query
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/profile")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=params)
            if response.ok:
                data = response.content
                result = ActivityProfileDocument(id=profile_id,
                                                 content=data,
                                                 activity=activity)
                headers = response.headers
                if headers.get("lastModified", None) is not None:
                    result.timestamp = IDateTime(headers['lastModified'])
                if headers.get("contentType", None) is not None:
                    result.content_type = headers["contentType"]
                if headers.get("etag", None) is not None:
                    result.content_type = headers["etag"]
            elif response.status_code != 404:
                logger.error("Invalid server response [%s] while getting activity profile %s",
                             response.status_code, profile_id)

            return result

    # misc

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
