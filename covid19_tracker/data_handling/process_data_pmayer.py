import pandas as pd
import json

from covid19_tracker.data_handling import LKname_to_ags


DATA_URL = 'https://pavelmayer.de/covid/risks/all-series.csv'
DATA_FILE = '../../data/all-series.csv'
AGS_DEFINITION = "../../ags.json"


if __name__=="__main__":

    data = pd.read_csv(DATA_FILE)
                       #index_col=['Datum'], date_parser=lambda col: pd.to_datetime(col, utc=True))
    data['Datum'] = pd.to_datetime(data['Datum'], format="%d.%m.%Y") # date column after loading is str -> convert to datetime
    data.set_index('Datum', inplace=True)
    print(data.tail())

    ags = 7334 # test: germersheim
    date = pd.to_datetime("17.03.2021", format="%d.%m.%Y")
    # select data for specific LK:
    data_LK = data[ data['IdLandkreis']==7334 ]
    selected_row = data_LK.loc[date]
    #selected_row = data[ (data['Datum']==date) & (data['IdLandkreis']==7334) ]
    #selected_row = data.iloc[date].loc[data['IdLandkreis'] == 7334]

    #print(f"LK: {selected_row.iloc[0].loc['Landkreis']}")
    print(f"LK: {selected_row['Landkreis']}")
    print(f"LK Typ: {selected_row['LandkreisTyp']}")
    print(f"Land: {selected_row['Bundesland']}")
    print(f"Neue Fälle: {selected_row['MeldeTag_AnzahlFallNeu']}")
    print(f"7di Summe: {selected_row['InzidenzFallNeu_7TageSumme']}")


    import plotly.graph_objs as go

    x_vals = data.index[data.IdLandkreis==ags]
    y_vals = data.loc[data.IdLandkreis==ags, 'InzidenzFallNeu_7TageSumme']
    print(y_vals)

    trace1 = go.Scatter(
        x = x_vals,
        y = y_vals,
        mode = "lines",
        name = "name",
        marker= dict(color = 'rgba(80, 26, 80, 0.8)'),
        text = y_vals
    )

    figdata = [trace1]
    layout = dict(title='First line plot',
                 xaxis=dict(title='date', ticklen=5, zeroline=False)
                 )

    #fig = dict(data=data, layout=layout)
    #py.iplot(fig)

    #import plotly.graph_objects as go

    # fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
    fig = go.Figure(data=figdata)
    fig.write_html('first_figure.html', auto_open=True)