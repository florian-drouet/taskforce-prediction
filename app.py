# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from tools.func import update_data, get_data, machine_learning_parameters
from tools.plot import plot_taskforce, plot_alert

X, y = get_data()
scaler, lin_reg = machine_learning_parameters()

#external_stylesheets = ['C:/Users/4170422/Documents/Etudes/Etudes_its_taskforce/stylesheet.css']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash("dashboard_RH", external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.H1(children='Global taskforce prediction with control parameters'),

        html.Div(children='''
            Made with \u2764\ufe0f with Dash.
        '''),
        
        html.Div(className='row',  # Define the row element
                 children=[html.Div(className='three columns', # define the left elements
                                    children=[html.H4("Projection parameter"),
                                              dcc.Input(id='projection_parameter',
                                                        type='number',
                                                        value=1.01,
                                                        step=0.001,
                                                       ),
                                              html.H4("Number of days"),
                                              dcc.Input(id='number_of_days_projections',
                                                        type='number',
                                                        value=60,
                                                        min=1,
                                                        step=1,
                                                       ),
                                              html.H4("Type of projection"),
                                              dcc.Dropdown(id='projection_mode',
                                                           options=[
                                                               {'label': 'Linear', 'value': 'linear'},
                                                               {'label': 'Quadratic', 'value': 'quadratic'},
                                                               {'label': 'Exponential', 'value': 'exponential'}
                                                           ],
                                                           value='quadratic',
                                                          ),
                                               html.H4("Type of population"),
                                               dcc.Dropdown(id='population_type',
                                                           options=[
                                                               {'label': 'ITS', 'value': 'nurse'},
                                                               {'label': 'Doctors', 'value': 'doctor'}
                                                           ],
                                                           value='nurse',
                                                          ),
                                             ]),  # Define the right elements
                           html.Div(className='nine columns',
                                    children=[
                                        dcc.Graph(id='its_graph'),
                                        dcc.Graph(id='alert_graph')
                                    ])
                          ])
    ])

@app.callback(Output('its_graph', 'figure'),
              Output('alert_graph', 'figure'),
              Input('projection_parameter', 'value'),
              Input('number_of_days_projections', 'value'),
              Input('projection_mode', 'value'),
              Input('population_type', 'value'))
def update_alert_graph(projection_parameter, number_of_days_projections, projection_mode, population_type):
    y_true, y_future, alerts = update_data(X=X, y=y[population_type], model=lin_reg[population_type], preprocessing=scaler, projection_mode=projection_mode, projection_parameter=projection_parameter, number_of_days_projections=number_of_days_projections)
    fig1 = plot_taskforce(y_true, y_future, population_type)
    fig2 = plot_alert(alerts, y_future)
    return fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)