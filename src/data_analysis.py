#imports
import os
import pathlib

import dash
import json
from datetime import date

from dash import dcc, dash_table, html

import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_uploader as du

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np

#--------------------------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP] #SUPERHERO, BOOTSTRAP, ZEPHYR
)
server = app.server
app.title = "LIFE D1.1"

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

#--------------------------------------------------------------------------------------------

def checklist():
    return html.Div(
    [
        html.Div([
            html.H3("Choose Scenario"),
            dbc.Checklist(
                options=[
                    {"label": "RE_UBL_LCZ6", "value": "RE_UBL_LCZ6"},
                    {"label": "RE_UCM_LCZ6", "value": "RE_UCM_LCZ6"}
                ],
                value=["RE_UBL_LCZ6"],
                id="checklist-input1",
            ),
            html.H3("Choose Roof Type"),
            dbc.Checklist(
                options=[
                    {"label": "01_HBR", "value": "01_HBR"},
                    {"label": "02_COOL", "value": "02_COOL"},
                    {"label": "03_GREEN", "value": "03_GREEN"},
                    {"label": "04_WATERPROOF", "value": "04_WATERPROOF"},
                    {"label": "05_METAL", "value": "05_METAL"}
                ],
                value=["01_HBR"],
                id="checklist-input2",
            ),
        ],
        style={
            'margin' : 'auto',
            'text-align' : 'center',
            'width': '15%',
        }
        ),
        html.Hr(),
        html.Div(id='checklist-output'),
        html.Div(id='checklist-output-scatter'),
        html.Div(id='checklist-output-roof')
    ]
)

#--------------------------------------------------------------------------------------------

@app.callback(
    Output('checklist-output','children'),
    [Input('checklist-input1','value'),
     Input('checklist-input2','value')]
)

def render_checklist_output(list_scenario, list_roof):
    container_tmean = []
    container_tsum = []
    container_tmean5max = []
    container_uhii = []
    container_qhvac = []

    for i in list_scenario:
        for k in sorted(list_roof):
            df = pd.read_excel('./{}/{}/results/I-O_matrix.xlsx'.format(i,k), header = 0)
            df_tmean = df[['Tmean']].rename(columns={'Tmean':'{}-{}'.format(i,k)})
            container_tmean.append(df_tmean)
            df_tsum = df[['Tsum']].rename(columns={'Tsum':'{}-{}'.format(i,k)})
            container_tsum.append(df_tsum)
            df_tmean5max = df[['Tmean5max']].rename(columns={'Tmean5max':'{}-{}'.format(i,k)})
            container_tmean5max.append(df_tmean5max)
            df_uhii = df[['UHII']].rename(columns={'UHII':'{}-{}'.format(i,k)})
            container_uhii.append(df_uhii)
            df_qhvac = df[['Qhvac']].rename(columns={'Qhvac':'{}-{}'.format(i,k)})
            container_qhvac.append(df_qhvac)

    data_tmean = pd.concat(container_tmean, axis=1)
    data_tsum = pd.concat(container_tsum, axis=1)
    data_tmean5max = pd.concat(container_tmean5max, axis=1)
    data_uhii = pd.concat(container_uhii, axis=1)
    data_qhvac = pd.concat(container_qhvac, axis=1)

    fig_tmean_box = px.box(data_tmean)#, y=data_tmean.columns, color_discrete_sequence=px.colors.qualitative.Pastel)

    fig_tsum_bar = px.bar(data_tsum.mean(axis=0), text_auto='.5s', color = data_tsum.mean(axis=0).index)#, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_tsum_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig_tsum_bar.layout.update(showlegend=False)

    fig_tmean5max_box = px.box(data_tmean5max)#, y=data_tmean5max.columns, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_tmean5max_box = px.bar(data_tmean5max.mean(axis=0), text_auto='.5s', color = data_tmean5max.mean(axis=0).index)#, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_tmean5max_box.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig_tmean5max_box.layout.update(showlegend=False)

    fig_uhii_box = px.box(data_uhii)#, y=data_uhii.columns, color_discrete_sequence=px.colors.qualitative.Pastel)

    fig_qhvac_box = px.box(data_qhvac)#, y=data_qhvac.columns, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_qhvac_bar = px.bar(data_qhvac.mean(axis=0), text_auto='.5s', color = data_qhvac.mean(axis=0).index)#, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_qhvac_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig_qhvac_bar.layout.update(showlegend=False)

    return html.Div([
        html.H3('Canyon Mean Air Temperature'),
        dcc.Graph(figure=fig_tmean_box),
        html.Hr(),
        html.H3('Canyon Sum of Air Temperature (Summer)'),
        dcc.Graph(figure=fig_tsum_bar),
        html.Hr(),
        html.H3('Mean of 5% of Maximum Roof Surface Temperature'),
        dcc.Graph(figure=fig_tmean5max_box),
        html.Hr(),
        html.H3('UHI Intensity Mean'),
        dcc.Graph(figure=fig_uhii_box),
        html.Hr(),
        html.H3('Heat Waste from HVAC system'),
        dcc.Graph(figure=fig_qhvac_bar),
        dcc.Graph(figure=fig_qhvac_box),
        html.Hr()
    ])

