#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

import re

from zope import interface

from zope.interface import Attribute

from zope.interface.common.mapping import IMapping

from zope.schema.interfaces import ValidationError

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import Variant
from nti.schema.field import ValidURI
from nti.schema.field import Timedelta
from nti.schema.field import ListOrTuple
from nti.schema.field import ValidDatetime
from nti.schema.field import DecodingValidTextLine as ValidTextLine


_UUID_REGEX = re.compile(
    r'^[a-f0-9]{8}-'
    r'[a-f0-9]{4}-'
    r'[1-5][a-f0-9]{3}-'
    r'[89ab][a-f0-9]{3}-'
    r'[a-f0-9]{12}$'
)


def _check_uuid(uuid):
    if not _UUID_REGEX.match(uuid):
        raise InvalidUUID('Invalid UUID')
    return True


class InvalidUUID(ValidationError):
    """
    Raised when a UUID is of the wrong format
    """


class Version(object):
    """
    Version information
    """
    supported = [
        u'1.0.3',
        u'1.0.2',
        u'1.0.1',
        u'1.0.0',
    ]
    latest = supported[0]


class IXAPIBase(interface.Interface):
    """
    A base interface for other xAPI defined interfaces
    """


class IExtensions(IMapping, IXAPIBase):
    """
    An extension map for various contexts. keys must be IRIs and values can be any
    valid json serializable structure.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#41-extensions
    """


class ILanguageMap(IMapping, IXAPIBase):
    """
    A mapping from language tag to display string. The keys and values are both
    strings.

    A language map is a dictionary where the key is a RFC 5646 Language Tag,
    and the value is a string in the language specified in the tag. This map
    SHOULD be populated as fully as possible based on the knowledge of the string in
    question in different languages.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#42-language-maps
    """


class IAbout(IXAPIBase):
    """
    Information about an LRS
    """

    version = ListOrTuple(title=u'version',
                          description=u'The support versions',
                          required=True,
                          default=(Version.latest,))

    extensions = Object(IExtensions,
                        title=u'supported extensions',
                        description=u'Extensions supported by this LRS',
                        required=False)


class IAgentAccount(IXAPIBase):
    """
    A user account on an existing system, such as a private system (LMS or intranet) or a public system (social networking site).

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#2424-account-object
    """

    name = ValidTextLine(title=u'account name',
                         description=u'The unique id or name used to log in to this account',
                         required=True,
                         min_length=1)

    homePage = ValidURI(title=u'The canonical home page for the account',
                        description=u'The canonical home page for the system the account is on. This is based on FOAFs accountServiceHomePage.',
                        required=True)


class IIFIEntity(interface.Interface):
    """
    An Entity identified by an Inverse Functional Identifier (IFI) is a value of an Agent or Identified Group
    that is guaranteed to only ever refer to that Agent or Identified Group.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#2423-inverse-functional-identifier
    """
    mbox = ValidURI(title=u'mailto URI',
                    required=False)

    mbox_sha1sum = ValidTextLine(title=u'The hex-encoded SHA1 hash of a mailto IRI',
                                 required=False,
                                 min_length=1)

    openid = ValidURI(title=u'An openID that uniquely identifies the Agent.',
                      required=False)

    account = Object(IAgentAccount,
                     title=u'A user account on an existing system',
                     required=False)


class INamedEntity(IXAPIBase):
    """
    An xAPI entity (group or agent) with a name
    """

    name = ValidTextLine(title=u'Agent name.',
                         description=u'Full name of the Agent.',
                         required=False,
                         min_length=1)


class IAgent(INamedEntity, IIFIEntity):
    """
    An Agent (an individual) is a persona or system.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#2421-when-the-actor-objecttype-is-agent
    """


class IGroup(INamedEntity):
    """
    A Group represents a collection of Agents

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#description-3
    """


class IAnonymousGroup(IGroup):
    """
    An Anonymous Group is used to describe a cluster of people where there is no
    ready identifier for this cluster, e.g. an ad hoc team.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#description-3
    """
    member = ListOrTuple(title=u'The members of this Group.',
                         value_type=Object(IAgent),
                         default=(),
                         required=True)


