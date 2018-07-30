#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import has_entries
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import verifiably_provides

import unittest

from zope.schema.interfaces import ValidationError

from nti.externalization.externalization import to_external_object

from nti.externalization.internalization import update_from_external_object

from nti.xapi.interfaces import IAgent
from nti.xapi.interfaces import IStatement
from nti.xapi.interfaces import IStatementRef
from nti.xapi.interfaces import ISubStatement
from nti.xapi.interfaces import IStatementResult

from nti.xapi.statement import Statement
from nti.xapi.statement import StatementRef
from nti.xapi.statement import SubStatement
from nti.xapi.statement import StatementResult

from nti.xapi.tests import SharedConfiguringTestLayer


class TestStatementRef(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def data(self):
        return {
            "objectType": "StatementRef",
            "id": "e05aa883-acaf-40ad-bf54-02c8ce485fb0"
        }

    def setUp(self):
        self.ref = StatementRef()
        update_from_external_object(self.ref, self.data)

    def validate_statement_ref(self, ref):
        assert_that(ref, verifiably_provides(IStatementRef))
        assert_that(ref,
                    has_property('id', 'e05aa883-acaf-40ad-bf54-02c8ce485fb0'))

    def test_creation(self):
        self.validate_statement_ref(self.ref)

    def test_externalization(self):
        assert_that(to_external_object(self.ref), is_(self.data))

    def test_internalization(self):
        ref = StatementRef()
        update_from_external_object(ref, self.data)
        self.validate_statement_ref(ref)


class TestStatement(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def data(self):
        return {
            "id": "7ccd3322-e1a5-411a-a67d-6a735c76f119",
            "timestamp": "2015-12-18T12:17:00+00:00",
            "actor": {
                "objectType": "Agent",
                "name": "Example Learner",
                "mbox": "mailto:example.learner@adlnet.gov"
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/attempted",
                "display": {
                    "en-US": "attempted"
                }
            },
            "object": {
                "id": "http://example.adlnet.gov/xapi/example/simpleCBT",
                "definition": {
                    "name": {
                        "en-US": "simple CBT course"
                    },
                    "description": {
                        "en-US": "A fictitious example CBT course."
                    }
                }
            },
            "result": {
                "score": {
                    "scaled": 0.95
                },
                "success": True,
                "completion": True,
                "duration": "PT1234S"
            },
            "attachments": [{
                "usageType": "http://adlnet.gov/expapi/attachments/signature",
                "display": {"en-US": "Signature"},
                "description": {"en-US": "A test signature"},
                "contentType": "application/octet-stream",
                "length": 4235,
                "sha2": "672fa5fa658017f1b72d65036f13379c6ab05d4ab3b6664908d8acf0b6a0c634"
            }]
        }

    def setUp(self):
        self.statement = Statement()
        update_from_external_object(self.statement, self.data)

    def validate_statement(self, statement):
        assert_that(statement, verifiably_provides(IStatement))
        assert_that(statement,
                    has_property('id', is_('7ccd3322-e1a5-411a-a67d-6a735c76f119')))
        assert_that(statement,
                    has_property('attachments', has_length(1)))

    def test_statement(self):
        self.validate_statement(self.statement)

    def test_externalization(self):
        external = to_external_object(self.statement)
        assert_that(external,
                    has_entries('id', '7ccd3322-e1a5-411a-a67d-6a735c76f119'))

    def test_timestamp_optional(self):
        d = self.data
        d.pop('timestamp')
        stmt = Statement()
        update_from_external_object(stmt, d)
        assert_that(stmt, verifiably_provides(IStatement))

    def test_ambiguous_actor(self):
        stmt_data = {
            "timestamp": "2015-12-18T12:17:00Z",
            "actor": {
                "name": "Example Learner",
                "mbox": "mailto:example.learner@adlnet.gov"
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/attempted",
                "display": {
                    "en-US": "attempted"
                }
            },
            "object": {
                "id": "http://example.adlnet.gov/xapi/example/simpleCBT",
                "definition": {
                    "name": {
                        "en-US": "simple CBT course"
                    },
                    "description": {
                        "en-US": "A fictitious example CBT course."
                    }
                }
            }
        }
        stmt = Statement()
        update_from_external_object(stmt, stmt_data)
        assert_that(stmt.actor, verifiably_provides(IAgent))

    def test_no_object_type(self):
        assert_that(self.statement, does_not(has_property('objectType', 'Statement')))

class TestSubStatement(TestStatement):

    layer = SharedConfiguringTestLayer

    @property
    def data(self):
        return {
            "timestamp": "2015-12-18T12:17:00Z",
            "actor": {
                "objectType": "Agent",
                "name": "Example Learner",
                "mbox": "mailto:example.learner@adlnet.gov"
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/attempted",
                "display": {
                    "en-US": "attempted"
                }
            },
            "object": {
                "id": "http://example.adlnet.gov/xapi/example/simpleCBT",
                "definition": {
                    "name": {
                        "en-US": "simple CBT course"
                    },
                    "description": {
                        "en-US": "A fictitious example CBT course."
                    }
                }
            }
        }

    def setUp(self):
        self.statement = SubStatement()
        update_from_external_object(self.statement, self.data)

    def validate_statement(self, statement):
        assert_that(statement, verifiably_provides(ISubStatement))

    def test_externalization(self):
        external = to_external_object(self.statement)
        assert_that(external, has_entries('timestamp', '2015-12-18T12:17:00Z',
                                          'actor', has_entry('name', 'Example Learner'),
                                          'verb', has_entry('id', 'http://adlnet.gov/expapi/verbs/attempted'),
                                          'object', has_entry('id', 'http://example.adlnet.gov/xapi/example/simpleCBT')))

    def test_substatements_not_recursive(self):
        with self.assertRaises(ValidationError):
            self.statement.object = SubStatement()

        with self.assertRaises(ValidationError):
            self.statement.object = StatementRef(id='e05aa883-acaf-40ad-bf54-02c8ce485fb0')


class TestStatementResult(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @property
    def statement(self):
        return {
            "id": "7ccd3322-e1a5-411a-a67d-6a735c76f119",
            "timestamp": "2015-12-18T12:17:00+00:00",
            "actor": {
                "objectType": "Agent",
                "name": "Example Learner",
                "mbox": "mailto:example.learner@adlnet.gov"
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/attempted",
                "display": {
                    "en-US": "attempted"
                }
            },
            "object": {
                "id": "http://example.adlnet.gov/xapi/example/simpleCBT",
                "definition": {
                    "name": {
                        "en-US": "simple CBT course"
                    },
                    "description": {
                        "en-US": "A fictitious example CBT course."
                    }
                }
            },
            "attachments": [{
                "usageType": "http://adlnet.gov/expapi/attachments/signature",
                "display": {"en-US": "Signature"},
                "description": {"en-US": "A test signature"},
                "contentType": "application/octet-stream",
                "length": 4235,
                "sha2": "672fa5fa658017f1b72d65036f13379c6ab05d4ab3b6664908d8acf0b6a0c634"
            }]
        }

    @property
    def data(self):
        return {
            "statements": [self.statement],
            "more": "more/1234"
        }

    def test_result(self):
        result = StatementResult()
        update_from_external_object(result, self.data)
        assert_that(result, is_not(none()))
        assert_that(list(result), has_length(1))
        assert_that(result, has_property('more', "more/1234"))
        assert_that(result, has_property('statements', has_length(1)))
