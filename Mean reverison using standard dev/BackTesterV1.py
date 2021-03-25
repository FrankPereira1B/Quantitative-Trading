# -*- coding: utf-8 -*-
"""
@author: Frank R Pereira and Melroy Pereira
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import dash
import dash_table
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
from plotly import graph_objects as go

#here strategy will send the predicted signals.

class BackTester:
    
    def __init__(self, strategy, data, lookback, lots, deposit):
        self.data = data
        self.lookback = lookback
        self.lots = lots
        self.deposit = deposit
        self.trading = strategy
    
    def DataCenter(self, start):
        n = start
        stop = n+self.lookback+1
        lookback_data = self.data.iloc[start:stop, :]
        return (lookback_data)
       
    def RunStrategy(self, data_df):
        signal = self.trading(data_df)
        return (signal)
    
    def PandLCalculator(self, data_df, pred):
        df = data_df.copy()
        df = round(df, 4)
        df['Signal'] = np.where(df['Open'] < df['Close'], 1, -1)
        df = df.iloc[self.lookback:, :]
        df['Pred'] = pred
        # return calculator
        ret = []
        for ix, sig in zip(df.index, df['Pred']):
            if (sig == 1):
                ret.append((df['Close'][ix]-df['Open'][ix])*10000*10*self.lots)
            elif (sig == -1):
                ret.append((df['Open'][ix]-df['Close'][ix])*10000*10*self.lots)
            else:
                ret.append(0)
        df['Return'] = ret
        # P&L Calculator
        pl = []
        dep = 10000
        for r in df['Return']:
            dep = dep + r
            pl.append(dep)
        df['P&L'] = pl
        return (df)
    
    def DashBoard(self, pos):
        #creating web app name
        app = JupyterDash(__name__)

        #colors and style
        colors = {'background':"darkslategrey",
                 'text': "cyan"}
        style = {'textAlign': 'right',
                'color':"cyan"}

        app.layout = html.Div(style = {'backgroundColor': colors['background']},children = [
            html.H1(children = "Backtesting Forex Strategy",                                  #header
                    style = {'textAlign': 'center',
                             'color':colors['text']}),

            html.Div([                                                                       #division for plotting
                html.Label(['Forex strategy type'],
                          style = style),
                dcc.Dropdown(                                                                 # dropdown method
                    id='my_dropdown',
                    options=[
                             {'label': 'Long only', 'value': 'P&L_Buy'},                  #dropdown labels
                             {'label': 'Short only', 'value': 'P&L_Sell'},
                             {'label': 'Long-Short', 'value': 'P&L'},
                    ],
                    value = 'P&L',
                    multi=False,
                    clearable=False,
                    style={"width": "50%"}
                ),
            ]),
            html.Div([
                html.Label(["Strategy Report"],                                           #label for the each division
                          style = style),
                html.Label(["P&L for the strategy"], 
                          style = style),
                dcc.Graph(id='the_graph')]),                                        #we plot here by taking the id of that plot  
        ])

        @app.callback(                                                   #callback function for chnage in input of dropdown
            Output(component_id='the_graph', component_property='figure'),
            [Input(component_id='my_dropdown', component_property='value')]
        )

        def update_graph(my_dropdown):

            if (my_dropdown == "P&L"):
                df = pos
                fig_ = go.Figure()
                fig_.add_traces(data = go.Scatter(y = pos['P&L'], name = "P&L_"))
                fig_.update_layout(title = "P&L from both long and short", title_x = 0.5,
                          plot_bgcolor = colors['background'],
                          paper_bgcolor = colors['text'],  xaxis_title = "Toatal Data", yaxis_title = "Profit",
                                  width = 1300, height = 500,
                                  xaxis = {'showgrid': False},
                                  yaxis = {'showgrid':False})
            elif (my_dropdown == "P&L_Buy"):
                df = pos
                fig_ = go.Figure()
                fig_.add_traces(data = go.Scatter(y = pos['P&L'].loc[pos.loc[pos['Pred']==1].index], name = "P&L_"))
                fig_.update_layout(title = "P&L from long only", title_x = 0.5,
                          plot_bgcolor = colors['background'],
                          paper_bgcolor = colors['text'], xaxis_title = "Total Data", yaxis_title = "Profit",
                                  width = 1300, height = 500,
                                  xaxis = {'showgrid': False},
                                  yaxis = {'showgrid':False})
            elif (my_dropdown == "P&L_Sell"):
                df = pos
                fig_ = go.Figure()
                fig_.add_traces(data = go.Scatter(y = pos['P&L'].loc[pos.loc[pos['Pred']==0].index], name = "P&L_"))
                fig_.update_layout(title = "P&L from short only", title_x = 0.5,
                          plot_bgcolor = colors['background'],
                          paper_bgcolor = colors['text'], xaxis_title = "Total Data", yaxis_title = "Profit",
                                  width = 1300, height = 500,
                                  xaxis = {'showgrid': False},
                                  yaxis = {'showgrid':False})
            return (fig_)
        app.run_server(mode = 'external', port = 9181)
        return
        
    
    def Backtest(self):
        positions = []
        for l in range(self.data.shape[0]-self.lookback):
            data_df = self.DataCenter(l)
            signal = self.RunStrategy(data_df)
            positions.append(int(signal))
        analysis = self.PandLCalculator(self.data, positions)
        dashb = self.DashBoard(analysis)
        return (analysis)
