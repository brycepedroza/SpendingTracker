from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from apiclient import errors

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
MYLABEL = "banking"


def get_message(service, user_id, msg_id):
    """
    Get a Message with given ID.
    :param service: Authorized gmail api service instance
    :param user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user
    :param msg_id: THE ID of the message required
    :return: a message
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


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    label_to_check = get_label(MYLABEL, labels)
    response = service.users().messages() \
        .list(userId='me', labelIds=[label_to_check],maxResults=2).execute()
    print(response['messages'][0]['id'])
    get_message(service, 'me', response['messages'][0]['id'])
    # get_mime_message(service, 'me', response['messages'][0]['id'])
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])


def get_label(label_name: str, labels: list) -> str:
    """
    searches for the label name from a list and returns its ID
    :param label_name:
    :param labels:
    :return: str of the ID
    """
    for label in labels:
        if label['name'] == label_name:
            return label['id']
    raise Exception('Could not find {} in the list of labels'
                    .format(label_name))


if __name__ == '__main__':
    main()
