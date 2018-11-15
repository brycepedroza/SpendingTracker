from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from apiclient import errors
import os


class GmailClient(object):

    def __init__(self, label):
        self.scopes = 'https://www.googleapis.com/auth/gmail.readonly'
        self.label = label
        self.token_path = 'SpendingTracker/token.json'
        self.cred_path = 'credentials.json'

    @staticmethod
    def get_message(service, user_id, msg_id):
        """
        Get a Message with given ID.
        :param service: Authorized gmail api service instance
        :param user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user
        :param msg_id: THE ID of the message required
        :return: a list containing each line of the email
        """

        try:
            message = service.users().messages().get(userId=user_id, id=msg_id,
                                                     format='full').execute()
            try:
                body = message['payload']['parts'][0]['parts'][0]\
                ['parts'][0]['body']['data']
            except Exception as e:
                print("Something went wrong: {}".format(e))
                return []

            msg_str = base64.b64decode(body).decode('utf8')
            msg_str = msg_str.replace('\r', ' ').replace('\n \n', '\n').split('\n')
            return msg_str
        except errors.HttpError() as e:
            print('An error occurred: %s' % e)

    def get_label(self, labels: list) -> str:
        """
        searches for the label name from a list and returns its ID
        :param labels:
        :return: str of the ID
        """
        for label in labels:
            if label['name'] == self.label:
                return label.get('id')
        raise Exception('Could not find {} in the list of labels'
                        .format(self.label))

    def check_email(self):
        """
        grabs the first email in the label specified and returns it in
        list format by lines breaks
        """
        store = file.Storage(self.token_path)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(self.cred_path, self.scopes)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))

        # Call the Gmail API
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        label_id = self.get_label(labels)
        response = service.users().messages() \
            .list(userId='me', labelIds=[label_id], maxResults=1).execute()
        print(response['messages'][0]['id'])
        return GmailClient.get_message(service, 'me',
                                       response['messages'][0]['id'])

