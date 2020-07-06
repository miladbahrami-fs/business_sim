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


def safe_div(n, d):
    return n / d if d else 0

def get_conversion_rate(expected, stdev):
    conversion_rate = max(np.random.normal(expected,stdev),
                          0.001)
    return conversion_rate

# assume min clv = 1


def get_clv(expected, stdev):
    clv = max(np.random.normal(expected,stdev),
                          1)
    return clv

# Function for calculating the new customer of a marketing campaign

def get_new_leads(budget,cost_per_click,click_to_lead):
    return np.random.binomial(budget/cost_per_click,click_to_lead)

def get_new_customer(leads, lead_to_client):
    return np.random.binomial(leads, lead_to_client)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.H1(
            id='header-state',
            children='Deriv Marketing Campaign Simulation',style={'text=align':'center'}),

        html.Div(
            id='parameter-state',
            children=[
                html.H3('''Please enter your campaing parameters for simulation :'''),
                html.Label('Campaign Budget'),
                dcc.Input(
                    id='budget-inp',
                    type="number",
                    value=1000,
                    placeholder='Campaign Budget'),
                html.Label('Cost Per Click'),
                dcc.Input(
                    id='cpc-inp',
                    type='number',
                    value=1.75,
                     placeholder='Cost Per Click'),
                html.Label('Click To Lead Ratio'),
                dcc.Input(
                    id='ctl-inp',
                    type="number",
                    value=0.2,
                    placeholder='Click to lead ratio'),
                html.Label('Lead To New Client Ratio'),
                dcc.Input(
                    id='ltc-inp',
                    type="number",
                    value=0.2,
                    placeholder='lead to new client ratio'),
                html.Label('Expected CLV'),
                dcc.Input(
                    id='clv-inp',
                    type='number',
                    value=58,
                    placeholder='Expected CLV'),
                html.Br(),
                html.Br(),
                html.Button(
                    id='submit-button-state',
                    n_clicks=0,
                    children='Simulate')
            ],style={'padding-left':'5%'}),

        html.Div(
            id='output-state',
            children=[
                dcc.Graph(id='clv'),
                dcc.Graph(id='cpa'),
                dcc.Graph(id='cpl'),
                dcc.Graph(id='clv-cpa'),
                dcc.Graph(id='new-customer'),
                dcc.Graph(id='campaign-ltv'),
                dcc.Graph(id='campaign-return')]),
    
        html.Div(
            id='summary-state',
            children=[
                html.H2('Simulation Summary'),
                html.Table(
                    children=[
                        html.Tr([html.Td('Expected Customer Life Time Value'), html.Td(id='summary-clv')]),
                        html.Tr([html.Td('Mean Cost Per Acquisition'), html.Td(id='summary-cpa')]),
                        html.Tr([html.Td('Mean Cost Per Lead'), html.Td(id='summary-cpl')]),
                        html.Tr([html.Td('Mean CLV - CPA'), html.Td(id='summary-clv-cpa')]),
                        html.Tr([html.Td('Mean Number of New Customers'), html.Td(id='summary-new-customer')]),
                        html.Tr([html.Td('Mean Campaign LTV'), html.Td(id='summary-ltv')]),
                        html.Tr([html.Td('Mean Campaign Return'), html.Td(id='summary-return')])
                    ],style={"margin-left":"auto","margin-right":"auto"})
            ],style={'text-align':'center'})
])

@app.callback(
    [Output('clv', 'figure'),
    Output('cpa','figure'),
    Output('cpl','figure'),
    Output('clv-cpa','figure'),
    Output('new-customer','figure'),
    Output('campaign-ltv','figure'),
    Output('campaign-return','figure'),
    Output('summary-clv','children'),
    Output('summary-cpa','children'),
    Output('summary-cpl','children'),
    Output('summary-clv-cpa','children'),
    Output('summary-new-customer','children'),
    Output('summary-ltv','children'),
    Output('summary-return','children')],
    [Input('submit-button-state','n_clicks')],
    [State('budget-inp', 'value'),
    State('cpc-inp','value'),
    State('ctl-inp', 'value'),
    State('ltc-inp', 'value'),
    State('clv-inp','value')])
