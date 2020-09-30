import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(
        className = "row",
        style = {'textAlign': 'center', 'font-size': '30px'},
        children = [
            html.Div(children= 'Prime-Time : an Interesting Trivia Finder')
        ]
    ), 
    html.Div([
        'Brief description of problem statement:',
        'Did you know that Virender Sehwag highest scores in T20, ODI and Tests are 119, 219 and 319 respectively or that Alec Stewart was born on 8-4-63 and he scored 8463 Test runs. How about if Micheal Phelps were a country, he would rank No. 35 on the all-time Olympic gold medal list, ahead of 97 nations! Sounds interesting right? These facts are quite exquite because they present a unique idea about a domain, which is eye catchy and well, mostly unheard of. But, how are these facts generated? We are hoping behind the curtains of AI and ML, that there is not an army of data crunchers looking through all possible scenarions and finding cool facts. And we intend to prove so! The aim is to create an intelligent news center, which crunches every possible variant of data to give simple, impactful and powerful facts as output.'
    ]),
    dcc.Upload(
        id='upload-data',
        style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'},
        children = [
            html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ])
        ]
    ),
    html.Div(
        id='output-data'
    ),
    html.Div(
        children=[   
            
            dcc.Loading(
                    id="loading-2",
                    children=[html.Div([html.Div(id="loading-output-2")])],
                    type="circle",
                )
            ],
        id='html_progress_bar'
    ),
    dcc.Link(
        html.Button('Navigate to results'),
        style = {'display': 'none'},
        href='/results',
        id = 'Link'
    )
])

#dcc.Interval(id="progress-interval", n_intervals=0, interval=110),
 #           html.Progress(id = "html_progress" , max = '100', style = {'width': '100%'} ),

def Homepage():
    return app.layout

if __name__ == '__main__':
    app.run_server(debug=True)