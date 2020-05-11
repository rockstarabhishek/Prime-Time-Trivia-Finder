import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import dash_table
import pickle
import dash_bootstrap_components as dbc
external_stylesheets =  'https://codepen.io/chriddyp/pen/bWLwgP.css'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app.css.append_css({"external_url": 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
#app = dash.Dash(__name__)
app.layout = html.Div(
    children = [
        html.H1(
            className = "row",
            style = {'textAlign': 'center', 'font-size': '30px'},
            children = [
                html.Div(children= 'Prime Time: Interesting Trivia Finder')
            ]
        ),
        html.Div(
            className = "row",
            id = 'classification-div',
            style = {},
            children = [
                html.Div(
                    className = "six columns",
                    style = {'display': 'inline-block'},
                    children = [
                        dcc.RadioItems(
                            className = "row",
                            id = 'radio-button',
                            labelStyle = {'display': 'inline-block', 'textAlign': 'center'},
                            options = [{'label': i, 'value': i} for i in ['Conflict', 'Comparison']],
                            style = {'textAlign': 'center', 'font-size': '20px'},
                            value = 'Conflict',
                        ),
                        dash_table.DataTable(
                            id = 'table',
                            style_cell = {'textAlign': 'left', 'whiteSpace': 'normal'},
                            columns = [{"name": i, "id": i} for i in ["Trivia"]],
                            data = [{}]
                        )
                    ]
                ),
                html.Div(
                    className="six columns" ,
                    style = {'display': 'inline-block'},
                    children = [
                        html.Div(
                            className = "row",
                            id = 'graph'
                        ),
                        html.Div(
                            className = "row",
                            id = 'stats',
                            style = {'padding-left':'15%'},
                        )
                    ]
                )
            ]
        )
    ]
)

def App():
    return app.layout

def Result(value, rows, selected_row_indices):
    pickle_file = 'trivia_output2.pickle'
    with open(pickle_file, 'rb') as handle:
        result_dict = pickle.load(handle)

    conflict_trivia_df = result_dict['conflict_trivia_df']
    conflict_trivia_evidence_df = result_dict['conflict_trivia_evidence_df']
    comparison_trivia_df = result_dict['comparison_trivia_df']
    comparison_trivia_evidence_df = result_dict['comparison_trivia_evidence_df']

    if value == 'Conflict':
        trivia_df = pd.DataFrame(conflict_trivia_df[["Trivia"]])
        evidence_df = pd.DataFrame(conflict_trivia_evidence_df[['Stats','Overl_dist_graph']])
    elif value == 'Comparison':
        trivia_df = pd.DataFrame(comparison_trivia_df[["Trivia"]])
        evidence_df = pd.DataFrame(comparison_trivia_evidence_df[['Stats','Overl_dist_graph']])
    data = trivia_df.to_dict('records')

    if selected_row_indices is None:
        r = 0
    else:
        r = selected_row_indices['row']
    # print('selected row = ', r)

    subgroup_values_list = evidence_df.iloc[r]['Overl_dist_graph']
    subgroup1 = subgroup_values_list[0]
    subgroup2 = subgroup_values_list[1]

    subgroup_stats_list = evidence_df.iloc[r]['Stats']
    stat1_dict = subgroup_stats_list[0]
    stat2_dict = subgroup_stats_list[1]

    col_list = ['Stats','Subgroup 1' , 'Subgroup 2']
    col_value_list = ['count' , 'mean' , 'median' , 'var' , 'std']
    stat1_dict_values = [value for value in stat1_dict.values()]
    stat2_dict_values = [value for value in stat2_dict.values()]
    values_list = [col_value_list, stat1_dict_values, stat2_dict_values]

    subgroup1_mu = np.mean(subgroup1)
    subgroup1_sigma = np.std(subgroup1)
    new_subgroup1 = np.linspace(subgroup1_mu - 3*subgroup1_mu, subgroup1_mu + 3*subgroup1_sigma, 100)
    subgroup2_mu = np.mean(subgroup2)
    subgroup2_sigma = np.std(subgroup2)
    new_subgroup2 = np.linspace(subgroup2_mu - 3*subgroup2_mu, subgroup2_mu + 3*subgroup2_sigma, 100)
    hist_data = [new_subgroup1, new_subgroup2]
    group_labels = ['Group 1', 'Group 2']
    fig = ff.create_distplot(hist_data, group_labels, bin_size=.5, show_hist=False, show_rug=False, colors=['#333F44', '#37AA9C'])
    fig.update_layout(title_text='Curve Plot',width=700, height=400)

    return [
        data,
        dcc.Graph(
            id='column',
            figure=fig
        ),
        html.Table(
            [ #Header
                html.Tr(
                    [html.Th(col) for col in col_list],
                )
            ] +
            [ #Body
                html.Tr(
                    [html.Td((values_list[j][i])) for j in range(3)]
                ) for i in range(4)
            ],
        )
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
