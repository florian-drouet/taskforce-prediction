# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import sys
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from tools.func import update_data, get_data, machine_learning_parameters
from tools.plot import plot_taskforce, plot_alert

if sys.argv[1] == "DEBUG":
    DEBUG = True
else:
    DEBUG = False

X, y = get_data(DEBUG)
scaler, lin_reg = machine_learning_parameters()

app = dash.Dash(
    "dashboard_RH",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            className="grid-container",
            children=[
                html.Div(
                    className="header",
                    children=[
                        html.Div(
                            "Global taskforce prediction with control parameters",
                            className="header--title",
                        ),
                        html.Div(
                            "Made with \u2764\ufe0f with Dash.",
                            className="header--subtitle",
                        ),
                        html.Img(src="/assets/logo_covidom.png", className="img"),
                    ],
                ),
                html.Div(
                    className="controllers",
                    children=[
                        dcc.DatePickerRange(
                            id="input_dates",
                            start_date=datetime.date(2020, 3, 10),
                            display_format="DD/MM/YYYY",
                            min_date_allowed=datetime.date(2020, 3, 10),
                            start_date_placeholder_text="START DATE",
                            end_date_placeholder_text="END DATE",
                            clearable=True,
                        ),
                        html.Label("Type of population"),
                        dcc.Dropdown(
                            id="population_type",
                            options=[
                                {"label": "ITS", "value": "nurse"},
                                {"label": "Doctors", "value": "doctor"},
                            ],
                            value="nurse",
                        ),
                        html.Label("Type of projection"),
                        dcc.Dropdown(
                            id="projection_mode",
                            options=[
                                {"label": "Linear", "value": "arithmetic"},
                                {"label": "Quadratic", "value": "geometric"},
                                {"label": "Bell curve", "value": "bell_curve"},
                            ],
                            value="bell_curve",
                        ),
                        html.Label("Number of days"),
                        dcc.Input(
                            id="number_of_days_projections",
                            type="number",
                            value=60,
                            min=1,
                            step=1,
                            required=True,
                        ),
                        html.Label("Arithmetic parameter"),
                        dcc.Input(
                            id="arithmetic_parameter",
                            type="number",
                            value=20,
                            step=1,
                            disabled=True,
                            required=True,
                        ),
                        html.Label("Geometric parameter"),
                        dcc.Input(
                            id="geometric_parameter",
                            type="number",
                            value=1.01,
                            step=0.001,
                            disabled=False,
                            required=True,
                        ),
                        html.Label("Alert's peak"),
                        dcc.Input(
                            id="alerts_peak",
                            type="number",
                            value=20,
                            min=1,
                            step=1,
                            disabled=True,
                            required=True,
                        ),
                        html.Label("Upstream slope"),
                        dcc.Input(
                            id="coef_bell1",
                            type="number",
                            value=1.02,
                            step=0.001,
                            disabled=True,
                            required=True,
                        ),
                        html.Label("Downstream slope"),
                        dcc.Input(
                            id="coef_bell2",
                            type="number",
                            value=0.97,
                            step=0.001,
                            disabled=True,
                            required=True,
                        ),
                    ],
                ),
                html.Div(className="fig1", children=[dcc.Graph(id="its_graph")]),
                html.Div(className="fig2", children=[dcc.Graph(id="alert_graph")]),
            ],
        )
    ]
)


@app.callback(
    Output("its_graph", "figure"),
    Output("alert_graph", "figure"),
    Input("input_dates", "start_date"),
    Input("input_dates", "end_date"),
    Input("arithmetic_parameter", "value"),
    Input("geometric_parameter", "value"),
    Input("number_of_days_projections", "value"),
    Input("projection_mode", "value"),
    Input("population_type", "value"),
    Input("alerts_peak", "value"),
    Input("coef_bell1", "value"),
    Input("coef_bell2", "value"),
)
def update_graphs(
    start_date_,
    end_date_,
    arithmetic_parameter,
    geometric_parameter,
    number_of_days_projections,
    projection_mode,
    population_type,
    alerts_peak,
    coef_bell1,
    coef_bell2,
):
    """
    This function updates the two graphs with the parameters from the controller's section.
    """
    # converts start date input into datetime    
    try:
        start = datetime.datetime.strptime(start_date_, "%Y-%m-%d")
        end=datetime.datetime.strptime(end_date_, "%Y-%m-%d")
    except:
        start=datetime.datetime(2020,3,10,0,0,0)
        end=datetime.datetime.combine((y[population_type].index[-1]+datetime.timedelta(days=number_of_days_projections)).date(), datetime.datetime.min.time())
    y_plot = y[population_type]

    if alerts_peak >= number_of_days_projections:
        raise Exception(
            "WARNING : The peak of alerts cannot be greather than (or equal) to the number of projection days ! Please enter anothe value."
        )

    y_true, y_future, alerts = update_data(
        X=X.loc[X.index >= start],
        y=y_plot.loc[y_plot.index >= start],
        model=lin_reg[population_type],
        preprocessing=scaler,
        projection_mode=projection_mode,
        arithmetic_parameter=arithmetic_parameter,
        geometric_parameter=geometric_parameter,
        number_of_days_projections=number_of_days_projections,
        alerts_peak=alerts_peak,
        coef_bell1=coef_bell1,
        coef_bell2=coef_bell2,
    )    
    fig1 = plot_taskforce(y_true, y_future, population_type, end)
    fig2 = plot_alert(alerts, y_future, end)
    return fig1, fig2


@app.callback(
    Output("arithmetic_parameter", "disabled"),
    Output("geometric_parameter", "disabled"),
    Output("alerts_peak", "disabled"),
    Output("coef_bell1", "disabled"),
    Output("coef_bell2", "disabled"),
    Input("projection_mode", "value"),
)
def enable_inputs(value):
    if value == "arithmetic":
        return False, True, True, True, True
    elif value == "geometric":
        return True, False, True, True, True
    elif value == "bell_curve":
        return True, True, False, False, False


if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