def update_figure(n_clicks, budget, cpc, ctl, ltc, clv):

    # Conversion rate, depends on we look at cpc or cpm
    # here i use cpc, and hence the conversion rate is click > lead(virtual) > real , as we dont really care roi of camp for BA (which use cpm)
    spend=budget
    # visitor > real signup
    click_to_lead_expected = ctl 
    lead_to_client_expected = ltc
    # conversion rate is (click to lead ratio) * (lead to client ratio)
    # i will use 20% of std for now as the spreadsheet dont provide the std of india
    click_to_lead_stdev = click_to_lead_expected * 0.1
    lead_to_client_stdev = lead_to_client_expected * 0.1
    # from the spreadsheet only have clv_d14, but i would suggest to use clv_d60 as 2 months more or less represent the whole cycle of a client
    # similar approach with conversion,
    clv_expected = clv
    # similar to conversion rate
    clv_stdev = clv_expected * 0.2

    # Let's call it to get the number of new customers from our campaign
    # click_to_lead = get_conversion_rate(click_to_lead_expected,
    #                                     click_to_lead_stdev)
    
    # lead_to_client = get_conversion_rate(lead_to_client_expected,
    #                                     lead_to_client_stdev)
    
    # leads = get_new_leads(spend,cpc,click_to_lead)
    # new_customer_count = get_new_customer(leads,lead_to_client)
    # And calculate our cost per acquisition (CPA)
    # cpa = safe_div(spend,new_customer_count)
    # get clv
    # clv=get_clv(clv_expected, clv_stdev)
    # calculate total campaign value
    # campaign_ltv=clv * new_customer_count

    # Simulate 1000 times and look at the distributions
    new_customer_count_list=[]
    cpa_list=[]
    cpl_list=[]
    clv_list=[]
    campaign_ltv_list=[]

    for _ in range(1000):

        # Run marketing campaign sim
        click_to_lead = get_conversion_rate(click_to_lead_expected,
                                        click_to_lead_stdev)
    
        lead_to_client = get_conversion_rate(lead_to_client_expected,
                                        lead_to_client_stdev)
        leads = get_new_leads(spend,cpc,click_to_lead)
        new_customer_count = get_new_customer(leads,lead_to_client)
        
        if new_customer_count == 0 :
            continue

        cpl=spend/leads    
        cpa=spend/new_customer_count
        clv=get_clv(clv_expected, clv_stdev)
        campaign_ltv=clv * new_customer_count

        new_customer_count_list.append(new_customer_count)
        cpa_list.append(cpa)
        cpl_list.append(cpl)
        clv_list.append(clv)
        campaign_ltv_list.append(campaign_ltv)


    # Store simulation results in a dataframe
    results_df=pd.DataFrame()
    results_df['new_customer_count']=new_customer_count_list
    results_df['clv']=clv_list
    results_df['cpa']=cpa_list
    results_df['cpl']=cpl_list
    results_df['clv - cpa']=results_df['clv'] - results_df['cpa']
    results_df['campaign_ltv']=campaign_ltv_list
    results_df['campaign_return']=np.array(campaign_ltv_list) - spend

    
    # fig=ff.create_distplot([results_df[c] for c in columns], columns)
    # fig = make_subplots(rows=3, cols=1)
    # fig.add_trace(ff.create_distplot([results_df['clv']],['CLVDist']),row=1,col=1)
    # fig.add_trace(ff.create_distplot([results_df['cpa']],['CPADist']),row=2,col=1)
    fig_clv=ff.create_distplot([results_df['clv']],['CLV'],colors=['rgb(0, 0, 100)'])
    fig_clv.update_layout(title_text='Customer Life Time Value')
    
    fig_cpa=ff.create_distplot([results_df['cpa']],['CPA'])
    fig_cpa.update_layout(title_text='Cost Per Acquisition')

    fig_cpl=ff.create_distplot([results_df['cpl']],['CPL'])
    fig_cpl.update_layout(title_text='Cost Per Lead')

    fig_new_customer=ff.create_distplot([results_df['new_customer_count']],['new customer count'],colors=['rgb(0, 200, 200)'])
    fig_new_customer.update_layout(title_text='New Customer Count')

    fig_clv_cpa=ff.create_distplot([results_df['clv - cpa']],['CLV - CPA'])
    fig_clv_cpa.update_layout(title_text='CLV - CPA')

    fig_campaign_ltv=ff.create_distplot([results_df['campaign_ltv']],['Campaign LTV'],colors=['magenta'])
    fig_campaign_ltv.update_layout(title_text='Campaign LTV')

    fig_campaign_return=ff.create_distplot([results_df['campaign_return']],['Campaign Return'])
    fig_campaign_return.update_layout(title_text='Campaign Return')

    mean_new_customer=round(results_df['new_customer_count'].mean())
    mean_cpa=round(results_df['cpa'].mean(),2)
    mean_cpl=round(results_df['cpl'].mean(),2)
    mean_diff=round(results_df['clv - cpa'].mean(),2)
    mean_ltv=round(results_df['campaign_ltv'].mean(),2)
    mean_return=round(results_df['campaign_return'].mean(),2)
    
    return fig_clv, fig_cpa, fig_cpl, fig_clv_cpa, fig_new_customer,fig_campaign_ltv, fig_campaign_return, clv_expected, mean_cpa,mean_cpl ,mean_diff, mean_new_customer, mean_ltv, mean_return


if __name__ == '__main__':
    app.run_server(debug=True)