#--------------------------------------------------------------------------------------------

@app.callback(
    Output('checklist-output-scatter','children'),
    [Input('checklist-input1','value'),
     Input('checklist-input2','value')]
)

def render_checklist_output(list_scenario, list_roof):
    fig_scatter = go.Figure()

    for i in list_scenario:
        for k in sorted(list_roof):
            df = pd.read_excel('./{}/{}/results/I-O_matrix.xlsx'.format(i,k), header = 0)[['_albedo_Roof','Tmean5max']].rename(columns={
                '_albedo_Roof':'{}-{}-albedo_Roof'.format(i,k),
                'Tmean5max':'{}-{}-Tmean5max'.format(i,k)
                })
            fig_scatter.add_trace(go.Scatter(
                x=df['{}-{}-albedo_Roof'.format(i,k)],
                y=df['{}-{}-Tmean5max'.format(i,k)],
                mode='markers',
                opacity=0.8,
                # marker_color='rgba(255, 182, 193, .9)',
                name='{}-{}'.format(i,k)
            ))
    fig_scatter.update_traces(mode='markers', marker_line_width=0, marker_size=10)
    # fig_scatter.layout.update(showlegend=False)
    return html.Div([
        html.H3('Scatter Plot Albedo - Tmean5max Roof'),
        dcc.Graph(figure=fig_scatter),
        html.Hr()
    ])


    
#--------------------------------------------------------------------------------------------


    
#--------------------------------------------------------------------------------------------


    
#--------------------------------------------------------------------------------------------


    
#--------------------------------------------------------------------------------------------


    
#--------------------------------------------------------------------------------------------

list_scenario_1 = ['RE_UBL_LCZ6','RE_UCM_LCZ6']
list_roof_1 = ['01_HBR','02_COOL','03_GREEN','04_WATERPROOF','05_METAL']
time = pd.DataFrame({'Date/Time': pd.date_range('2020-06-01','2020-09-01', freq='1H', closed='left')})
# re_ubl_lcz6_container_max = []
re_ubl_lcz6_container_mean = []
# re_ubl_lcz6_container_min = []
for i in list_scenario_1:
    for k in sorted(list_roof_1):
        df_3 = pd.read_excel('./{}/{}/results/Troof_profiles.xlsx'.format(i,k), header=0, index_col=0)
        # df_max = df_3.describe().loc[['max']].set_axis(['{}-{}'.format(i,k)])
        # re_ubl_lcz6_container_max.append(df_max)
        df_mean = df_3.describe().loc[['mean']].set_axis(['{}-{}'.format(i,k)])
        re_ubl_lcz6_container_mean.append(df_mean)
        # df_min = df_3.describe().loc[['min']].set_axis(['{}-{}'.format(i,k)])
        # re_ubl_lcz6_container_min.append(df_min)

