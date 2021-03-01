import pandas as pd
import json
from datetime import datetime
from textwrap import dedent
import geopandas as gpd
import seaborn
import itertools
import matplotlib.pyplot as plt

from covid19_tracker.data_handling import ProcessAGSData, LKname_to_ags
AGS_DEFINITION = "../../ags.json"  # DUplicate

DE_GEODATA_FILE = "../../geodata/DE-counties.geojson"


def addDataToMap(geodata, data, dataindex=-1):

    print("ok")
    print(f"{len(geodata)} rows found")
    n_rows = len(geodata)
    cases = []
    for i in range(n_rows):
        ags = geodata.iloc[i]["AGS"]
        data_value = data.iloc[dataindex].loc[str(int(ags))] # get case value of selected row (=dataindex) of current county. in data, we don't want leading zeros in ags number.
        print(f"AGS: {ags} - value: {data_value}")
        cases.append(data_value)
        #geodata.iloc[i]["cases"] = data_value
    geodata["cases"] = cases
    return geodata


def plot_map(geodata, cases, ax, index=-1):
    """ plot LK case map for one time index (-1-> last row)"""

    geo_de = addDataToMap(geodata, cases, index)
    print(geo_de.tail)

    geo_de.plot(
        ax = ax,
        column = "cases",
        alpha = 0.7,
        edgecolor = "#555",
        categorical = False,
        legend = False,
        #title = f"index={index}",
        #cmap = "autumn_r",
        cmap = seaborn.color_palette("rocket_r", as_cmap=True),
    )
    ax.set_title(f"index={index}")
    #plt.show()

def main():


    data_processor = ProcessAGSData()

    # load AGS info: dictionary (keys=ags ids) with Landkreis infos
    with open(AGS_DEFINITION, "rb") as f:
        ags_dict = json.loads( f.read().decode("utf-8") )
    #print(ags_dict)

    df = data_processor.load_data(start_date=None)
    df = data_processor.get_daily_case_change_rolling(df, win_len_days=7, sum_over_win=True)
    df = data_processor.normalize_100K(df)

    # print(df.tail)
    #print(df.tail)




    #---- plot cases
    geo_de = gpd.read_file(DE_GEODATA_FILE)
    #print(geo_de.head)
    #print(geo_de.iloc[0])
    ax = plt.axes()
    for time_index in range(-20,0):
        #ax.clear()
        #plt.clf()
        print(time_index)
        plot_map(geo_de, df, ax, time_index)
        #plt.title(f"index: {time_index}")
        plt.pause(1)

    plt.show()




if __name__=="__main__":

    main()

