# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from influxdb import DataFrameClient

PERIOD='1h'

client = DataFrameClient(host='incubator.local', database='incubator')

def generate_graph (measure):
    result = client.query('select target,value from ' + measure + ' where time > now()-' + PERIOD)
    df = list(result.values())[0]
    df.index = df.index.tz_convert('Europe/Madrid')
    fig = px.line(df)

    result = client.query('select power from ' + measure + ' where time > now()-' + PERIOD)
    df = list(result.values())[0]
    df.index = df.index.tz_convert('Europe/Madrid')
    power_fig = px.line(df)

    return html.Div(children=[
        dcc.Graph(id = measure, figure=fig),
        dcc.Graph(id = measure + 'power', figure=power_fig)])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='US Agriculture Exports (2011)'),
    generate_graph('temperature'),
    generate_graph('humidity')
])

if __name__ == '__main__':
    app.run_server(debug=True)
