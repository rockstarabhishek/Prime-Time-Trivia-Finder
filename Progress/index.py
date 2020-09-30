import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import no_update

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

@app.callback(Output('upload-data-div', 'style'),
              [Input('upload-data', 'contents')])
def update_upload_data_div(contents):
    if contents is not None:
        return {'display':'none'}

@app.callback([Output('loading-bar-div', 'style'),
               Output('result-ready-div', 'children'),
               Output('navigate-result', 'style'),
               Output("loading-output-2", "children")],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_loading_navigation_bar(contents, filename):
    if contents is not None:
        success = Analysis(filename)
        if(success):
            return [{'display':'none'},
                    'Result is ready',
                    {'display':'block', 'textAlign':'center'},
                    '']
                   
        else:
            return [{'display':'none'},
                    'Analysis failed',
                    {'display':'none'},
                    '']
    else:
        return [no_update, no_update, no_update, no_update]

@app.callback(
    [Output('table','data'),
     Output('graph','children'),
     Output('stats','children')],
    [Input('radio-button', 'value'),
     Input('table', 'selected_row_ids'),
     Input('table', 'active_cell')])
def update_result(value, rows, selected_row_indices):
    return Result(value, rows, selected_row_indices)
    
if __name__ == '__main__':
    app.run_server(debug=True)