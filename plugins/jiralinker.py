#!/usr/bin/env python

from jira import JIRA
from jira import JIRAError
import re
import os
import sys

outputs = []


def process_message(data):
    jirakeys = os.environ['JIRA_KEYS'].split()
    channel = data['channel']
    message = data['text']

    idfinder = JiraIdFinder(jirakeys, message)
    client = JiraClient(os.environ['JIRA_SERVER_URI'], os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD'])

    ids = idfinder.find_jira_ids()
    for id in ids:
        issue = client.lookup_jira_issue(id)
        if issue is not None:
            summary = issue.fields.summary
            assignee =  issue.fields.assignee.displayName
            url = issue.permalink()
            status = issue.fields.status.name

            response = id + ": " + summary + "." \
                          + "  [Assignee: " + assignee + "]" \
                          + "  [" + status + "]" \
                          + "\n" + url

            outputs.append([channel, response])

class JiraIdFinder(object):
    def __init__(self, jirakeys, message):
        self.jirakeys = jirakeys
        self.message = message

    def find_jira_ids(self):
        jiraids = []
        for key in self.jirakeys:
            p = re.compile('(' + key + '\-\d+)')
            jiraids.extend(p.findall(self.message))

        return frozenset(jiraids)


class JiraClient(object):
    def __init__(self, server_uri, username, password):
        self.server_uri = server_uri
        self.username = username
        self.password = password
        options = {
            'server': self.server_uri
        }

        self.jira = JIRA(options, basic_auth=(self.username, self.password))

    def lookup_jira_issue(self, issueid):
        try:
            return self.jira.issue(issueid)
        except JIRAError:
            pass