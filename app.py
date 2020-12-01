# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from influxdb import DataFrameClient

PERIOD='1w'

client = DataFrameClient(host='incubator.local', database='incubator')

def generate_graph (measure):
    result = client.query('select * from ' + measure + ' where time > now()-' + PERIOD)
    try:
        df = list(result.values())[0]
    except IndexError:
        graph = html.P('No ' + measure + ' data for the last ' + PERIOD)
    else:
        df.index = df.index.tz_convert('Europe/Madrid')
        measure_df = df[['value','target']]
        power_df = df[['power']].apply(lambda x: x * 100 / 255)
        fig = px.line(measure_df)
        power_fig = px.line(power_df)
        graph = html.Div(children=[
            dcc.Graph(id = measure, figure=fig),
            dcc.Graph(id = measure + 'power', figure=power_fig)])

    return graph

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.Div(children=[
        html.Video(id='video', autoPlay=True, controls=True),
        html.Script(src='https://cdn.jsdelivr.net/npm/hls.js@latest'),
        html.Script('''
        var video = document.getElementById('video');
        var videoSrc = '/stream/index.m3u8';
        var config = {
          capLevelOnFPSDrop: true,
          capLevelToPlayerSize: true}
        if (Hls.isSupported()) {
           var hls = new Hls(config);
           hls.loadSource(videoSrc);
           hls.attachMedia(video);
           hls.on(Hls.Events.MANIFEST_PARSED, function() {
             video.play();
           });
        }
        else if (video.canPlayType('application/vnd.apple.mpegurl')) {
           video.src = videoSrc;
           video.addEventListener('loadedmetadata', function() {
             video.play();
           });
        }
        ''')]),
    generate_graph('temperature'),
    generate_graph('humidity'),
])

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
