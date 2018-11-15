from SpendingTracker.clients.gmail_client.gmail_client import GmailClient

gc = GmailClient('banking')
print(gc.check_email())
pass