class IIdentifiedGroup(IGroup, IIFIEntity):
    """
    An Identified Group is used to uniquely identify a cluster of Agents.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#description-3
    """
    member = ListOrTuple(title=u'The members of this Group.',
                         value_type=Object(IAgent),
                         required=False)


class IVerb(IXAPIBase):
    """
    The Verb defines the action between an Actor and an Activity.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#243-verb
    """

    id = ValidURI(title=u'Corresponds to a Verb definition',
                  required=True)

    display = Object(ILanguageMap,
                     title=u'The human readable representation of the Verb in one or more languages.',
                     required=False)


class IActivityInteraction(IXAPIBase):
    """
    Traditional e-learning has included structures for interactions or assessments.
    As a way to allow these practices and structures to extend Experience API's utility,
    this specification includes built-in definitions for interactions,
    which borrows from the SCORM 2004 4th Edition Data Model.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#interaction-activities
    """
    correctResponsesPattern = ListOrTuple(title=u'A pattern representing the correct response to the interaction.\
    The structure of this pattern varies depending on the interactionType.',
                                          required=False)

# Must implement Subinterfaces of IACtivityInteraction for each type
# https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#appendix-c-example-definitions-for-activities-of-type-cmiinteraction


class IActivityDefinition(IActivityInteraction):
    """
    Metadata providing more definition for an IActivity.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#activity-definition
    """

    name = Object(ILanguageMap,
                  title=u'The human readable/visual name of the Activity',
                  required=False)

    description = Object(ILanguageMap,
                         title=u'A description of the Activity',
                         required=False)

    type = ValidURI(title=u'The type of activity',
                    required=False)

    moreInfo = ValidURI(title=u'Resolves to a document with human-readable information about the Activity',
                        required=False)

    extensions = Object(IExtensions,
                        title=u'Activity definition extensions.',
                        required=False)


class IActivity(IXAPIBase):
    """
    A Statement can represent an Activity as the Object of the Statement.
    The following table lists the Object properties in this case.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#2441-when-the-objecttype-is-activity
    """

    id = ValidTextLine(title=u'An identifier for a single unique Activity',
                       required=True)

    definition = Object(IActivityDefinition,
                        title=u'Metadata about the activity',
                        required=False)


class IStatementRef(IXAPIBase):
    """
    A Statement Reference is a pointer to another pre-existing Statement.
    A common use case for Statement References is grading or commenting on an experience
    that could be tracked as an independent event. The special case of
    voiding a Statement would also use a Statement Reference.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#description-8
    """

    id = ValidTextLine(title=u'ID for the statement we are referencing',
                       required=True,
                       constraint=_check_uuid)


class IContextActivities(IXAPIBase):
    """
    Many Statements do not just involve one (Object) Activity that is the focus,
    but relate to other contextually relevant Activities. The `IContextActivities` object
    property allow for these related Activities to be represented in a structured manner.

    The values in this object are not for expressing all the relationships the Statement Object has.
    Instead, they are for expressing relationships appropriate for the specific Statement
    (though the nature of the Object will often be important in determining that).
    For instance, it is appropriate in a Statement about a test to include the course the test
    is part of as a "parent", but not to include every possible degree
    program the course could be part of in the grouping value.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#details-15
    """

    parent = ListOrTuple(title=u'An Activity with a direct relation to the Activity which is the Object of the Statement.',
                         value_type=Object(IActivity),
                         required=False)

    grouping = ListOrTuple(title=u'An Activity with an indirect relation to the Activity which is the Object of the Statement.',
                           value_type=Object(IActivity),
                           required=False)

    category = ListOrTuple(title=u'An Activity with an indirect relation to the Activity which is the Object of the Statement.',
                           value_type=Object(IActivity),
                           required=False)

    other = ListOrTuple(title=u'A contextActivity that doesn\'t fit one of the other properties.',
                        value_type=Object(IActivity),
                        required=False)


