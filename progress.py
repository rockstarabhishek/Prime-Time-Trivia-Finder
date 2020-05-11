import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
        [
           dcc.Interval(id="progress-interval", n_intervals=0, interval=110),
            
            html.Progress(id = "html_progress" , max = '100' ,contentEditable = "Yes", children = 'Ohh Yess'),
            dbc.Spinner(color="primary")
            
            

        ]
    )
    
@app.callback(
    [Output("html_progress", "value"),Output("html_progress", "style")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    progress = min(n % 110, 100)
    #print(progress)
    # only add text after 5% progress to ensure text isn't squashed too much
    return str(progress), {
  'content':'progress',
  'position':'absolute',
  'left':'0',
  'right':'0',
  'text-align':'center',
 'display':'inline-block',
 'position':'relative',
 'width' :'100%'
}



if __name__ == '__main__':
    app.run_server(debug=True)