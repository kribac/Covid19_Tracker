"""
TODO
- add JJ to calculations
- az: second shots modeling
- update deliveries
- add delivery prognoses for AZ and JJ
- model ausfälle of vaccines
- plot delivered/planned

- Zweitimpfungen: Bedarf vs tatsächlich
- add datenstand + data update
- Wöchentlich
- select date
- area plots
- daily/weekly bar plot
- disply todays status

- create default settings file with data paths etc
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import dash_auth

from plot_vax import plot_vax_accumulated, plot_vax_daily
from plot_vax import VaxPlot
from predict_vax_progress import VaxPredictor
from data_update import update_vax_data

#--------------------------------- MODEL SETTINGS
USE_VACCINES = {
    "BIONTECH": True,
    "MODERNA": True,
    "ASTRAZENECA":True,
    "JOHNSON": True
}
DELIVERY_PREDICTION = "prognosis" #"static", "prognosis"
# DELIVERY_PREDICTION = "static" #"static", "prognosis"
END_DATE = "2021-09-30"



#--------------------------------- PLOT CONTROL DEFAULTS
DFLT_PLOT_ENABLE = {'total':True, 'biontech':True, 'astrazeneca':True, 'moderna':True, 'johnson':True}
DFLT_DAILY = False # show daily or accumulated
DFLT_ROLLING = False # 7 day rolling average
#---------------------------------------------

#--------------------------------- APP SETTINGS
colors = {'background': 'lightgray',#'#111111',
          'text': '#7FDBFF'
          }
#----------------------------------------------

app = dash.Dash()

markdown_text = '''
# Covid-19 Impfungen Deutschland Prognose
'''

#---------------------------------
def update_vax_graph():
    vaxplot.updateData()
    return vaxplot.plotVaxLine()


#--------------------------------- CALL MODEL
vax_predictor = VaxPredictor(use_vaccines=USE_VACCINES, end_date=END_DATE)
vax_predictor.loadData()
vax_predictor.predictVaxTS()
#----------------------------------------------

#----------------------------------- INIT PLOT
# plotdata, plotlayout = plot_vax_accumulated(vax_predictor.vax_ts, plot_enable=PLOT_ENABLE)
# fig_vax_acc = plot_vax_accumulated(vax_predictor, plot_enable=PLOT_ENABLE)

vaxplot = VaxPlot(vax_predictor)
vaxplot.enable = DFLT_PLOT_ENABLE
vaxplot.daily = DFLT_DAILY
vaxplot.rolling = DFLT_ROLLING
fig_vax = update_vax_graph()
#fig_vax = vaxplot.plotVaxLine()

#----------------------------------------------


#----------------------------------------------


app_layout = html.Div(
    [
        dcc.Markdown(children = markdown_text),
        html.Div(
            style={'backgroundColor': colors['background']},
            children = [
                html.Label('Anzeige Impfstoffe Einstellungen'),
                dcc.Dropdown(
                    id = 'option_select_vax',
                    options =[
                        {'label': 'Gesamt', 'value': 'all'},
                        {'label': 'BioNTech', 'value': 'biontech'},
                        {'label': 'Astra Zeneca', 'value': 'astrazeneca'},
                        {'label': 'Moderna', 'value': 'moderna'},
                        {'label': 'Johnson & Johnson', 'value': 'johnson'},
                              ],
                    value=['all','biontech','astrazeneca','moderna'], # default value
                    multi = True # multi-select dropdown
                ),
                #
                html.Label('Text Box'),
                dcc.Input(id='my-id', value='biontech', type='text'),
                html.Div(id='my-div'),],
        ),
        dcc.Graph(
            id = 'graph_vax_accumulated',
            figure = fig_vax
            # {
            #     'data' : plotdata,
            #     'layout' : plotlayout
            # }
        )
    ]
)


# graph settings for accumulated vaccinations
sub_layout_settings_plot = [
    html.Label('Einstellungen Graph'),
    dcc.Dropdown(
            id = 'opt_select_vax',
            options =[
                {'label': 'Gesamt', 'value': 'total'},
                {'label': 'BioNTech', 'value': 'biontech'},
                {'label': 'Astra Zeneca', 'value': 'astrazeneca'},
                {'label': 'Moderna', 'value': 'moderna'},
                {'label': 'Johnson & Johnson', 'value': 'johnson'},
                ],
            value=['total','biontech','astrazeneca','moderna', 'johnson'], # default value
            multi = True # multi-select dropdown
        ),
    dcc.Checklist(
        id = 'opt_data_prep',
        options = [
            {'label': 'Täglich', 'value':'daily'},
            {'label': '7 Tage Mittel', 'value':'rolling'}
        ],
        value = [] #default
    )
]




app_layout_tmp = html.Div(
    [
        ### SELECT TYPE OF GRAPH
        dcc.Markdown(children = markdown_text),
        html.Div(
            id = 'graph_select',
            children = [
                html.Label('Auswahl Graph'),
                dcc.Dropdown(
                    id = 'opt_graph_type',
                    options = [
                        {'label': 'Impfungen', 'value':'vax'},
                        {'label': 'Lieferungen', 'value': 'vax_deliveries'},
                    ],
                    value = 'vax_acc',
                    multi = False
                ),
            ],
        ),
        ### SETTINGS OF THE GRAPH
        html.Div(
            id = 'settings_graph',
            style = {'backgroundColor': colors['background']},
            children = sub_layout_settings_plot,
        ),
        ### GRAPH
        dcc.Graph(
            id = 'graph_vax',
            figure = fig_vax,
        )
    ]
)

app.layout = app_layout_tmp




# @app.callback(
#     Output(component_id='opt_select_vax', component_property='value'),
#     [Input(component_id='graph_select', component_property='value')]
# )
# def adapt_graph_settings(input_value):
#     if input_value ==

#---- callback: selection of vaccines to plot
@app.callback(
    Output(component_id='graph_vax', component_property='figure'),
    [ Input(component_id='opt_select_vax', component_property='value'),
      Input(component_id='opt_data_prep', component_property='value'), ]
)
def update_graph_vax(selected_vax, data_options):
    """
    update graph: data format (daily or accumulated, w/o smoothing
    """
    vaxplot.enable = {'total': False, 'biontech': False, 'astrazeneca': False, 'moderna': False, 'johnson': False}
    for vaxtype in selected_vax:
        vaxplot.enable[vaxtype] = True

    vaxplot.daily = True if 'daily' in data_options else False
    vaxplot.rolling = True if 'rolling' in data_options else False
    return update_vax_graph()






if __name__ == '__main__':




    app.run_server(debug=True)
    # call: python app.py