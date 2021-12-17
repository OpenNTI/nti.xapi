#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from requests import Session
from requests import Request

import simplejson as json

import six
from six.moves import urllib_parse

from mimetypes import guess_type

from zope import interface

from zope.interface.common.idatetime import IDateTime

from nti.externalization import to_external_object

from nti.externalization import update_from_external_object

from nti.xapi.about import About

from nti.xapi.documents.document import StateDocument
from nti.xapi.documents.document import AgentProfileDocument
from nti.xapi.documents.document import ActivityProfileDocument

from nti.xapi.documents.interfaces import IStateDocument
from nti.xapi.documents.interfaces import IAgentProfileDocument
from nti.xapi.documents.interfaces import IActivityProfileDocument

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import Version
from nti.xapi.interfaces import IActivity
from nti.xapi.interfaces import ILRSClient
from nti.xapi.interfaces import IStatement

from nti.xapi.statement import Statement
from nti.xapi.statement import StatementResult

logger = __import__('logging').getLogger(__name__)

# Date parsing lifted from webob.datetime_utils
# for dealing with http header to datetime conversions
# https://github.com/Pylons/webob/blob/master/src/webob/datetime_utils.py
from datetime import datetime, timedelta, tzinfo
from email.utils import mktime_tz, parsedate_tz


class _UTC(tzinfo):
    def dst(self, dt):
        return timedelta(0)

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def __repr__(self):
        return "UTC"


UTC = _UTC()


def _parse_date(value):
    if not value:
        return None
    try:
        if not isinstance(value, str):
            value = str(value, "latin-1")
    except Exception:
        return None
    t = parsedate_tz(value)

    if t is None:
        # Could not parse

        return None

    t = mktime_tz(t)

    return datetime.fromtimestamp(t, UTC)