class IContext(IXAPIBase):
    """
    The "context" provides a place to add some contextual information to a Statement.
    It can store information such as the instructor for an experience,
    if this experience happened as part of a team-based Activity,
    or how an experience fits into some broader activity.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#246-context
    """

    # Use a field that actually validates UUID. Will be assigned
    registration = ValidTextLine(title=u'The registration that the Statement is associated with.',
                                 required=False,
                                 constraint=_check_uuid)

    instructor = Object(INamedEntity,
                        title=u'Instructor that the Statement relates to, if not included as the Actor of the Statement.',
                        required=False)

    team = Object(IGroup,
                  title=u'Team that this Statement relates to, if not included as the Actor of the Statement.',
                  required=False)

    contextActivities = Object(IContextActivities,
                               title=u'Learning activity context that this Statement is related to',
                               required=False)

    revision = ValidTextLine(title=u'Revision of the learning activity associated with this Statement. Format is free.',
                             required=False)

    platform = ValidTextLine(title=u'Platform used in the experience of this learning activity.',
                             required=False)

    # Actually validate proper language code
    language = ValidTextLine(title=u'Code representing the language in which the experience \
    being recorded in this Statement (mainly) occurred in, if applicable and known.',
                             required=False)

    statement = Object(IStatementRef,
                       title=u'Another Statement to be considered as context for this Statement.',
                       required=False)

    extensions = Object(IExtensions,
                        title=u'A map of other properties as needed.',
                        required=False)


class MissingAttachmentDataException(Exception):
    """
    An exception raised when attempting to send a request with a file hash that is not referenced in the Statement's
     list of IAttachment objects.
    """


class IAttachment(IXAPIBase):
    """
    In some cases an Attachment is logically an important part of a Learning Record.
    It could be an essay, a video, etc. Another example of such an Attachment is (the image of)
    a certificate that was granted as a result of an experience.
    It is useful to have a way to store these Attachments in and retrieve them from an LRS.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#2411-attachments
    """
    usageType = ValidURI(title=u'Identifies the usage of this Attachment.',
                         required=True)

    display = Object(ILanguageMap,
                     title=u'Display name (title) of this Attachment.',
                     required=True)

    description = Object(ILanguageMap,
                         title=u'A description of the Attachment',
                         required=False)

    contentType = ValidTextLine(title=u'The content type of the Attachment.',
                                required=True,
                                min_length=1)

    length = Number(title=u'The length of the Attachment data in octets.',
                    required=True,
                    min=0)

    sha2 = ValidTextLine(title=u'The SHA-2 hash of the Attachment data.',
                         required=True,
                         min_length=1)

    fileUrl = ValidURI(title=u'An IRL at which the Attachment data can be retrieved',
                       required=False)


class IScore(IXAPIBase):
    """
    An optional property that represents the outcome of a graded Activity achieved by an Agent.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#Score
    """

    scaled = Number(title=u'Scaled score',
                    description=u'The score related to the experience as modified by scaling and/or normalization.',
                    required=False,
                    min=-1.0,
                    max=1.0)

    # Validate this based on min and max on this object
    raw = Number(title=u'Raw Score',
                 description=u'The score achieved by the Actor in the experience described by the Statement.',
                 required=False)

    min = Number(title=u'Min Score',
                 description=u'The lowest possible score for the experience described by the Statement.',
                 required=False)

    max = Number(title=u'Max Score',
                 description=u'The highest possible score for the experience described by the Statement.',
                 required=False)


class IResult(IXAPIBase):
    """
    An optional property that represents a measured outcome related to the Statement in which it is included.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#Score
    """

    score = Object(IScore,
                   title=u'The score of the Agent in relation to the success or quality of the experience.',
                   required=False)

    success = Bool(title=u'Indicates whether or not the attempt on the Activity was successful.',
                   required=False)

    completion = Bool(title=u'Indicates whether or not the Activity was completed.',
                      required=False)

    response = ValidTextLine(title=u'A response appropriately formatted for the given Activity.',
                             required=False)

    duration = Timedelta(title=u'Period of time over which the Statement occurred.',
                         required=False)

    extensions = Object(IExtensions,
                        title=u'A map of other properties as needed.',
                        required=False)


