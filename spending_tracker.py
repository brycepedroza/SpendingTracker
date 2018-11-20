from SpendingTracker.clients.gmail_client.gmail_client import GmailClient
from SpendingTracker.actions.gmail_actions import gmail_logic

gc = GmailClient('banking')
email = gc.check_email()
gmail_info = gmail_logic.read_email(email)
print(gmail_info)