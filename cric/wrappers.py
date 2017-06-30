import collections
import numpy as np
import pandas as pd
import pickers as pck


def col_contains(value):
    def cell_contains_value(cell_list):
        return value in cell_list

    return cell_contains_value


class BaseFrame(pd.DataFrame):
    # Overriding the DataFrame constructor so that new instances
    # derived from this class take the type of the subclass
    @property
    def _constructor(self):
        return self.__class__

    # Support the propagation of attributes across  data frames
    # from: https://github.com/pandas-dev/pandas/issues/2485#issuecomment-174577149
    def _combine_const(self, other, *args, **kwargs):
        return super(BaseFrame, self)._combine_const(other, *args, **kwargs).__finalize__(self)


class MatchesFrame(BaseFrame):
    """Compositional wrapper around a dataframe for a number of matches.

    Provides helpers specfic for manipulating cricket match data.
    """
    def filter_team(self, team):
        return self.teams.apply(col_contains(team))

    def filter_umpire(self, umpire):
        return self.umpires.apply(col_contains(umpire))

    def won_matches(self):
        df = self
        won_matches = df[df.outcome.apply(lambda oc: 'winner' in oc)]
        return MatchesFrame(won_matches)

    def toss_winner_won(self):
        df = self.won_matches()
        toss_winner_won = df[df.toss.apply(pck.pick_winner) == df.outcome.apply(pck.pick_winner)]
        return MatchesFrame(toss_winner_won)

    def team_names(self):
        """List of teams who have at least one match in the matches."""
        all_teams = [(t, True) for tpair in self.teams for t in tpair]
        team_names = collections.OrderedDict(all_teams)
        return np.array(team_names.keys())

    def team_innings(self, team_name):
        """Returns a series of innings of the team_name batting"""
        team_innings = [inn1 if inn1.attrs['batting'] == team_name
                        else inn2 if inn2.attrs['batting'] == team_name
                        else np.nan
                        for (inn1, inn2) in zip(self['1st innings_frame'],
                                                self['2nd innings_frame'])]
        return pd.Series(team_innings, index=self.index)