# re_ubl_lcz6_max_tot = pd.concat(re_ubl_lcz6_container_max).T.set_index(time['Date/Time'])
re_ubl_lcz6_mean_tot = pd.concat(re_ubl_lcz6_container_mean).T.set_index(time['Date/Time'])
# re_ubl_lcz6_min_tot = pd.concat(re_ubl_lcz6_container_min).T.set_index(time['Date/Time'])

# print(re_ubl_lcz6_mean_tot)
    
#--------------------------------------------------------------------------------------------

@app.callback(
    Output('checklist-output-roof','children'),
    [Input('checklist-input1','value'),
     Input('checklist-input2','value')]
)

def render_checklist_timeseries_roof(list_scenario, list_roof):
    # re_ubl_lcz6_container_max2 = []
    re_ubl_lcz6_container_mean2 = []
    # re_ubl_lcz6_container_min2 = []
    for i in list_scenario:
        for k in sorted(list_roof):
            # df2_max = re_ubl_lcz6_max_tot[['{}-{}'.format(i,k)]]
            # re_ubl_lcz6_container_max2.append(df2_max)
            df2_mean = re_ubl_lcz6_mean_tot[['{}-{}'.format(i,k)]]
            re_ubl_lcz6_container_mean2.append(df2_mean)
            # df2_min = re_ubl_lcz6_min_tot[['{}-{}'.format(i,k)]]
            # re_ubl_lcz6_container_min2.append(df2_min)

    # re_ubl_lcz6_max = pd.concat(re_ubl_lcz6_container_max2, axis=1)
    re_ubl_lcz6_mean = pd.concat(re_ubl_lcz6_container_mean2, axis=1)
    # re_ubl_lcz6_min = pd.concat(re_ubl_lcz6_container_min2, axis=1)

    # fig_roof_max = go.Figure()
    # for column in re_ubl_lcz6_max.columns.to_list():
    #     fig_roof_max.add_trace(
    #         go.Scatter(
    #             x=re_ubl_lcz6_max.index,
    #             y=re_ubl_lcz6_max[column],
    #             name=column
    #         )
    #     )
    #     fig_roof_max.update_xaxes(
    #         rangeslider_visible=True,
    #         rangeselector=dict(
    #             buttons=list([
    #                 dict(count=1, label="1d", step="day", stepmode="backward"),
    #                 dict(count=7, label="1w", step="day", stepmode="backward"),
    #                 dict(count=2, label="1m", step="month", stepmode="backward"),
    #                 dict(step="all")
    #             ])
    #         )
    #     )

    fig_roof_mean = go.Figure()
    for column in re_ubl_lcz6_mean.columns.to_list():
        fig_roof_mean.add_trace(
            go.Scatter(
                x=re_ubl_lcz6_mean.index,
                y=re_ubl_lcz6_mean[column],
                name=column
            )
        )
        fig_roof_mean.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=2, label="1m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

    # fig_roof_min = go.Figure()
    # for column in re_ubl_lcz6_min.columns.to_list():
    #     fig_roof_min.add_trace(
    #         go.Scatter(
    #             x=re_ubl_lcz6_min.index,
    #             y=re_ubl_lcz6_min[column],
    #             name=column
    #         )
    #     )
    #     fig_roof_min.update_xaxes(
    #         rangeslider_visible=True,
    #         rangeselector=dict(
    #             buttons=list([
    #                 dict(count=1, label="1d", step="day", stepmode="backward"),
    #                 dict(count=7, label="1w", step="day", stepmode="backward"),
    #                 dict(count=2, label="1m", step="month", stepmode="backward"),
    #                 dict(step="all")
    #             ])
    #         )
    #     )

    return html.Div([
        # html.H3('Roof Timestep Max'),
        # dcc.Graph(figure=fig_roof_max),
        html.H3('Roof Timestep Mean'),
        dcc.Graph(figure=fig_roof_mean),
        # html.H3('Roof Timestep Min'),
        # dcc.Graph(figure=fig_roof_min),
        html.Hr()
    ])

#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------

app.layout = html.Div([
    checklist(),
    # timeseries_data(),    
    ],
    style={
        'margin' : 'auto',
        'text-align' : 'center',
        'width': '90%',
    }
)

#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------

#run app
if __name__ == '__main__':
    app.run_server(debug=False)