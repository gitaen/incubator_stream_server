# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from datetime import date, datetime, timedelta
from dateutil import tz
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from influxdb import DataFrameClient
from dash.dependencies import Input, Output

STARTING_DATE = datetime.fromisoformat('2021-03-08 00:00:00+01:00')
PERIOD = '1d'
hatching_datetime = STARTING_DATE + timedelta(days=20)

client = DataFrameClient(host='incubator.local', database='incubator')


def generate_measurement_graph(measure, title, units, actuator):
    result = client.query('select * from ' + measure + ' where time > now()-'
                          + PERIOD)
    try:
        df = list(result.values())[0]
    except IndexError:
        graph = html.P('No ' + measure + ' data for the last ' + PERIOD)
    else:
        df.index = df.index.tz_convert('Europe/Madrid')
        measure_df = df[['value', 'target']]
        measure_df.columns = ['Actual', 'Target']
        power_df = df[['power']].apply(lambda x: x * 100 / 255)
        power_df.columns = ['Power']
        fig = px.line(measure_df, title=title, labels={
            'value': units,
            'index': 'Time',
            'variable': 'Temperature'})
        power_fig = px.line(power_df, title=actuator, labels={
            'value': '%',
            'variable': ''})
        graph = html.Div(children=[
            dcc.Graph(id=measure, figure=fig),
            dcc.Graph(id=measure + 'power', figure=power_fig)])

    return graph


def generate_turner_graph():
    result = client.query('select * from turner where time > now()-' + PERIOD)
    try:
        df = list(result.values())[0][['time_left']]
    except IndexError:
        graph = html.P('No egg turner data for the last ' + PERIOD)
    else:
        df.index = df.index.tz_convert('Europe/Madrid')
        fig = px.line(df, title='Egg Turner')
        graph = dcc.Graph(id='egg_turner', figure=fig)

    return graph


def get_turning_datetime():
    result = client.query('select last(time_left) from turner')

    df = list(result.values())[0]
    (label, measure) = list(df.items())[0]
    entry = measure.to_dict()
    (time_stamp, time_left) = entry.popitem()
    return time_stamp + timedelta(seconds=time_left)


def generate_uptime_graph():
    result = client.query('select * from uptime where time > now()-' + PERIOD)
    try:
        df = list(result.values())[0]
    except IndexError:
        graph = html.P('No uptime data for the last ' + PERIOD)
    else:
        df.index = df.index.tz_convert('Europe/Madrid')
        fig = px.line(df, title='Uptime')
        graph = dcc.Graph(id='uptime', figure=fig)

    return graph


def serve_layout():
    return html.Div(children=[
        dcc.Location(id='url', refresh=False),
        html.H1('Pollo-o-Matic!'),
        html.H2('Hatching on {}. {} days left'
                .format(hatching_datetime.date(), (hatching_datetime.date()
                                                   - date.today()).days)),
        html.Div(children=[
            dcc.Interval(id='nextTurnInterval'),
            html.Div(id='nextTurn')]),
        html.Div(children=[
            html.Video(id='video', width="100%", autoPlay=True,
                       controls=True)]),
        generate_measurement_graph('temperature', 'Temperature', 'ºC',
                                   'Heater Power'),
        generate_measurement_graph('humidity', 'Relative Humidity', '%RH',
                                   'Humidifier Power'),
        html.Div(id='advanced')
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdn.jsdelivr.net/npm/hls.js@latest']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                external_scripts=external_scripts)
app.title = 'Pollo-o-Matic!'

app.layout = serve_layout


@app.callback(dash.dependencies.Output('nextTurnInterval', 'interval'),
              [dash.dependencies.Input('nextTurnInterval', 'n_intervals')])
def get_turning_interval(n_intervals):
    return ((get_turning_datetime().to_pydatetime()
            - datetime.now(tz.gettz('Europe/Madrid'))).total_seconds() + 60) * 1000


@app.callback(dash.dependencies.Output('nextTurn', 'children'),
              [dash.dependencies.Input('nextTurnInterval', 'n_intervals')])
def get_turning_time(n_intervals):
    try:
        turning_date=get_turning_datetime()
    except IndexError:
        return html.P('No egg turner data')

    return html.H3('Next egg rotation at {} CET'
                   .format(turning_date.astimezone(tz.gettz('Europe/Madrid'))
                           .strftime('%H:%M:%S')))
    # return html.Div(children=[
    #     html.H3(turning_date.astimezone(tz.gettz('Europe/Madrid'))),
    #     html.H3("Eggs turning in {}"
    #             .format(turning_date.to_pydatetime()
    #                     - datetime.now(tz.gettz('Europe/Madrid'))))])



@app.callback(dash.dependencies.Output('advanced', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_advanced(pathname):
    if pathname == '/advanced':
        return [generate_turner_graph(),
                generate_uptime_graph()]
    else:
        return


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
                        console.log("manifest loaded, found " +
                                     data.levels.length + " quality level");
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
