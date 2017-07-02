import math
import numpy as np
import pandas as pd
import pickers as pck


def create_innings_dataframe(number, innings):
    """Given an cricsheet innings convert it into a data frame"""
    delivery_ids, outcomes = split_id_outcome(pck.pick_deliveries(innings))
    # heirarchical index by over and delivery. eg: 4.3 => (4, 3)
    outcome_index = heirarchical_delivery_index(number, delivery_ids)
    # flatten the outcome into columns
    outcome_rows = [flat_delivery_outcome(o) for o in outcomes]

    inning_df = pd.DataFrame(outcome_rows, index=outcome_index)
    if 'rb' in inning_df.columns:
        inning_df.insert(6, 'rb_cum', inning_df.groupby('batsman').rb.cumsum())

    if 're' in inning_df.columns:
        inning_df.insert(7, 're_cum', inning_df.re.cumsum())

    if 'rt' in inning_df.columns:
        # add a cummulative run counter
        inning_df.insert(8, 'rt_cum', inning_df.rt.cumsum())

    inning_df['w_cum'] = 0
    if 'wpo' in inning_df.columns:
        # set the wicket counter = 1 where a person was out
        inning_df.loc[inning_df.wpo.notnull(), 'w_cum'] = 1
    inning_df['w_cum'] = inning_df.w_cum.cumsum()

    return inning_df


def inning_summary(inning_frame, team):
    """Takes a inning data frame and tries to produce a summary of the inning"""
    if len(inning_frame):
        last_ball = inning_frame.iloc[-1]
        rt_cum = last_ball['rt_cum'] if 'rt' in inning_frame.columns else '-'
        w_cum = last_ball['w_cum'] if 'w_cum' in inning_frame.columns else '-'
        return "%s %d/%0s" % (team, rt_cum, w_cum)
    else:
        return "%s -" % (team,)


def split_id_outcome(deliveries):
    """Splits an iterable of deliveries into the [delivery_ids], [outcomes]"""
    # each delivery is a map { delivery_id => outcome }
    # d.items() will return a list of [(k, v)] pairs in the delivery
    # a list of maps is converted into a list of tuples
    id_outcome_tuples = [d.items()[0] for d in deliveries]

    # id_outcome_tuples is essentially a pair of lists zipped together into a
    # list of pairs.
    #
    # zip is its own inverse. i.e. we can unzip a list of pairs using zip
    return zip(*id_outcome_tuples)


def heirarchical_delivery_index(inum, delivery_ids):
    """Given a list of delivery ids of the form Over.ball, converts it into a
    2-level pandas Index with overs and balls"""
    # unzip a list of pairs into a pair of lists
    balls, overs = zip(*[math.modf(did) for did in delivery_ids])
    balls = [round(b, 1) for b in balls]
    # construct the 2d index
    index = pd.MultiIndex.from_arrays([np.array([inum]*len(balls)), np.array(overs), np.array(balls)], names=['inning', 'over', 'ball'])
    return index


def flat_delivery_outcome(do):
    flat_do = do.copy()
    if 'runs' in flat_do:
        flat_do['rb'] = flat_do['runs']['batsman']
        flat_do['re'] = flat_do['runs']['extras']
        flat_do['rt'] = flat_do['runs']['total']
        flat_do.pop('runs')
    if 'wicket' in flat_do:
        flat_do['wk'] = flat_do['wicket']['kind']
        flat_do['wpo'] = flat_do['wicket']['player_out']
        if 'fielders' in flat_do['wicket']:
            flat_do['wf'] = flat_do['wicket']['fielders']

        flat_do.pop('wicket')
    if 'extras' in flat_do:
        flat_do.pop('extras', None)

    return flat_do
