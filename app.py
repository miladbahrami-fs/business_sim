import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

# 1) Define functions
# assuming conversion rate and clv follows normal distribution
# from the expected(avg) and stdev of it, get the realized value

# assume min conver rate = 0.1%


def get_conversion_rate(expected, stdev):
    conversion_rate = max(expected + np.random.normal()*stdev,
                          0.001)
    return conversion_rate

# assume min clv = 1


def get_clv(expected, stdev):
    clv = max(expected + np.random.normal()*stdev,
                          1)
    return clv

# Function for calculating the new customer of a marketing campaign


def get_new_customer(spend, cpc, conversion_rate):
    return np.random.binomial(spend/cpc, conversion_rate)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(id='header-state',children='Deriv Marketing Campaign Simulation'),

    html.Div(id='parameter-state',children=[
        html.H3('''Please inter your campaing parameters for simulation.'''),
        html.Label('Spend Amount'),
        dcc.Input(
            id='spend-inp',
            type="number",
            value=1000,
            placeholder='Spend amount'),
        html.Label('Cost Per Click'),
        dcc.Input(
            id='cpc-inp',
            type='number',
            value=1.75,
            placeholder='Cost Per Click'),
        html.Label('Click To Lead'),
        dcc.Input(
            id='ctl-inp',
            type="number",
            value=0.2,
            placeholder='Click to lead ratio'),
        html.Label('CLV'),
        dcc.Input(
            id='clv-inp',
            type='number',
            value=58,
            placeholder='Expected CLV'),
        html.Button(
            id='submit-button-state',
            n_clicks=0,
            children='Simulate')]),

    html.Div(id='output-state',
    children=[
    dcc.Graph(id='clv'),
    dcc.Graph(id='cpa'),
    dcc.Graph(id='clv-cpa'),
    dcc.Graph(id='new-customer'),
    dcc.Graph(id='campaign-ltv'),
    dcc.Graph(id='campaign-return')]),
    
    html.Div(id='summary-state',children=[
        html.H2('Simulation Summary'),
        html.Table([
            html.Tr([html.Td('Expected Customer Life Time Value'), html.Td(id='summary-clv')]),
            html.Tr([html.Td('Mean Cost Per Acquisition'), html.Td(id='summary-cpa')]),
            html.Tr([html.Td('Mean CLV - CPA'), html.Td(id='summary-clv-cpa')]),
            html.Tr([html.Td('Mean Number of New Customers'), html.Td(id='summary-new-customer')]),
            html.Tr([html.Td('Mean Campaign LTV'), html.Td(id='summary-ltv')]),
            html.Tr([html.Td('Mean Campaign Return'), html.Td(id='summary-return')])
            ])
    ])
])

@app.callback(
    [Output('clv', 'figure'),
    Output('cpa','figure'),
    Output('clv-cpa','figure'),
    Output('new-customer','figure'),
    Output('campaign-ltv','figure'),
    Output('campaign-return','figure'),
    Output('summary-clv','children'),
    Output('summary-cpa','children'),
    Output('summary-clv-cpa','children'),
    Output('summary-new-customer','children'),
    Output('summary-ltv','children'),
    Output('summary-return','children')],
    [Input('submit-button-state','n_clicks')],
    [State('spend-inp', 'value'),
    State('cpc-inp','value'),
    State('ctl-inp', 'value'),
    State('clv-inp','value')])
