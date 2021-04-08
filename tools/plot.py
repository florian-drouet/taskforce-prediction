import plotly.graph_objects as go


def plot_taskforce(y_true, y_future, population_type):

    pop_translate = {"nurse": "ITS", "doctor": "Doctor"}

    trace_1 = go.Scatter(x=y_true.index, y=y_true.values, name="training")
    trace_2 = go.Scatter(x=y_future.index, y=y_future.values, name="predictions")

    # Create fig and add layout
    layout = go.Layout(
        xaxis=dict(
            showgrid=False,  # Hide Gridlines
            showline=False,  # Hide X-Axis
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        yaxis=dict(
            showgrid=False,  # Hide Gridlines
            showline=False,  # Hide X-Axis
            fixedrange=False
            # gridcolor='Black',
            # gridwidth=0.5
        ),
    )

    fig1 = go.Figure(layout=layout)

    # Add traces
    fig1.add_trace(trace_1)
    fig1.add_trace(trace_2)

    # Add shape regions
    fig1.add_vrect(
        x0=y_future.index[0],
        x1=y_future.index[-1],
        fillcolor="LightGrey",
        opacity=0.5,
        layer="below",
        line_width=0,
        name="prediction period",
    )

    fig1.update_layout(
        plot_bgcolor="whitesmoke",
        title=f"{pop_translate[population_type]} taskforce prediction",
    )
    fig1.update_yaxes(range=(0, max(y_true.max(), y_future.max())))

    return fig1


def plot_alert(alerts, y_future):
    trace_1 = go.Bar(
        x=alerts.index,
        y=alerts.number_of_orange_alerts,
        name="orange_alerts",
        marker_color="gold",
    )
    trace_2 = go.Bar(
        x=alerts.index,
        y=alerts.number_of_red_alerts,
        name="red_alerts",
        marker_color="tomato",
    )

    # Create fig and add layout
    layout = go.Layout(
        barmode="stack",
        xaxis=dict(
            showgrid=False,  # Hide Gridlines
            showline=False,  # Hide X-Axis
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        yaxis=dict(
            showgrid=False,  # Hide Gridlines
            showline=False,  # Hide X-Axis
            fixedrange=False,
        ),
    )

    fig2 = go.Figure(layout=layout)

    ## Add traces
    fig2.add_trace(trace_1)
    fig2.add_trace(trace_2)

    # Add shape regions
    fig2.add_vrect(
        x0=y_future.index[0],
        x1=y_future.index[-1],
        fillcolor="LightGrey",
        opacity=0.5,
        layer="below",
        line_width=0,
        name="prediction period",
    )

    fig2.update_layout(
        plot_bgcolor="whitesmoke", title="Evolution of red and orange alerts"
    )

    return fig2
