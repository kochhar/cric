import inning as inn
import pandas as pd
import pickers as pic

PROPAGATION_COLS = ['venue', 'city', 'neutral_venue', 'match_type', 'overs',
                    'umpires', 'toss.winner', 'toss.decision', 'supersubs']


def create_match_summaries_frame(match_summaries):
    """Convert an interable of match summaries in cricsheet format into a
    data frame.

    The dataframe has each match as a row. The columns of the frame represent
    the attributes of the match. Each match will have two teams. There will be
    two columns of the dataframe with the names of the teams. These columns
    will contain a sub-dataframe representing the teams' innings in the match
    """
    match_infos = []
    for match in match_summaries:
        match_info = pic.pick_match_info(match)
        match_info['dates'] = pd.to_datetime(match_info['dates'][0])
        match_info['team.home'], match_info['team.away'] = match_info.pop('teams')

        toss = match_info.pop('toss')
        match_info['toss.winner'] = toss['winner']
        match_info['toss.decision'] = toss['decision']
        match_info.update(flat_match_outcome(match_info.pop('outcome')))

        for innings in pic.pick_innings(match):
            inum, innings_name, innings_data = pic.pick_innings_num_name_data(innings)
            team_name = innings_data['team']
            match_info[team_name] = inn.create_innings_dataframe(inum, innings_data)
            match_info[innings_name] = inn.inning_summary(match_info[team_name], team_name)

        match_infos.append(match_info)

    df = pd.DataFrame(match_infos)
    df.set_index(['dates', 'team.home', 'team.away'], inplace=True)

    # create hierarchical column index
    # df.columns = pd.MultiIndex.from_tuples([tuple(c.split('.')) for c in df.columns])
    col_order = partial_reorder_columns(df)
    # reindex the dataframe with new column order
    df = df.reindex(columns=col_order)

    return df


def flat_match(date, home, away, match_s):
    """Given a match dataframe (such as one from a row of
    create_match_summaries_frame), flatten it into a delivery-by-delivery frame.
    The match data is denormalised into every delivery of both the innings.

    Params:
      date: the date when the match was played
      home: the home team name
      away: the away team name
      match_s: a Series with data for a single match

    Returns:
      dataframe. rows are deliveries, columns are delivery details and match details
    """
    home_inning = match_s[home]
    away_inning = match_s[away]

    # figure out the first inning and second inning
    first_team = match_s['1st innings'].split(' ')[0]
    first_inning = home_inning if home == first_team else away_inning
    second_inning = away_inning if home == first_team else home_inning

    first_inning = merge_match_into_inning(date, home, away, match_s, first_inning, first=True)
    second_inning = merge_match_into_inning(date, home, away, match_s, second_inning, first=False)
    return pd.concat([first_inning, second_inning], axis=0)


def merge_match_into_inning(date, home, away, match_s, inning, first=True, match_cols=None):
    """Merge a Series representing information about a `match` played on `date`
    between `home` and `away` into all the deliveries of an `inning`. The
    optional params first and match_cols tweak the data based on whether
    the innings is the first or second inning.

    Params:
      first: True if this is the first inning, will not add first inning result
             into the columns. Default is True
      match_cols: Set of columns from the match info to propagate into the
             inning data. By default will use PROPAGATION_COLS from this module
    """
    if not match_cols: match_cols = list(PROPAGATION_COLS)
    # if this is the second innings, add the 1st innings score to the columns
    if not first: match_cols[-2] = '1st innings'

    # select the columns from the match which we want to keep
    match_s = match_s[match_cols]

    # create a frame of the match data projected for every row in the inning
    match_project = pd.DataFrame(data=[match_s.values]*len(inning), columns=match_s.index,
                                 index=inning.index)

    # add the date and teams into the projection frame
    match_project.insert(0, 'date', date)
    match_project.insert(1, 'team.home', home)
    match_project.insert(2, 'team.away', away)

    # perform the frame merge: inning and the match. both frames are indexed by
    # the deliveries
    inning = inning.merge(match_project, left_index=True, right_index=True)

    # now move the date and teams into the merged index
    # save the original index levels.
    index_levels = inning.index.names
    # add date and team columns into the index
    inning = inning.set_index(['date', 'team.home', 'team.away'], append=True)
    # reorder the index columns (using the saved columns from earlies)
    inning.index = inning.index.reorder_levels(['date', 'team.home', 'team.away'] + index_levels)
    return inning


def add_inning_to_match_info(inning, match_info):
    """Given an inning and some match information add the innings information
    into the match."""
    return match_info


def partial_reorder_columns(df, column_order=None):
    index_cols = 'dates', 'team.home', 'team.away'
    if column_order is None:
        column_order = ['venue', 'city', 'overs', 'umpires',
                        'match_type', 'neutral_venue', 'gender', 'toss.winner', 'toss.decision',
                        'player_of_match']

    reordered_cols = list(df.columns)
    for (new_pos, col_name) in enumerate(column_order):
        # find the current position of the column
        curr_pos = reordered_cols.index(col_name)
        # pop it out of that position and reinsert it in the new position
        reordered_cols.insert(new_pos, reordered_cols.pop(curr_pos))

    return reordered_cols


def flat_match_outcome(outcome):
    """Flattens a match's outcome using dotted notation"""
    flat_outcome = dict()
    if 'winner' in outcome:
        flat_outcome['outcome.result'] = 'win'
        flat_outcome['outcome.winner'] = outcome['winner']
        flat_outcome['outcome.by'] = outcome['by']
    else:
        flat_outcome['outcome.result'] = outcome['result']
        for option in ['bowl_out', 'eliminator', 'method']:
            if option in outcome:
                flat_outcome['outcome.'+option] = outcome[option]

    return flat_outcome