def update_figure(n_clicks, spend, cpc, ctl, expected_clv):
    # variable
    # we can discussed how we define each variables here

    spend=spend
    cpc=cpc

    # Conversion rate, depends on we look at cpc or cpm
    # here i use cpc, and hence the conversion rate is click > lead(virtual) > real , as we dont really care roi of camp for BA (which use cpm)

    # visitor > real signup
    conversion_rate_expected=ctl
    # i will use 20% of std for now as the spreadsheet dont provide the std of india
    conversion_rate_stdev=conversion_rate_expected * 0.2

    # from the spreadsheet only have clv_d14, but i would suggest to use clv_d60 as 2 months more or less represent the whole cycle of a client
    # similar approach with conversion,
    clv_avg=expected_clv
    # similar to conversion rate
    clv_stdev=clv_avg * 0.2

    # Let's call it to get the number of new customers from our campaign
    conversion_rate=get_conversion_rate(conversion_rate_expected,
                                        conversion_rate_stdev)
    new_customer_count=get_new_customer(spend, cpc, conversion_rate)
    # And calculate our cost per acquisition (CPA)
    cpa=spend/new_customer_count
    # get clv
    clv=get_clv(clv_avg, clv_stdev)
    # calculate total campaign value
    campaign_ltv=clv * new_customer_count

    # Simulate 1000 times and look at the distributions
    new_customer_count_list=[]
    cpa_list=[]
    clv_list=[]
    campaign_ltv_list=[]

    for _ in range(1000):

        # Run marketing campaign sim
        conversion_rate=get_conversion_rate(conversion_rate_expected,
                                        conversion_rate_stdev)
        new_customer_count=get_new_customer(spend, cpc, conversion_rate)

        cpa=spend/new_customer_count
        clv=get_clv(clv_avg, clv_stdev)
        campaign_ltv=clv * new_customer_count

        new_customer_count_list.append(new_customer_count)
        cpa_list.append(cpa)
        clv_list.append(clv)
        campaign_ltv_list.append(campaign_ltv)


    # Store simulation results in a dataframe
    results_df=pd.DataFrame()
    results_df['new_customer_count']=new_customer_count_list
    results_df['clv']=clv_list
    results_df['cpa']=cpa_list
    results_df['clv - cpa']=results_df['clv'] - results_df['cpa']
    results_df['campaign_ltv']=campaign_ltv_list
    results_df['campaign_return']=np.array(campaign_ltv_list) - spend

    
    # fig=ff.create_distplot([results_df[c] for c in columns], columns)
    # fig = make_subplots(rows=3, cols=1)
    # fig.add_trace(ff.create_distplot([results_df['clv']],['CLVDist']),row=1,col=1)
    # fig.add_trace(ff.create_distplot([results_df['cpa']],['CPADist']),row=2,col=1)
    fig_clv=ff.create_distplot([results_df['clv']],['CLV'])
    fig_clv.update_layout(title_text='Customer Life Time Value')
    
    fig_cpa=ff.create_distplot([results_df['cpa']],['CPA'])
    fig_cpa.update_layout(title_text='Cost Per Acquisition')

    fig_new_customer=ff.create_distplot([results_df['new_customer_count']],['new customer count'])
    fig_new_customer.update_layout(title_text='New Customer Count')

    fig_clv_cpa=ff.create_distplot([results_df['clv - cpa']],['CLV - CPA'])
    fig_clv_cpa.update_layout(title_text='CLV - CPA')

    fig_campaign_ltv=ff.create_distplot([results_df['campaign_ltv']],['Campaign LTV'])
    fig_campaign_ltv.update_layout(title_text='Campaign LTV')

    fig_campaign_return=ff.create_distplot([results_df['campaign_return']],['Campaign Return'])
    fig_campaign_return.update_layout(title_text='Campaign Return')

    mean_new_customer=round(results_df['new_customer_count'].mean(),2)
    mean_cpa=round(results_df['cpa'].mean(),2)
    mean_diff=round(results_df['clv - cpa'].mean(),2)
    mean_ltv=round(results_df['campaign_ltv'].mean(),2)
    mean_return=round(results_df['campaign_return'].mean(),2)
    
    return fig_clv, fig_cpa, fig_clv_cpa, fig_new_customer,fig_campaign_ltv, fig_campaign_return, expected_clv,mean_cpa, mean_diff, mean_new_customer, mean_ltv, mean_return


if __name__ == '__main__':
    app.run_server(debug=True)
