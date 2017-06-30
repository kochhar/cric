# coding: utf-8
from __future__ import print_function
import glob
import math
import numpy as np
import pandas as pd
import sys
from yaml import load
from yaml import CLoader as Loader

from cric import inning as inn
from cric import pickers as pck


def first_match_first_innings_data_frame(summaries):
    """Takes the first match and converts the first innings into a dataframe"""
    summaries = cric.match_summaries_from_dir('data/t20s')
    m1 = summaries.next()

    # match_info = pick_match_info(m1)
    deliveries = pck.pick_deliveries(pck.pick_1st_innings(m1))
    delivery_ids, delivery_outcomes = zip(*[d.items()[0] for d in deliveries])
    delivery_records = [inn.flat_delivery_outcome(do) for do in delivery_outcomes]

    balls, overs = zip(*[math.modf(did) for did in delivery_ids])
    balls = [round(b, 1) for b in balls]
    index = pd.MultiIndex.from_arrays([np.array(overs), np.array(balls)], names=['over', 'ball'])
    df = pd.DataFrame(delivery_records, index=index)
    df.groupby('over')[['rb', 're', 'rt']].sum()
    return df

