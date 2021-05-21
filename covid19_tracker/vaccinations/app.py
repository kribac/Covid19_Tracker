"""
TODO
- add datenstand
- add JJ
- backend
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
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

PERSONS_TO_VACCINATE = 51087903 # from "pandemieende.de"
POPULATION_GERMANY = 83190556


#--------------------------------- PLOT CONTROL
PLOT_ENABLE = {'all':True, 'biontech':True, 'astrazeneca':True, 'moderna':True}
#---------------------------------------------

#--------------------------------- APP SETTINGS
colors = {'background': '#111111',
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
                html.Label('Multi-Select Dropdown'),
                dcc.Dropdown(
                    options =[
                        {'label': 'New York City', 'value': 'NYC'},
                        {'label': u'Montréal', 'value': 'MTL'},
                        {'label': 'San Francisco', 'value': 'SF'},
                              ],
                    value='MTL', # default value
                    multi = True # multi-select dropdown
                ),
                #
                html.Label('Text Box'),
                dcc.Input(id='my-id', value='MTL', type='text'),
                html.Div(id='my-div'),],
        ),
        dcc.Graph(
            id = 'vax_accumulated',
            figure = fig_vax_acc
            # {
            #     'data' : plotdata,
            #     'layout' : plotlayout
            # }
        )
    ]
)


app.layout = app_layout

if __name__ == '__main__':




    app.run_server(debug=True)
    # call: python app.py