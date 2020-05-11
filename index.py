import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from homepage import Homepage
from analysis import Analysis
from app import App, Result
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])

@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/results':
        return App()
    else:
        return Homepage()

@app.callback([Output("html_progress_bar", "style"),Output('output-data', 'children'),Output("loading-output-2", "children"),Output("Link", "style"),Output('upload-data', "style")],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(contents, filename):
    if contents is not None:
        success = Analysis(filename)
        if(success):
            return {'display': 'none'},'Result is ready',"",{'display': 'block'},{'display': 'none'}
        else:
            return {'display': 'block'},'Analysis failed',"",{},{}

@app.callback(
    [Output('table','data'),
     Output('graph','children'),
     Output('stats','children')],
    [Input('radio-button', 'value'),
     Input('table', 'selected_row_ids'),
     Input('table', 'active_cell')])
def update_result(value, rows, selected_row_indices):
    return Result(value, rows, selected_row_indices)
    

"""@app.callback(
    [Output("html_progress", "value") ],
    [Input('upload-data', 'contents'),
     Input("progress-interval", "n_intervals")],
)
def update_progress(contents,n):
    if contents is not None:
        # check progress of some background process, in this example we'll just
        # use n_intervals constrained to be in 0-100
        progress = min(n % 110, 100)
        #print(progress)
        # only add text after 5% progress to ensure text isn't squashed too much
        return str(progress)
    else:
        return "0"
        
"""
if __name__ == '__main__':
    app.run_server(debug=True)