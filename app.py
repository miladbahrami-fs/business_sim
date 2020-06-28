import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.figure_factory as ff

# 1) Define functions
# assuming conversion rate and clv follows normal distribution
# from the expected(avg) and stdev of it, get the realized value

#assume min conver rate = 0.1%
def get_conversion_rate(expected, stdev):
    conversion_rate = max(expected + np.random.normal()*stdev, 
                          0.001)
    return conversion_rate

#assume min clv = 1 
def get_clv(expected, stdev):
    clv  = max(expected + np.random.normal()*stdev, 
                          1)
    return clv

# Function for calculating the new customer of a marketing campaign
def get_new_customer(spend, cpc, conversion_rate):
    return np.random.binomial(spend/cpc, conversion_rate)
    
#variable
#we can discussed how we define each variables here

#take https://docs.google.com/spreadsheets/d/1ZeGzqvR4kq-xOT4sWPcQ5AwJBpp5aaRFDnr-MSQzuXA/edit#gid=0, India for example
spend = 1000
cpc = 1.73

# Conversion rate, depends on we look at cpc or cpm
#here i use cpc, and hence the conversion rate is click > lead(virtual) > real , as we dont really care roi of camp for BA (which use cpm)

#visitor > real signup
conversion_rate_expected = 0.0829
# i will use 20% of std for now as the spreadsheet dont provide the std of india
conversion_rate_stdev = conversion_rate_expected * 0.2

#from the spreadsheet only have clv_d14, but i would suggest to use clv_d60 as 2 months more or less represent the whole cycle of a client
#similar approach with conversion,
clv_avg = 58
#similar to conversion rate
clv_stdev = clv_avg * 0.2

# Let's call it to get the number of new customers from our campaign
conversion_rate = get_conversion_rate(conversion_rate_expected, 
                                      conversion_rate_stdev)
new_customer_count = get_new_customer(spend, cpc, conversion_rate)
# And calculate our cost per acquisition (CPA)
cpa = spend/new_customer_count
#get clv
clv = get_clv(clv_avg, clv_stdev)
#calculate total campaign value
campaign_ltv = clv * new_customer_count

print('Campagin Spend: ', spend)
print('Customers Gained: ', new_customer_count)
print('CPA: ', round(cpa, 2))
print('Total Cohort Value: ', int(campaign_ltv))
print('CLV: ', int(clv))
print('CLV-CPA: ', int(clv - cpa))

# Simulate 1000 times and look at the distributions
new_customer_count_list = []
cpa_list = []
clv_list = []
campaign_ltv_list = []

for i in range(1000):
    
    # Run marketing campaign sim
    conversion_rate = get_conversion_rate(conversion_rate_expected, 
                                      conversion_rate_stdev)
    new_customer_count = get_new_customer(spend, cpc, conversion_rate)
    
    cpa = spend/new_customer_count
    clv = get_clv(clv_avg, clv_stdev)
    campaign_ltv = clv * new_customer_count
    
    new_customer_count_list.append(new_customer_count)
    cpa_list.append(cpa)
    clv_list.append(clv)
    campaign_ltv_list.append(campaign_ltv)


# Store simulation results in a dataframe
results_df = pd.DataFrame()
results_df['new_customer_count'] = new_customer_count_list
results_df['clv'] = clv_list
results_df['cpa'] = cpa_list
results_df['clv - cpa'] = results_df['clv'] - results_df['cpa']
results_df['campaign_ltv']= campaign_ltv_list
results_df['campaign_return'] = np.array(campaign_ltv_list) - spend

columns = results_df[['new_customer_count','cpa','campaign_return','clv - cpa']].columns

# fig, axes = plt.subplots(2,2,figsize = [12,12], 
#                         gridspec_kw={'wspace': 0})

# for column, ax in zip(columns,axes.flat) :
    
#     sns.distplot(results_df[column], 
#              ax=ax)
fig = ff.create_distplot([results_df[c] for c in columns],columns,
                         curve_type='normal')

# Add title
fig.update_layout(title_text='CPA with Normal Distribution')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Graph(id='graph-normal',figure=fig)
])

# @app.callback(
#     Output('graph-with-slider', 'figure'),
#     [Input('year-slider', 'value')])
# def update_figure(selected_year):
#     filtered_df = df[df.year == selected_year]
#     traces = []
#     for i in filtered_df.continent.unique():
#         df_by_continent = filtered_df[filtered_df['continent'] == i]
#         traces.append(dict(
#             x=df_by_continent['gdpPercap'],
#             y=df_by_continent['lifeExp'],
#             text=df_by_continent['country'],
#             mode='markers',
#             opacity=0.7,
#             marker={
#                 'size': 15,
#                 'line': {'width': 0.5, 'color': 'white'}
#             },
#             name=i
#         ))

#     return {
#         'data': traces,
#         'layout': dict(
#             xaxis={'type': 'log', 'title': 'GDP Per Capita',
#                    'range':[2.3, 4.8]},
#             yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
#             margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest',
#             transition = {'duration': 500},
#         )
#     }


if __name__ == '__main__':
    app.run_server(debug=True)