class IStatementBase(IXAPIBase):
    """
    Shared fields for all types of statements
    """

    actor = Object(INamedEntity,
                   title=u'The Actor defines who performed the action',
                   required=True)

    verb = Object(IVerb,
                  title=u'Action taken by the Actor.',
                  required=True)

    object = Attribute(u'Base type for a statement.')

    timestamp = ValidDatetime(
        title=u'Timestamp of when the events described within this Statement occurred.',
        required=False)

    context = Object(IContext,
                     title=u'Context that gives the Statement more meaning.',
                     required=False)

    attachments = ListOrTuple(title=u'Headers for Attachments to the Statement.',
                              value_type=Object(IAttachment),
                              required=False)


class ISubStatement(IStatementBase):
    """
    A SubStatement is like a StatementRef in that it is included as
    part of a containing Statement, but unlike a StatementRef, it does not
    represent an event that has occurred. It can be used to describe, for example,
    a predication of a potential future Statement or the behavior a teacher
    looked for when evaluating a student (without representing the student actually doing that behavior).

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#substatements
    """

    # Redefine object to the variant we expect
    object = Variant((Object(INamedEntity),
                      Object(IActivity)),
                     title=u'The thing that was acted on.',
                     required=True)


class IStatement(IStatementBase):
    """
    Statements are the evidence for any sort of experience or event which
    is to be tracked in xAPI. While Statements follow a machine readable JSON format,
    they can also easily be described using natural language.
    This can be extremely useful for the design process. Statements are meant to
    be aggregated and analyzed to provide larger meaning for the overall experience
    than just the sum of its parts.

    See also: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#statements
    """

    id = ValidTextLine(title=u'The UUID for this statement',
                       required=False,
                       constraint=_check_uuid)

    # Redefine object to the variant we expect
    object = Variant((Object(INamedEntity),
                      Object(IActivity),
                      Object(IStatementRef),
                      Object(ISubStatement),),
                     title=u'The thing that was acted on.',
                     required=True)

    result = Object(IResult,
                    title=u'Result Object, further details representing a measured outcome.',
                    required=False)

    stored = ValidDatetime(title=u'Timestamp of when this Statement was recorded. Set by LRS.',
                           required=False,
                           readonly=True)
    stored.setTaggedValue('_ext_allow_initial_set', True)

    authority = Object(INamedEntity,
                       title=u'Agent or Group who is asserting this Statement is true.',
                       required=False)


class IStatementList(IXAPIBase):

    statements = ListOrTuple(title=u'statements',
                             description=u'The Statements',
                             required=True,
                             value_type=Object(IStatement),
                             default=())

    def __iter__():
        """
        Return an iterable with the statements in this list
        """


class IStatementResult(IStatementList):

    more = ValidTextLine(title=u'more',
                         description=u'URL retrieve more statements',
                         required=False)


