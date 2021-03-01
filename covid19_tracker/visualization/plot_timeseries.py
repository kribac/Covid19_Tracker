import pandas as pd
import json
from datetime import datetime
from textwrap import dedent
import bokeh.plotting
import bokeh.models
from bokeh.layouts import column, layout
from bokeh.palettes import Category10
import itertools

from covid19_tracker.data_handling import ProcessAGSData, LKname_to_ags
AGS_DEFINITION = "../../ags.json"  # DUplicate

OUTPUT_HTML_PATH = f"../../plots/plot-lk-tmp.html"

def setCommonBokehFigProps(fig):
    fig.xaxis.axis_label = "Date"
    fig.yaxis.axis_label = "cumulative number of confirmed cases"
#    fig.xaxis.ticker.desired_num_ticks = 15
    fig.xaxis.formatter = bokeh.models.DatetimeTickFormatter(days=["%b-%d"])
    fig.xaxis.major_label_orientation = 3.1415 / 4 + 0.5
#    fig.y_range.start = 0
#    fig.title.text_font_size = "10px"


def color_gen():
    yield from itertools.cycle(Category10[10])
color = color_gen()

def plot_lk_lines(df, ags_dict, ags_list):

    fig = bokeh.plotting.figure(
        title=f"cumulative COVID-19 case count over time (linear)",
        x_axis_type = "datetime",
        toolbar_location = None,
        background_fill_color = "#eeeeee",
    )

    for ags in ags_list:
        ags_info = ags_dict[ags]
        fig.line(
            "time",
            ags,
            color = next(color),
            line_width=1,
            legend_label = ags_info["name"],
            source = bokeh.models.ColumnDataSource(data=df)
        )

    setCommonBokehFigProps(fig)
    fig.legend.location = "top_left"
    #figlin.y_range.end = df[ags].max() * 1.3
    return fig




def main():


    data_processor = ProcessAGSData()

    # load AGS info: dictionary (keys=ags ids) with Landkreis infos
    with open(AGS_DEFINITION, "rb") as f:
        ags_dict = json.loads( f.read().decode("utf-8") )

    print(ags_dict)

    df = data_processor.load_data(start_date=None)
    df = data_processor.get_daily_case_change_rolling(df, win_len_days=7, sum_over_win=True)

    # print(df.tail)

    lk_names = ["LK Südliche Weinstraße",
                "LK Rhein-Neckar-Kreis",
                "LK Bad Dürkheim",
                "LK Germersheim",
                ]
    ags_list = [LKname_to_ags(ags_dict, lk_name) for lk_name in lk_names]
    print(ags_list)
    #ags, info = LKname_to_ags(ags_dict, lk_name)
    #print(ags)
    #print(info)
    #ags_list = [ags]
    #print(df[ags])

    #---- plot cases

    preamble_text = dedent(f""" confirmed COVID-19 cases for Landkreise""")
    bokeh.plotting.output_file(OUTPUT_HTML_PATH)
    preamble = bokeh.models.Div(text=preamble_text, height=120)

    fig_line = plot_lk_lines(df, ags_dict, ags_list)

    bokeh.plotting.save(
        column( preamble, fig_line,
                        #sizing_mode="stretch_both",
                        max_width=9000
                ),
        browser="firefox",
    )



if __name__=="__main__":

    main()

