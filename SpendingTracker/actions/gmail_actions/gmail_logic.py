import re
from dateutil.parser import parse


def read_email(email: str) -> dict:
    """
    the emailed is passed in a per line basis that is parsed and returned
    as a dictionary
    :param email: email as a list
    :return: email information as dictionary
    """
    # remove white spaces
    white_space = re.compile('(  )+( )*')
    email = re.sub(white_space, ' ', email)
    email = email.replace('\r', '').replace('\n\n', '\n').replace(',', '')
    # break down the list by lines
    e_list = email.split('\n')

    body = {}
    i = 0
    balance = withdraw = False
    while i < len(e_list) and not (balance and withdraw):
        if 'balance summary' in e_list[i].lower():
            ending_balance, avail_balance, i = parse_balance(e_list, i + 1)
            body.update({'ending': ending_balance,
                         'available': avail_balance})
            balance = True
        elif 'Withdrawals' in e_list[i]:
            i += 1
            withdrawals = []
            while 'PURCHASE' in e_list[i]:
                withdrawals.append(parse_withdrawal(e_list[i]))
                i += 1
            body.update({'withdrawals': withdrawals})
            withdraw = True
        #  I don't care about deposits right now
        #  i might want to parse them later though
        # elif 'Deposits' in e_list[i]:
        #     i += 1
        #     deposits = []
        #     while len(re.findall('\d+[.]\d\d', e_list[i])) > 0:
        i += 1
    return body


def parse_balance(e_list: list, i: int) -> tuple:
    """
    balance is broken up into ending balance and available balance. This
    function parses through those  two lines
    :param e_list: the email as a list
    :param i: the index that we are at
    :return:ending balance, available balance, and our new index
    """
    money_regex = re.compile('\d+[.]\d\d')
    ending_balance = re.findall(money_regex, e_list[i])
    i += 1  # move to next line  to get available balance
    avail_balance = re.findall(money_regex, e_list[i])
    if len(avail_balance) > 0 and len(ending_balance) > 0:
        return ending_balance[0], avail_balance[0], i
    raise Exception("something went wrong parsing the balance")


def parse_withdrawal(section: str) -> dict:
    """
    parse a transaction to return its important information
    :param section: the line breaking down the transaction
    :return: dict describing the transaction
    """
    # grabbing the key information out of the transaction
    date = re.findall('\d\d[/]\d\d', section)
    pre_loc = re.findall('.*(?=S\d\d\d)', section)
    amount = re.findall('(?<=[$]).*', section)

    if len(date) > 0 and len(pre_loc) > 0 and len(amount) > 0:
        location = pre_loc[0].split(date[0])  # split on the date found
        date = parse(date[0]).date()  # parse the str to a date
        return {'amount': float(amount[0].strip()),
                'location': location[1].strip(),
                'date': date}
    raise Exception('something went wrong parsing the withdrawal')


def parse_deposit() -> dict:
    pass
