#!/usr/bin/env python

import re
import os
import logging

from jira import JIRA
from jira import JIRAError


outputs = []


def process_message(data):
    # Used to ignore the bot's own messages (and to avoid being stuck in a loop)
    this_bot_user_id = os.environ['BOT_USER_ID']

    logging.debug("Received data:")
    logging.debug(data)

    if 'user' in data and data['user'] == this_bot_user_id:
        logging.debug("Ignoring own message.")
        return

    if 'channel' not in data:
        logging.info("Cannot process message: no channel present in received data.")
        return

    if 'text' not in data:
        logging.info("Cannot process message: no text present in received data.")
        return

    jirakeys = os.environ['JIRA_KEYS'].split()
    channel = data['channel']
    message = data['text']

    idfinder = JiraIdFinder(jirakeys, message)
    client = JiraClient(os.environ['JIRA_SERVER_URI'], os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD'])

    ids = idfinder.find_jira_ids()
    for id in ids:
        issue = client.lookup_jira_issue(id)

        if issue is not None:
            response = JiraIssueFormatter(issue).format()
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

        return remove_duplicates(jiraids)


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


class JiraIssueFormatter(object):
    def __init__(self, issue):
        self.issue = issue

    def format(self):
        summary = self.issue.fields.summary

        if self.issue.fields.assignee is None:
            assignee = "[Unassigned]"
        else:
            assignee = "[Assignee: " + self.issue.fields.assignee.displayName + "]"

        url = self.issue.permalink()
        status = self.issue.fields.status.name

        response = self.issue.key + ": " + summary + ". " \
                   + assignee \
                   + " [" + status + "]\n" \
                   + url
        return response


def remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]