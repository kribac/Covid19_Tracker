import plotly.graph_objs as go

from predict_vax_progress import VaxPredictor

FILE_VAX_TIMESERIES = '../../data/germany_vaccinations_timeseries_v2.tsv'
FILE_DELIVERIES_TIMESERIES = '../../data/germany_deliveries_timeseries_v2.tsv'
FILE_VAX_BY_STATE = '../../data/germany_vaccinations_by_state.tsv'

# Q2 deliveries
# FILE_DELIVERY_PROGNOSIS = "../../data/impfung_lieferprognoseQ2_stand210507.csv"

# Q2 deliveries + estimates for Q3
FILE_DELIVERY_PROGNOSIS = "../../data/impfung_lieferprognoseQ2Q3_stand210517.csv"


# determine which vaccines are considered in vaccination campaign
USE_VACCINES = {
    "BIONTECH": True,
    "MODERNA": True,
    "ASTRAZENECA":True,
    "JJ": False
}

DELIVERY_PREDICTION = "prognosis" #"static", "prognosis"
# DELIVERY_PREDICTION = "static" #"static", "prognosis"
END_DATE = "2021-09-30"


PERSONS_TO_VACCINATE = 51087903 # from "pandemieende.de"
POPULATION_GERMANY = 83190556


# PLOT PROPERTIES

PLOT_ENABLE = {'all':True, 'biontech':True, 'astrazeneca':True, 'moderna':True}

PLOT_VAX_ALL = dict(
    #enable=True,
    column_names = ["dosen_kumulativ", "personen_erst_kumulativ", "personen_voll_kumulativ"],
    names = ["Dosen gesamt", "Erstimpfungen gesamt", "Vollgeimpfte gesamt"],
    linestyles = ["dot", "solid", "dash" ],
    color = "black",
)

PLOT_VAX_BIONTECH = dict(
    #enable=True,
    column_names = ["dosen_biontech_kumulativ", "dosen_biontech_erst_kumulativ", "dosen_biontech_zweit_kumulativ"],
    names = ["Dosen BioNTech", "Erstimpfungen BioNTech", "Vollgeimpfte BioNTech"],
    linestyles = ["dot", "solid", "dash" ],
    color = "blue",
)

PLOT_VAX_ASTRAZENECA = dict(
    #enable=True,
    column_names = ["dosen_astrazeneca_kumulativ", "dosen_astrazeneca_erst_kumulativ", "dosen_astrazeneca_zweit_kumulativ"],
    names = ["AZ Dosen", "AZ Erstimpfungen", "AZ Vollgeimpfte"],
    linestyles = ["dot", "solid", "dash" ],
    color = "purple",
)

PLOT_VAX_MODERNA = dict(
    #enable=True,
    column_names = ["dosen_moderna_kumulativ", "dosen_moderna_erst_kumulativ", "dosen_moderna_zweit_kumulativ"],
    names = ["MD Dosen", "MD Erstimpfungen", "MD Vollgeimpfte"],
    linestyles = ["dot", "solid", "dash" ],
    color = "green",
)


def plot_vax_daily(vax_predictor, plot_enable):

    vax_ts = vax_predictor.vax_ts

    plotdata = []
    if plot_enable['all']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_ALL, daily=True))
    if plot_enable['biontech']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_BIONTECH, daily=True))
    if plot_enable['astrazeneca']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_ASTRAZENECA, daily=True))
    if plot_enable['moderna']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_MODERNA, daily=True))

    layout = dict(title="Impfungen kumulativ",
                  xaxis=dict(title="Datum", ticklen=5, zeroline=False),
                  height=800,
                  )

    fig = go.Figure(data=plotdata, layout=layout)

    fig.add_hline(y=POPULATION_GERMANY, line=dict(color='darkgrey',dash='solid', width=1),
                  annotation_text="100% Gesamtbevölkerung", annotation_position="top left")
    fig.add_hline(y=0.75*POPULATION_GERMANY, line=dict(color='darkgrey', dash='solid', width=1),
                  annotation_text="75% Gesamtbevölkerung", annotation_position="top left")
    fig.add_hline(y=0.6*POPULATION_GERMANY, line=dict(color='darkgrey', dash='solid', width=1),
                  annotation_text="60% Gesamtbevölkerung", annotation_position="top left")

    fig.add_vline(x=vax_predictor.TODAY, line=dict(color='darkorange',width=1))

    return fig #plotdata, layout



