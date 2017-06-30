import inning as inn
import pandas as pd
import pickers as pic


def create_match_summaries_frame(match_summaries):
    """Convert a series of match summaries into a data frame."""
    match_infos = []
    for match in match_summaries:
        match_info = pic.pick_match_info(match)
        match_info['dates'] = pd.to_datetime(match_info['dates'][0])
        match_info['team.home'], match_info['team.away'] = match_info.pop('teams')

        toss = match_info.pop('toss')
        match_info['toss.winner'] = toss['winner']
        match_info['toss.decision'] = toss['decision']
        match_info.update(flat_match_outcome(match_info.pop('outcome')))
        for inning in pic.pick_innings(match):
            add_inning_to_match_info(inning, match_info)

        match_infos.append(match_info)

    df = pd.DataFrame(match_infos)
    df.set_index(['dates', 'team.home', 'team.away'], inplace=True)

    # create hierarchical column index
    # df.columns = pd.MultiIndex.from_tuples([tuple(c.split('.')) for c in df.columns])
    col_order = partial_reorder_columns(df)
    # reindex the dataframe with new column order
    df = df.reindex(columns=col_order)

    return df


def add_inning_to_match_info(innings, match_info):
    inning_name, inning_data = innings.items()[0]
    match_info[inning_data['team']] = inn.create_innings_dataframe(inning_data)
    match_info[inning_name] = inn.inning_summary(match_info[inning_data['team']],
                                                 inning_data['team'])
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
