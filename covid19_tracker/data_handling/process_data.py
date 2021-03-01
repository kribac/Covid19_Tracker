import numpy as np
import pandas as pd
import json

AGS_DEFINITION = "../../ags.json"
AGS_CSV_RL = 'https://raw.githubusercontent.com/jgehrcke/covid-19-germany-gae/master/cases-rl-crowdsource-by-ags.csv'




def LKname_to_ags(ags_dict, lk_name):
    for ags in ags_dict.keys():
        if ags_dict[ags]["name"] == lk_name:
            return ags


def populationGer(ags_dict):
    # Get total population (GER): skip AGSs that do not have the populuation
    # key set (expected for AGS 3152 "LK Göttingen (alt)". Minus the total for
    # Berlin, because Berlin is represented twice, on purpose.
    TOTAL_POPULATION_GER = (
            sum(v["population"] for k, v in ags_dict.items() if "population" in v)
            - ags_dict["11000"]["population"]
    )
    return TOTAL_POPULATION_GER

class ProcessAGSData:

    def __init__(self):
        self.source = "risklayer"
        self.csv_file = AGS_CSV_RL
        self.start_date = "2020-03-10"
        self.cases_per_100k = True

        with open(AGS_DEFINITION, "rb") as f:
            self.ags_dict = json.loads(f.read().decode("utf-8"))
        self.population_germany = populationGer(self.ags_dict)




    def load_data(self, start_date=None):

        if start_date is None:
            start_date = self.start_date


        df = pd.read_csv(
            self.csv_file,
            index_col=["time_iso8601"],  # row label
            parse_dates=["time_iso8601"],  # what does this do?
            date_parser=lambda col: pd.to_datetime(col, utc=True),
        )
        df = df[start_date:]

        df.index.name = "time"
        return df

    def get_daily_case_change_rolling(self, df, win_len_days=1, sum_over_win=False):
        """ currently, the daily change can also be negative -> this is not equivalent as new cases"""

        df = df.resample('1D').pad()
        # careful: there was an incidence in risklayer data, where date entries were not monotonous!

        # convert time stamps to deltas in seconds
        dt_seconds = pd.Series(df.index).diff().dt.total_seconds()
        # series with time differences in days
        dt_days = pd.Series(dt_seconds) / 86400.0
        # add original time stamps as index to new series
        dt_days.index = df.index

        # calculate the change in cases per day
        # diff computes the differences in values of each entry in df
        # div divides this by the time differences in days between the values in df
        df_case_change_per_day = df.diff().div(dt_days, axis=0)

        windowed = df_case_change_per_day.rolling(window="%sD" % win_len_days)
        if sum_over_win:
            df_out = windowed.sum()
        else:
            df_out = windowed.sum() / win_len_days

        return df_out


    def normalize_100K(self, df):

        for ags in df:
            #print(f"{ags}: {self.ags_dict[ags]}")
            if ags == "sum_cases":
                population = self.population_germany
            else:
                population = self.ags_dict[ags]['population']
            print(population)
            print(df[ags])
            df[ags] = df[ags] / population * 100000
            print(df[ags])
        return df