def plot_vax_accumulated(vax_predictor, plot_enable):

    vax_ts = vax_predictor.vax_ts

    plotdata = []
    if plot_enable['all']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_ALL))
    if plot_enable['biontech']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_BIONTECH))
    if plot_enable['astrazeneca']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_ASTRAZENECA))
    if plot_enable['moderna']:
        plotdata.extend(plot_vax_line(vax_ts, PLOT_VAX_MODERNA))

    layout = dict(title="Impfungen kumulativ",
                  xaxis=dict(title="Datum", ticklen=5, zeroline=False),
                  height=800,
                  )

    fig = go.Figure(data=plotdata, layout=layout)

    fig.add_hline(y=POPULATION_GERMANY, line=dict(color='darkgrey',dash='solid', width=1),
                  annotation_text="100% Gesamtbevölkerung", annotation_position="top left")
    fig.add_hline(y=0.75*POPULATION_GERMANY, line=dict(color='darkgrey', dash='solid', width=1),
                  annotation_text="75% Gesamtbevölkerung", annotation_position="top left")
    fig.add_hline(y=0.6*POPULATION_GERMANY, line=dict(color='darkgrey', dash='solid', width=1),
                  annotation_text="60% Gesamtbevölkerung", annotation_position="top left")

    fig.add_vline(x=vax_predictor.TODAY, line=dict(color='darkorange',width=1))

    return fig #plotdata, layout


def plot_vax_line(vax_ts, plot_props, daily=False):
    """
    plot timeseries of vaccinations
    """
    cols = plot_props['column_names']
    linestyles = plot_props['linestyles']


    plotdata = [
        go.Scatter(
            x = vax_ts.index,
            y = vax_ts[cols[i]] if daily is False else vax_ts[cols[i]].diff(),
            name = plot_props['names'][i],
            mode = "lines",
            marker = dict(color=plot_props['color']),
            line = dict(dash=linestyles[i])
            #text = vax_ts.dosen_kumulativ
        ) for i in range(len(cols))
    ]
    return plotdata




if __name__ == "__main__":

    vax_predictor = VaxPredictor(use_vaccines=USE_VACCINES, end_date=END_DATE)

    vax_predictor.loadData(FILE_VAX_TIMESERIES)
    vax_predictor.predictVaxTS()

    vax_ts = vax_predictor.vax_ts

    vax_ts_rolling = vax_ts.rolling(7).mean()


    vax_ts["personen_ziel"] = PERSONS_TO_VACCINATE
    vax_ts["dreiviertel_deutsche"] = 0.75*POPULATION_GERMANY



    status_fist_shots = vax_ts.personen_erst_kumulativ.loc[vax_predictor.TODAY]
    print(f"people with one shot: {status_fist_shots}")
    print(f"this is {status_fist_shots/POPULATION_GERMANY*100}% of the total population")
    print(f"this is {status_fist_shots / (0.75*POPULATION_GERMANY) * 100}% of 75% of all Germans")

    plot_enable = PLOT_ENABLE #{'all': True, 'biontech': True}
    plotdata, layout = plot_vax_accumulated(vax_ts, plot_enable)

    #plotdata.extend( plot_vax_accumulated(vax_ts, PLOT_VAX_BIONTECH))
    # layout = dict(title="Impfungen kumulativ",
    #               xaxis=dict(title="date", ticklen=5, zeroline=False)
    #               )
    fig = go.Figure(data=plotdata)
    fig.write_html('vaxplot_test.html', auto_open=True)