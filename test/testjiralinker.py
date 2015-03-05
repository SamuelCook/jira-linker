#!/usr/bin/env python

import unittest

from plugins.jiralinker import *
from collections import namedtuple


class TestJiraIdFinder(unittest.TestCase):
    def test_no_matches_when_no_jira_ids(self):
        jirakey = "ABC"
        message = "This message does not contain the key of any JIRA issue."
        parser = JiraIdFinder([jirakey], message)
        jiraids = parser.find_jira_ids()

        self.assertEquals(0, len(jiraids))

    def test_includes_jira_id(self):
        jirakey = "ABC"
        input_jira_id = jirakey + "-1234"
        message = "This message " + input_jira_id + " is the key of a JIRA issue."

        parser = JiraIdFinder([jirakey], message)
        jiraids = parser.find_jira_ids()

        self.assertEquals([input_jira_id], jiraids)

    def test_supports_multiple_jira_ids(self):
        jirakey = "ABC"
        input_jira_id1 = jirakey + "-1234"
        input_jira_id2 = jirakey + "-5678"

        message = "This message " + input_jira_id1 + " is the key of a JIRA issue and so is " + input_jira_id2 + "."

        parser = JiraIdFinder([jirakey], message)
        jiraids = parser.find_jira_ids()

        self.assertEquals([input_jira_id1, input_jira_id2], jiraids)

    def test_includes_only_one_result_for_duplicate_jira_ids(self):
        jirakey = "ABC"
        input_jira_id1 = jirakey + "-1234"
        input_jira_id2 = jirakey + "-5678"

        message = "This message " + input_jira_id1 + " is the key of JIRA issue " + input_jira_id1 + "."

        parser = JiraIdFinder([jirakey], message)
        jiraids = parser.find_jira_ids()

        self.assertEquals([input_jira_id1], jiraids)

    def test_supports_multiple_jira_ids_with_different_keys(self):
        jirakey1 = "ABC"
        input_jira_id1 = jirakey1 + "-1234"

        jirakey2 = "XYZ"
        input_jira_id2 = jirakey2 + "-1234"

        message = "This message " + input_jira_id1 + " is the key of a JIRA issue and so is " + input_jira_id2 + "."

        parser = JiraIdFinder([jirakey1, jirakey2], message)
        jiraids = parser.find_jira_ids()

        self.assertEquals([input_jira_id1, input_jira_id2], jiraids)

    def test_results_come_out_in_the_right_order(self):
        jirakey = "ABC"
        input_jira_ids = ["ABC-1", "ABC-2", "ABC-3", "ABC-4", "ABC-5", "ABC-6", "ABC-7", "ABC-8", "ABC-9"]

        message = " ".join(input_jira_ids)

        parser = JiraIdFinder([jirakey], message)
        actual_jira_ids = parser.find_jira_ids()

        self.assertEquals(input_jira_ids, actual_jira_ids)


class TestJiraIssueFormatter(unittest.TestCase):
    def create_sample_issue(self, key, statusname, summary, url, assigneename=None):
        def issue_permalink():
            return url

        class Fields(namedtuple('Fields', 'summary status assignee')):
            # noinspection PyInitNewSignature
            def __new__(cls, summary, status, assignee=None):
                return super(Fields, cls).__new__(cls, summary, status, assignee)

        Issue = namedtuple('Issue', 'key fields permalink')
        Assignee = namedtuple('Assignee', 'displayName')
        Status = namedtuple('Status', 'name')

        status = Status(name=statusname)

        if assigneename is not None:
            fields = Fields(summary=summary, status=status, assignee=Assignee(displayName=assigneename))
        else:
            fields = Fields(summary=summary, status=status)

        issue = Issue(key=key, fields=fields, permalink=issue_permalink)

        return issue

    def test_jira_issue_formatting(self):
        key = "JIRA-123"
        summary = "My JIRA Summary"
        assigneename = "Mr. Assignee"
        url = "http://example.org/example"
        statusname = "A Status"

        issue = self.create_sample_issue(key, statusname, summary, url, assigneename)

        expectedoutput = key + ": " + summary + ". [Assignee: " + assigneename + "] [" + statusname + "]\n" + url

        formatter = JiraIssueFormatter(issue)
        actualoutput = formatter.format()

        self.assertEquals(expectedoutput, actualoutput)

    def test_formatting_with_no_assignee(self):
        key = "JIRA-123"
        summary = "My JIRA Summary"
        url = "http://example.org/example"
        statusname = "A Status"

        issue = self.create_sample_issue(key, statusname, summary, url)

        expectedoutput = key + ": " + summary + ". [Unassigned] [" + statusname + "]\n" + url

        formatter = JiraIssueFormatter(issue)
        actualoutput = formatter.format()

        self.assertEquals(expectedoutput, actualoutput)

    def test_some_stuff(self):
        os.environ['DEBUG'] = 'true'
        os.environ['BOT_USER_ID'] = 'me'
        os.environ['JIRA_KEYS'] = 'BKR'
        os.environ['JIRA_SERVER_URI'] = 'http://localhost'
        os.environ['JIRA_USERNAME'] = 'me@elasticpath.com'
        os.environ['JIRA_PASSWORD'] = 'secr3t'
        data = {}
        process_message(data)

if __name__ == '__main__':
    unittest.main()