@interface.implementer(ILRSClient)
class LRSClient(object):

    def __init__(self, endpoint, auth=None,
                 version=Version.latest):
        """
        LRSClient Constructor

        :param endpoint: lrs endpoint
        :type endpoint: str | unicode
        :param version: Version used for lrs communication
        :type version: str
        :param auth: Authentication for interacting with the lrs
        :type auth: see requests.auth
        """
        if endpoint and not endpoint.endswith('/'):
            endpoint = endpoint + '/'

        self.version = version
        self.endpoint = endpoint
        self.auth = auth

    def session(self):
        s = Session()
        s.headers.update({'X-Experience-API-Version': self.version})
        return s

    @classmethod
    def prepare_json_text(cls, data):
        if isinstance(data, six.binary_type):
            data = data.decode("utf-8")
        return data

    # about

    def about(self):
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "about")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth)
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

    def save_statement(self, statement, attachments=None):
        statement = IStatement(statement, statement)
        with self.session() as session:
            sid = statement.id
            params = {"statementId": sid} if sid else None
            method = 'PUT' if sid else 'POST'
            response = self.prepare_statement_request_helper(method, session, [statement], attachments, params)
            response.raise_for_status()
            data = self.prepare_json_text(response.text)
            data = (sid,) if sid else json.loads(data, "utf-8")
            statement.id = data[0]
            return statement

    def save_statements(self, statements, attachments=None):
        with self.session() as session:
            method = 'POST'
            response = self.prepare_statement_request_helper(method, session, statements, attachments)
            response.raise_for_status()
            data = self.prepare_json_text(response.text)
            data = json.loads(data, "utf-8")
            for s, statement_id in zip(statements, data):
                s.id = statement_id
            return statements

    def send_statement_request_helper(self, method, session, statements, attachments, params=None):
        url = urllib_parse.urljoin(self.endpoint, "statements")
        payload = to_external_object(statements)
        if not attachments:
            r = Request(method, url, params=params, json=payload, auth=self.auth)
            prepped = session.prepare_request(r)
        else:
            files = {'json': ('json', json.dumps(payload), 'application/json')}
            for statement in statements:
                for attachment in statement.attachments or ():
                    if not hasattr(attachment, 'fileURL'):  # This is not a url based attachment.
                        file_hash = attachment.sha2
                        files[file_hash] = (file_hash, attachments[file_hash], attachment.contentType,
                                            {'X-Experience-API-Hash': file_hash,
                                             'Content-Transfer-Encoding': 'binary'})

            # send request, if request has an attachment, we must manually update the content header
            prepped = session.prepare_request(
                Request(method, url, files=files, params=params, json=payload, auth=self.auth))
            # xapi requires the content-type of requests with attachments to be 'mutlipart/mixed'
            prepped.headers['Content-type'] = prepped.headers['Content-type']\
                .replace('multipart/form-data', 'multipart/mixed')
        return session.send(prepped)

    def retrieve_statement(self, statement_id):
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
    statement = get_statement = retrieve_statement

    def retrieve_voided_statement(self, statement_id):
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
    get_voided_statement = retrieve_voided_statement

    def query_statements(self, query):
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
        result = None
        more_url = getattr(more_url, "more", more_url)
        more_url = urllib_parse.urljoin(self._get_endpoint_server_root(),
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
        stmt = Statement()
        update_from_external_object(stmt, data)
        return stmt

    def read_statement_result(self, data):
        data = json.loads(data, "utf-8")
        result = StatementResult()
        update_from_external_object(result, data)
        return result

    # states

    def retrieve_state_ids(self, activity, agent, registration=None, since=None):
        agent = IAgent(agent, agent)
        activity = IActivity(activity, activity)

        # set params
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
    get_state_ids = retrieve_state_ids

    def retrieve_state(self, activity, agent, state_id, registration=None):
        agent = IAgent(agent, agent)
        activity = IActivity(activity, activity)

        # set params
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
                self._set_document_headers(result, response.headers)
            elif response.status_code != 404:
                logger.error("Invalid server response [%s] while getting state %s",
                             response.status_code, state_id)

            return result
    get_state = retrieve_state

    def save_state(self, state):
        state = IStateDocument(state, state)

        # set params
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

        # set params
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
        return self._delete_state(
            activity=state.activity,
            agent=state.agent,
            state_id=state.id,
            etag=state.etag
        )

    def clear_state(self, activity, agent, registration=None):
        return self._delete_state(
            activity=activity,
            agent=agent,
            registration=registration
        )

    # activity profiles

    def retrieve_activity_profile_ids(self, activity, since=None):
        activity = IActivity(activity, activity)

        # set params
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
    get_activity_profile_ids = retrieve_activity_profile_ids

    def retrieve_activity_profile(self, activity, profile_id):
        activity = IActivity(activity, activity)

        # set params
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
                self._set_document_headers(result, response.headers)
            elif response.status_code != 404:
                logger.error("Invalid server response [%s] while getting activity profile %s",
                             response.status_code, profile_id)

            return result
    get_activity_profile = retrieve_activity_profile

    def save_activity_profile(self, profile):
        profile = IActivityProfileDocument(profile, profile)

        # set params
        # pylint: disable=no-member
        params = {
            "profileId": profile.id,
            "activityId": profile.activity.id
        }
        headers = {
            "Content-Type": profile.content_type or "application/octet-stream"
        }
        if profile.etag is not None:
            headers["If-Match"] = profile.etag

        result = profile
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/profile")
            # pylint: disable=too-many-function-args
            response = session.put(url, auth=self.auth, params=params,
                                   data=profile.content, headers=headers)
            if not (200 <= response.status_code < 300):
                logger.error("Invalid server response [%s] while saving activity profile %s",
                             response.status_code, profile.id)
                result = None
        return result

    def delete_activity_profile(self, profile):
        profile = IActivityProfileDocument(profile, profile)

        # set params
        # pylint: disable=no-member
        params = {
            "profileId": profile.id,
            "activityId": profile.activity.id
        }

        # headers
        headers = {"If-Match": profile.etag} if profile.etag else None

        result = True
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "activities/profile")
            # pylint: disable=too-many-function-args
            response = session.delete(url, auth=self.auth, params=params,
                                      headers=headers)
            if not (200 <= response.status_code < 300):
                logger.error("Invalid server response [%s] while deleting activity profile %s",
                             response.status_code, profile.id)
                result = False
        return result

    # agent profiles

    def retrieve_agent_profile_ids(self, agent, since=None):
        agent = IAgent(agent, agent)

        # set params
        params = {
            "agent": json.dumps(to_external_object(agent))
        }
        if since is not None:
            params["since"] = to_external_object(since)

        # query
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "agents/profile")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=params)
            if response.ok:
                data = self.prepare_json_text(response.text)
                result = json.loads(data)
            else:
                logger.error("Invalid server response [%s] while getting agent profile ids",
                             response.status_code)
            return result
    get_agent_profile_ids = retrieve_agent_profile_ids

    def retrieve_agent_profile(self, agent, profile_id):
        agent = IAgent(agent, agent)

        # set params
        # pylint: disable=no-member
        params = {
            "profileId": profile_id,
            "agent": json.dumps(to_external_object(agent))
        }

        # query
        result = None
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "agents/profile")
            # pylint: disable=too-many-function-args
            response = session.get(url, auth=self.auth, params=params)
            if response.ok:
                data = response.content
                result = AgentProfileDocument(id=profile_id,
                                              content=data,
                                              agent=agent)
                self._set_document_headers(result, response.headers)
            elif response.status_code != 404:
                logger.error("Invalid server response [%s] while getting agent profile %s",
                             response.status_code, profile_id)

            return result
    get_agent_profile = retrieve_agent_profile

    def save_agent_profile(self, profile):
        profile = IAgentProfileDocument(profile, profile)

        # set params
        # pylint: disable=no-member
        params = {
            "profileId": profile.id,
            "agent": json.dumps(to_external_object(profile.agent))
        }
        headers = {
            "Content-Type": profile.content_type or "application/octet-stream"
        }
        if profile.etag is not None:
            headers["If-Match"] = profile.etag

        result = profile
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "agents/profile")
            # pylint: disable=too-many-function-args
            response = session.put(url, auth=self.auth, params=params,
                                   data=profile.content, headers=headers)
            if not (200 <= response.status_code < 300):
                logger.error("Invalid server response [%s] while saving agent profile %s",
                             response.status_code, profile.id)
                result = None
        return result

    def delete_agent_profile(self, profile):
        profile = IAgentProfileDocument(profile, profile)

        # set params
        # pylint: disable=no-member
        params = {
            "profileId": profile.id,
            "agent": json.dumps(to_external_object(profile.agent))
        }

        # headers
        headers = {"If-Match": profile.etag} if profile.etag else None

        result = True
        with self.session() as session:
            url = urllib_parse.urljoin(self.endpoint, "agents/profile")
            # pylint: disable=too-many-function-args
            response = session.delete(url, auth=self.auth, params=params,
                                      headers=headers)
            if not (200 <= response.status_code < 300):
                logger.error("Invalid server response [%s] while deleting activity profile %s",
                             response.status_code, profile.id)
                result = False
        return result

    # misc

    def _set_document_headers(self, doc, headers):
        if headers.get("last-modified", None) is not None:
            doc.timestamp = IDateTime(_parse_date(headers['last-modified']))
        if headers.get("content-type", None) is not None:
            doc.content_type = headers["content-type"]
        if headers.get("etag", None) is not None:
            doc.etag = headers["etag"]
        return doc

    def _get_endpoint_server_root(self):
        """
        Parses RemoteLRS object's endpoint and returns its root

        :return: Root of the RemoteLRS object endpoint
        :rtype: str
        """
        parsed = urllib_parse.urlparse(self.endpoint)
        root = parsed.scheme + "://" + parsed.netloc
        return root


Client = LRSClient
