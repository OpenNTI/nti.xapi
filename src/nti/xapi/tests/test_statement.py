#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_property
from hamcrest import has_entry
from hamcrest import has_entries


import unittest

from zope.schema.interfaces import ValidationError

from nti.testing.matchers import verifiably_provides

from nti.externalization.internalization import update_from_external_object

from nti.externalization.externalization import to_external_object

from . import SharedConfiguringTestLayer

from ..interfaces import IStatement
from ..interfaces import IStatementRef
from ..interfaces import ISubStatement

from ..statement import StatementRef
from ..statement import SubStatement
       
class TestStatementRef(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def setUp(self):

	self.data = {
	    "objectType":"StatementRef",
	    "id" : "e05aa883-acaf-40ad-bf54-02c8ce485fb0"
	}
	self.ref = IStatementRef(self.data)

    def validate_statement_ref(self, ref):
        assert_that(ref, verifiably_provides(IStatementRef))
        assert_that(ref, has_property('id', 'e05aa883-acaf-40ad-bf54-02c8ce485fb0'))

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

    def setUp(self):
        self.data = {
	    "id":"7ccd3322-e1a5-411a-a67d-6a735c76f119",
	    "timestamp": "2015-12-18T12:17:00+00:00",
	    "actor":{
                "objectType": "Agent",
		"name":"Example Learner",
		"mbox":"mailto:example.learner@adlnet.gov"
	    },
	    "verb":{
		"id":"http://adlnet.gov/expapi/verbs/attempted",
		"display":{
		    "en-US":"attempted"
		}
	    },
	    "object":{
		"id":"http://example.adlnet.gov/xapi/example/simpleCBT",
		"definition":{
		    "name":{
			"en-US":"simple CBT course"
		    },
		    "description":{
			"en-US":"A fictitious example CBT course."
		    }
		}
	    },
	    "result":{
		"score":{
		    "scaled":0.95
		},
		"success": True,
		"completion":True,
		"duration": "PT1234S"
	    }
        }

        self.statement = IStatement(dict(self.data))

    def validate_statement(self, statement):
        assert_that(statement, verifiably_provides(IStatement))
        assert_that(statement, has_property('id', is_('7ccd3322-e1a5-411a-a67d-6a735c76f119')))

    def test_statement(self):
        self.validate_statement(self.statement)

    def test_externalization(self):
        external = to_external_object(self.statement)
        assert_that(external, has_entries('id', '7ccd3322-e1a5-411a-a67d-6a735c76f119'))


class TestSubStatement(TestStatement):

    layer = SharedConfiguringTestLayer

    def setUp(self):
        self.data = {
	    "timestamp": "2015-12-18T12:17:00Z",
	    "actor":{
                "objectType": "Agent",
		"name":"Example Learner",
		"mbox":"mailto:example.learner@adlnet.gov"
	    },
	    "verb":{
		"id":"http://adlnet.gov/expapi/verbs/attempted",
		"display":{
		    "en-US":"attempted"
		}
	    },
	    "object":{
		"id":"http://example.adlnet.gov/xapi/example/simpleCBT",
		"definition":{
		    "name":{
			"en-US":"simple CBT course"
		    },
		    "description":{
			"en-US":"A fictitious example CBT course."
		    }
		}
	    }
        }
        self.statement = ISubStatement(dict(self.data))

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