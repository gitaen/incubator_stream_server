# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from influxdb import DataFrameClient
from dash.dependencies import Input, Output

PERIOD='1d'

client = DataFrameClient(host='incubator.local', database='incubator')

def generate_measurement_graph (measure, title, units, actuator):
    result = client.query('select * from ' + measure + ' where time > now()-' + PERIOD)
    try:
        df = list(result.values())[0]
    except IndexError:
        graph = html.P('No ' + measure + ' data for the last ' + PERIOD)
    else:
        df.index = df.index.tz_convert('Europe/Madrid')
        measure_df = df[['value','target']]
        power_df = df[['power']].apply(lambda x: x * 100 / 255)
        fig = px.line(measure_df, title=title)
        power_fig = px.line(power_df, title=actuator)
        graph = html.Div(children=[
            dcc.Graph(id = measure, figure=fig),
            dcc.Graph(id = measure + 'power', figure=power_fig)])

    return graph

def generate_turner_graph ():
    result = client.query('select * from turner where time > now()-' + PERIOD)
    try:
        df = list(result.values())[0][['time_left']]
    except IndexError:
        graph = html.P('No egg turner data for the last ' + PERIOD)
    else:
        df.index = df.index.tz_convert('Europe/Madrid')
        fig = px.line(df, title='Egg Turner')
        graph = dcc.Graph(id = 'egg_turner', figure=fig)

    return graph


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdn.jsdelivr.net/npm/hls.js@latest']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                external_scripts=external_scripts)
app.title = 'Pollo-o-Matic!'

app.layout = html.Div(children=[
    html.H1('Pollo-o-Matic!'),
    html.Div(children=[
        html.Video(id='video', width="100%", autoPlay=True, controls=True)]),
    generate_measurement_graph('temperature', 'Temperature', 'C', 'Heater Power'),
    generate_measurement_graph('humidity', 'Humidity', '%', 'Humidifier Power'),
    generate_turner_graph(),

])

app.clientside_callback(
    """
    function AttachHls(elementId) {
        var video = document.getElementById('video');
        var videoSrc = '/stream/index.m3u8';
        var config = {
            debug: true,
            capLevelOnFPSDrop: true,
            capLevelToPlayerSize: true}
        if (Hls.isSupported()) {
                var hls = new Hls(config);
                hls.attachMedia(video);
                hls.on(Hls.Events.MEDIA_ATTACHED, function () {
                    console.log("video and hls.js are now bound together !");
                    hls.loadSource(videoSrc);
                    hls.on(Hls.Events.MANIFEST_PARSED, function (event, data) {
                        console.log("manifest loaded, found " + data.levels.length + " quality level");
                        video.play();
                    });
                });
        }
        else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = videoSrc;
                video.addEventListener('loadedmetadata', function() {
                video.play();
                });
        }
    }
    """,
    Output('video', 'children'),
    Input('video', 'id'),
)



server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