class ILRSClient(interface.Interface):
    """
    LRS Client
    """

    # about

    def about():
        """
        Gets about response from LRS

        :return: The returned About object
        :rtype: :class:`nti.xapi.interfaces.IAbout`
        """

    # statements

    def save_statement(statement):
        """
        Save statement to LRS and update statement id if necessary

        :param statement: Statement object to be saved
        :type statement: :class:`nti.xapi.interfaces.IStatement`
        :return: The saved statement
        :rtype: :class:`nti.xapi.interfaces.IStatement`
        """

    def save_statements(statements):
        """
        Save statements to LRS and update their statement id's

        :param statements: A list of statement objects to be saved
        :type statements: :class:`nti.xapi.interfaces.IStatementList`
        :return: The saved list of statements
        :rtype: :class:`nti.xapi.interfaces.IStatementList`
        """

    def retrieve_statement(statement_id):
        """
        Retrieve a statement from the server from its id

        :param statement_id: The UUID of the desired statement
        :type statement_id: str
        :return: The retrieved statement
        :rtype: :class:`nti.xapi.interfaces.IStatement`
        """

    def retrieve_voided_statement(statement_id):
        """
        Retrieve a voided statement from the server from its id

        :param statement_id: The UUID of the desired voided statement
        :type statement_id: str
        :return: The retrieved voided statement
        :rtype: :class:`nti.xapi.interfaces.IStatement`
        """

    def query_statements(query):
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

    def more_statements(more_url):
        """
        Query the LRS for more statements

        :param more_url: URL from a StatementsResult object used to retrieve more statements
        :type more_url: str
        :return: The returned StatementsResult object
        :rtype: :class:`nti.xapi.interfaces.IStatementResult`
        """

    # states

    def retrieve_state_ids(activity, agent, registration=None, since=None):
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

    def retrieve_state(activity, agent, state_id, registration=None):
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

    def save_state(state):
        """
        Save a state doc to the LRS

        :param state: State document to be saved
        :type state: :class:`nti.xapi.documents.interfaces.IStateDocument`
        :return: State document
        """

    def delete_state(state):
        """
        Delete a specified state from the LRS

        :param state: State document to be deleted
        :type state: :class:`nti.xapi.documents.interfaces.IStateDocument`
        :return: True if the state was deleted
        :rtype: bool
        """

    def clear_state(activity, agent, registration=None):
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

    # activity profiles

    def retrieve_activity_profile_ids(activity, since=None):
        """
        Retrieve activity profile id(s) with the specified parameters

        :param activity: Activity object of desired activity profiles
        :type activity: :class:`nti.xapi.interfaces.IActivity`
        :param since: Retrieve activity profile id's since this time
        :type since: str
        :return: List of retrieved activity profile ids
        """

    def retrieve_activity_profile(activity, profile_id):
        """
        Retrieve activity profile with the specified parameters

        :param activity: Activity object of the desired activity profile
        :type activity: :class:`nti.xapi.interfaces.IActivity`
        :param profile_id: UUID of the desired profile
        :type profile_id: str
        :return: Activity profile doc
        :rtype: :class:`nti.xapi.interfaces.IActivityProfileDocument`
        """

    def save_activity_profile(profile):
        """
        Save an activity profile doc to the LRS

        :param profile: Activity profile doc to be saved
        :type profile: :class:`nti.xapi.interfaces.IActivityProfileDocument`
        :return: The saved activity profile doc
        :rtype: :class:`nti.xapi.interfaces.IActivityProfileDocument`
        """

    def delete_activity_profile(profile):
        """
        Delete activity profile doc from LRS

        :param profile: Activity profile document to be deleted
        :type profile: :class:`nti.xapi.interfaces.IActivityProfileDocument`
        :return: True if object was deleted
        :rtype: bool
        """

    # agent profiles

    def retrieve_agent_profile_ids(agent, since=None):
        """
        Retrieve agent profile id(s) with the specified parameters

        :param agent: Agent object of desired agent profiles
        :type agent: :class:`nti.xapi.interfaces.IAgent`
        :param since: Retrieve agent profile id's since this time
        :type since: str
        :return: List of retrieved agent profile ids
        """

    def retrieve_agent_profile(agent, profile_id):
        """
        Retrieve agent profile with the specified parameters

        :param agent: Agent object of the desired agent profile
        :type agent: :class:`nti.xapi.interfaces.IAgent`
        :param profile_id: UUID of the desired agent profile
        :type profile_id: str
        :return: An agent profile document
        :rtype: :class:`nti.xapi.interfaces.IAgentProfileDocument`
        """

    def save_agent_profile(profile):
        """
        Save an agent profile doc to the LRS

        :param profile: Agent profile doc to be saved
        :type profile: :class:`nti.xapi.documents.interfaces.IAgentProfileDocument`
        :return: The saved agent profile doc
        :rtype: :class:`nti.xapi.documents.interfaces.IAgentProfileDocument`
        """

    def delete_agent_profile(profile):
        """
        Delete agent profile doc from LRS

        :param profile: Agent profile document to be deleted
        :type profile: :class:`nti.xapi.interfaces.IAgentProfileDocument`
        :return: True if object was deleted
        :rtype: bool
        """
