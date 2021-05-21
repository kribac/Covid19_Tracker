"""
TODO
- add datenstand
- add JJ
- select date

- tägliche impfungen
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import dash_auth

from plot_vax import plot_vax_accumulated
from predict_vax_progress import VaxPredictor
from data_update import update_vax_data

#--------------------------------- MODEL SETTINGS
USE_VACCINES = {
    "BIONTECH": True,
    "MODERNA": True,
    "ASTRAZENECA":True,
    "JJ": False
}
DELIVERY_PREDICTION = "prognosis" #"static", "prognosis"
# DELIVERY_PREDICTION = "static" #"static", "prognosis"
END_DATE = "2021-09-30"



#--------------------------------- PLOT CONTROL
PLOT_ENABLE = {'all':True, 'biontech':True, 'astrazeneca':True, 'moderna':True}
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

#--------------------------------- CALL MODEL
vax_predictor = VaxPredictor(use_vaccines=USE_VACCINES, end_date=END_DATE)
vax_predictor.loadData()
vax_predictor.predictVaxTS()
#----------------------------------------------
#----------------------------------- CALL PLOT
# plotdata, plotlayout = plot_vax_accumulated(vax_predictor.vax_ts, plot_enable=PLOT_ENABLE)
fig_vax_acc = plot_vax_accumulated(vax_predictor, plot_enable=PLOT_ENABLE)
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
            figure = fig_vax_acc
            # {
            #     'data' : plotdata,
            #     'layout' : plotlayout
            # }
        )
    ]
)


app.layout = app_layout


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='option_select_vax', component_property='value') ]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)



#---- callback: selection of vaccines to plot
@app.callback(
    Output(component_id='graph_vax_accumulated', component_property='figure'),
    [Input(component_id='option_select_vax', component_property='value') ]
)
def update_vax_graph(input_value):
    print(f"vaccines to include in graph: {input_value}")
    plot_enable = {'all': False, 'biontech': False, 'astrazeneca': False, 'moderna': False, 'johnson':False}
    for vaxtype in input_value:
        plot_enable[vaxtype] = True
    fig_vax_acc = plot_vax_accumulated(vax_predictor, plot_enable)
    return fig_vax_acc



if __name__ == '__main__':




    app.run_server(debug=True)
    # call: python app.py