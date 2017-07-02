"""
picking different elements from cricheet objects
"""


def pick_match_info(match_summary):
    return match_summary['info']


def pick_innings(match_summary):
    return match_summary['innings']


def pick_innings_num_name_data(innings):
    """Given a cricsheet inning object, return the inning
        (number, name, delivery_data)
    """
    innings_name, innings_data = innings.items()[0]
    inum = 1 if innings_name.split(' ')[0] == '1st' else 2
    return (inum, innings_name, innings_data)


def pick_1st_innings(match_summary):
    return pick_innings(match_summary)[0]['1st innings']


def pick_2nd_innings(match_summary):
    return pick_innings(match_summary)[1]['2nd innings']


def pick_deliveries(innings):
    return innings['deliveries']


def pick_winner(pick_from):
    return pick_from['winner']
