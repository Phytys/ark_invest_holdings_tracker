# Imports
from datetime import date, datetime, timedelta
from urllib.request import Request, urlopen                     # to automatically download csv files from url
import numpy as np
import pandas as pd                                             # for data analyses
import plotly.graph_objects as go                               # to plot interactive graphs
from plotly.subplots import make_subplots                       # to plot subplots                      
from tradingview_ta import TA_Handler, Interval                 # to get tech analyses from tradingview
import yfinance as yf                                           # to get ticker candlestick data from Yahoo finance
from pytrends.request import TrendReq                           # connect to google api to get search statistics

import dash                                                     # For Dash App
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output, State

### CONTENT ##########################################################################################
# 1. Help functions
# 2. Dash App


### 1. Help functions #################################################################################

# A dict where we map etf ticker to etf name. So we can easily translate from symbol to name
dict_ark_holdings = {
                 "ALL": "All ARK ETF funds combined",
                 "ARKF": "ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS",
                 "ARKG": "ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS",
                 "ARKK": "ARK_INNOVATION_ETF_ARKK_HOLDINGS",
                 "ARKQ": "ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS",
                 "ARKW": "ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS",
                 "IZRL": "ARK_ISRAEL_INNOVATIVE_TECHNOLOGY_ETF_IZRL_HOLDINGS",
                 "PRNT": "THE_3D_PRINTING_ETF_PRNT_HOLDINGS"
                }

# A function return company name from ticker name
def get_company_name(ticker):
    df = pd.read_csv("data/ark_holdings_latest.csv")
    df = df.groupby(["ticker"]).last()
    d = df.company.to_dict()
    company = d[ticker]
    return company

# get historical candlestick market data, valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def my_ticker(ticker, ticker_period):
    # https://pypi.org/project/yfinance/
    ticker = yf.Ticker(ticker)
    df = ticker.history(period=ticker_period)
    return df

# Get google search trend from keword list
def google_trend(kwd_list, google_time_period):
    # https://pypi.org/project/pytrends/
    # kwds_list input as list []
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(kwd_list, cat=0, timeframe=google_time_period, geo='', gprop='')
    df = pytrends.interest_over_time()
    return df

# Get Tech Analyses (TA) recommendation from trading view
def tradingview_rec(ticker, timeframe):
    try:
        if timeframe == "week":
            handler = TA_Handler(
                symbol=ticker,
                screener="america",
                exchange="NASDAQ",
                interval=Interval.INTERVAL_1_WEEK
            )
        elif timeframe == "month":
            handler = TA_Handler(
                symbol=ticker,
                screener="america",
                exchange="NASDAQ",
                interval=Interval.INTERVAL_1_MONTH
            )
        return handler.get_analysis().summary
    except:
        return "Could not fetch recommendation"


### 2. Dash App #####################################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = {
    'background': '#ffffff',
    'text': '#002266'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H1('ARK Invest tracker'),
        html.Div(id='last-downloaded-text'),
        dcc.Graph(id='graph-holdings-per-etf'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000_000, # in milliseconds
            n_intervals=0
        ),
        html.H3('Holdings weight per fund'),
        ####################################
        dcc.Dropdown(
            id='weight-fund-dropdown',
            options=[
                {'label': 'ALL_FUNDS', 'value': 'ALL'},
                {'label': 'ARK_FINTECH_INNOVATION_ETF_ARKF', 'value': 'ARKF'},
                {'label': 'ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG', 'value': 'ARKG'},
                {'label': 'ARK_INNOVATION_ETF_ARKK', 'value': 'ARKK'},
                {'label': 'ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ', 'value': 'ARKQ'},
                {'label': 'ARK_NEXT_GENERATION_INTERNET_ETF_ARKW', 'value': 'ARKW'},
                {'label': 'ARK_ISRAEL_INNOVATIVE_TECHNOLOGY_ETF_IZRL', 'value': 'IZRL'},
                {'label': 'THE_3D_PRINTING_ETF_PRNT_HOLDINGS', 'value': 'PRNT'},
            ],
            value='ARKK',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        dcc.Dropdown(
            id='weight-threshold-dropdown',
            options=[
                {'label': 'Weight > 1 %', 'value': 1},
                {'label': 'Weight > 2 %', 'value': 2},
                {'label': 'Weight > 3 %', 'value': 3},
                {'label': 'Weight > 4 %', 'value': 4},
                {'label': 'Weight > 5 %', 'value': 5},
            ],
            value=3,
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        dcc.Graph(id='graph-holdings-weight'),
        dcc.Slider(
            id="holdings-weight-day-slider",
            min=0,
            max=30,
            step=None,
            marks={
                1: '1 Day',
                3: '3 Days',
                5: '5 Days',
                7: '7 Days',
                14: '14 Days',
                21: '21 Days',
                30: '30 Days'
            },
            value=3
        ),
        html.Br(),html.Br(),
        html.H3('Holdings changes'),
        ####################################
        dcc.Dropdown(
            id='changes-fund-dropdown',
            options=[
                {'label': 'ALL_FUNDS', 'value': 'ALL'},
                {'label': 'ARK_FINTECH_INNOVATION_ETF_ARKF', 'value': 'ARKF'},
                {'label': 'ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG', 'value': 'ARKG'},
                {'label': 'ARK_INNOVATION_ETF_ARKK', 'value': 'ARKK'},
                {'label': 'ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ', 'value': 'ARKQ'},
                {'label': 'ARK_NEXT_GENERATION_INTERNET_ETF_ARKW', 'value': 'ARKW'},
                {'label': 'ARK_ISRAEL_INNOVATIVE_TECHNOLOGY_ETF_IZRL', 'value': 'IZRL'},
                {'label': 'THE_3D_PRINTING_ETF_PRNT_HOLDINGS', 'value': 'PRNT'},
            ],
            value='ARKK',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        dcc.Dropdown(
            id='toplist-size-dropdown',
            options=[
                {'label': 'Top 5', 'value': 5},
                {'label': 'Top 10', 'value': 10},
                {'label': 'Top 15', 'value': 15},
                {'label': 'Top 20', 'value': 20},
                {'label': 'Top 25', 'value': 25},
            ],
            value=10,
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        dcc.Graph(id='graph-holdings-changes'),
        dcc.Slider(
            id="holdings-changes-day-slider",
            min=0,
            max=30,
            step=None,
            marks={
                1: '1 Day',
                3: '3 Days',
                5: '5 Days',
                7: '7 Days',
                14: '14 Days',
                21: '21 Days',
                30: '30 Days'
            },
            value=7
        ),
        html.Br(),html.Br(),
        html.H3('Plot Ticker'),
        ####################################
        dcc.Dropdown(
            id='ticker-mode-dropdown',
            options=[
                {'label': 'Mode: Ticker vs BTC', 'value': 'ticker_vs_btc'},
                {'label': 'Mode: Ticker vs Google trend search', 'value': 'ticker_vs_google_search'},
            ],
            value='ticker_vs_google_search',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        dcc.Input(id='ticker-input-on-submit', type='text', value="TSLA"),
        html.Button('Submit', id='submit-val', n_clicks=0),
        html.Div(id='container-button-basic',
            children='Enter ticker id, port and press submit'),
        dcc.Graph(id='ticker-graph'),



    ])
)


@app.callback(Output('last-downloaded-text', 'children'),
              Input('interval-component', 'n_intervals'))
def last_downloaded_date(n):
    # Read in one row from latest downloade dataframe, and return date
    df = pd.read_csv("data/ark_holdings_latest.csv", nrows=1)
    ark_latest_update = df["date"].iloc[-1]
    
    return f"Last downloaded: {ark_download_time},  Holdings last updated by Ark Invest: {ark_latest_update}"



@app.callback(Output('graph-holdings-per-etf', 'figure'),
              Input('interval-component', 'n_intervals'))
def download_holdings(n):
    # This function download latest ark holdings csv files every 20 minutes (set in dcc.Interval)
    # And plot number of holdings per ETF fund

    global ark_download_time
    ark_download_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    arkf_url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv"
    arkg_url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.csv"
    arkk_url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv"
    arkq_url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv"
    arkw_url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv"
    izrl_url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_ISRAEL_INNOVATIVE_TECHNOLOGY_ETF_IZRL_HOLDINGS.csv"
    prnt_url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/THE_3D_PRINTING_ETF_PRNT_HOLDINGS.csv"  

    # Creating a list of the urls
    ark_urls = [arkf_url, arkg_url, arkk_url, arkq_url, arkw_url, izrl_url, prnt_url]

    list_of_df = []
    
    # loop over all urls
    for ark_url in ark_urls:
        req = Request(ark_url)
        # Make the website think that I am manually downloading the csv from a browser (or it will return "forbidden")
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')

        content = urlopen(req)
        df = pd.read_csv(content)
        df.dropna(inplace=True)
        print(ark_url)
        print("Shape of df: ", df.shape)
        list_of_df.append(df)
    
    # Concatenating all files into one dataframe
    df = pd.concat(list_of_df)
    
    # save current holdings with date
    yesterday = date.today() - timedelta(days=1)
    df.to_csv(f"data/ark_holdings_{yesterday}.csv", index=False)
    df.to_csv(f"data/ark_holdings_latest.csv", index=False)
    
    # Plot number of holdings per fund
    fig = go.Figure()

    for fund in df["fund"].unique():
        fig.add_trace(go.Bar(x=[fund], y=[df.loc[df["fund"] == fund].shape[0]] , name= dict_ark_holdings[fund] ))

    fig.update_layout(template="plotly_white", 
                  title="Number of holdings per ETF (yesterday)",
                  yaxis_title="# holdings")
    return fig

# Holdings weight per fund
@app.callback(Output('graph-holdings-weight', 'figure'),
              [Input('weight-fund-dropdown', 'value'),
              Input('weight-threshold-dropdown', 'value'),
              Input('holdings-weight-day-slider', 'value'),]
              )
def holdings_weight(fund, threshold, days):

    days_back = date.today() - timedelta(days=days)
    
    df1 = pd.read_csv(f"data/ark_holdings_{days_back}.csv")
    df2 = pd.read_csv("data/ark_holdings_latest.csv")
    
    if fund == "ALL":
        df1 = df1.loc[df1["weight(%)"] > threshold].sort_values("weight(%)", ascending=False)
        df2 = df2.loc[df2["weight(%)"] > threshold].sort_values("weight(%)", ascending=False)
    
    else:
        df1 = df1.loc[df1["weight(%)"] > threshold].sort_values("weight(%)", ascending=False)
        df1 = df1.loc[df1["fund"] == fund]
        df2 = df2.loc[df2["weight(%)"] > threshold].sort_values("weight(%)", ascending=False)
        df2 = df2.loc[df2["fund"] == fund]
    
    fig = go.Figure()
        
    fig.add_trace(go.Bar(x=df1["company"], y=df1["weight(%)"], name=df1["date"].iloc[-1]))

    fig.add_trace(go.Bar(x=df2["company"], y=df2["weight(%)"], name=df2["date"].iloc[-1]))
    
    fig.update_layout(template="plotly_white", 
                      title=f"Holdings weight in ETF: {dict_ark_holdings[fund]}<Br>(threshold > {threshold}%)",
                      yaxis_title=f"weight (%)")

    return fig


# Holdings changes per fund
@app.callback(Output('graph-holdings-changes', 'figure'),
              [Input('changes-fund-dropdown', 'value'),
              Input('toplist-size-dropdown', 'value'),
              Input('holdings-changes-day-slider', 'value'),]
              )
def holdings_changes(fund, toplist_size, days):

    yesterday = date.today() - timedelta(days=1)
    compare_with_date = date.today() - timedelta(days=days)

    df_new = pd.read_csv(f"data/ark_holdings_{yesterday}.csv")
    df_old = pd.read_csv(f"data/ark_holdings_{compare_with_date}.csv")

    df_new.drop(["cusip", "market value($)"], axis=1, inplace=True)
    df_old.drop(["cusip", "market value($)"], axis=1, inplace=True)

    # merge
    df = df_old.merge(df_new, how="outer", left_on=["fund", "ticker", "company"], right_on=["fund", "ticker", "company"])

    # fill NaN with zeros
    df["shares_x"].fillna(0, inplace=True)
    df["shares_y"].fillna(0, inplace=True)

    # Figuring out what has changed ..
    df["shares_change"] = df["shares_y"] - df["shares_x"]
    df["shares_change(%)"] = df["shares_change"] / df["shares_x"] * 100

    if fund != "ALL":
        df = df.loc[df["fund"] == fund]

    # For toplist (each df its own trace)
    df_incr_shares = df.sort_values("shares_change(%)", ascending=False).iloc[:toplist_size].round(1)
    df_incr_shares = df_incr_shares.loc[df_incr_shares["shares_change(%)"] != np.inf]

    df_decr_shares = df.sort_values("shares_change(%)", ascending=True).iloc[:toplist_size].round(1)
    
    # find new holdings and set col "new holding" to '100'. (just to make it appear clearly)
    df.loc[df["shares_change(%)"] == np.inf, "new_holding"] = 100
    df_new_holdings  = df.loc[df["new_holding"] == 100]
    print("Shape of df_new_holdings: ", df_new_holdings.shape)
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=df_incr_shares["ticker"], y=df_incr_shares["shares_change(%)"], name="Increased shares")
                 , secondary_y=False)

    fig.add_trace(go.Bar(x=df_decr_shares["ticker"], y=df_decr_shares["shares_change(%)"], name="Decreased shares")
                 , secondary_y=False)
    
    fig.add_trace(go.Bar(x=df_new_holdings["ticker"], y=df_new_holdings["new_holding"], name="New holding (inf increase)")
                 , secondary_y=False)

    fig.update_layout(template="plotly_white", yaxis_title=f"Holdings change (%)",
                      title=f"Holdings changes for: {dict_ark_holdings[fund]}<Br>{df['date_x'].dropna().iloc[-1]}  vs.  {df['date_y'].dropna().iloc[-1]}",
                     )

    return fig

# Plot ticker
@app.callback(Output('ticker-graph', 'figure'),
    [Input('ticker-mode-dropdown', 'value'),
     Input('submit-val', 'n_clicks')],
    [State('ticker-input-on-submit', 'value')]
)
def update_timeline_graph(mode, n_clicks, ticker):

    TICKER_PERIOD = "2y"  # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    GOOGLE_TIME_PERIOD = "today 12-m"
    KWD_LIST = [ticker, "bitcoin", "stimulus check"]
    TA_TIMEFRAME = "week"

    df = my_ticker(ticker, TICKER_PERIOD)
    # add moving average
    df["ma50"] = df["Close"].rolling(window=50).mean()
    df["ma200"] = df["Close"].rolling(window=200).mean()
    
    df_btc = my_ticker("BTC-USD", TICKER_PERIOD)
    df_google = google_trend(KWD_LIST, GOOGLE_TIME_PERIOD)
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Ohlc(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                increasing_line_color= 'green', decreasing_line_color= 'orange', name=ticker)
                 , secondary_y=True)
    
    fig.add_trace(go.Scatter(x=df.index, y=df["ma200"], name=f"{ticker} ma200",
                             line = dict(width=1, color="pink")), secondary_y=True)
    fig.add_trace(go.Scatter(x=df.index, y=df["ma50"], name=f"{ticker} ma50",
                             line = dict(width=1, color="lightgreen")), secondary_y=True)
    
    if mode == "ticker_vs_btc":
        fig.add_trace(go.Scatter(x=df_btc.index, y=df_btc["Close"], name="Bitcoin",
                             line = dict(width=1, color="lightblue")), secondary_y=False)
        fig.update_yaxes(title_text="Price BTC (USD)", secondary_y=False, color="lightblue")
    
    elif mode == "ticker_vs_google_search":
        for i, kwd in enumerate(KWD_LIST):
            fig.add_trace(go.Scatter(x=df_google.index, y=df_google[KWD_LIST[i]], name=f"search {str(KWD_LIST[i])}",
                                 line = dict(width=1, dash='dot')), secondary_y=False)
        fig.update_yaxes(title_text="Google search index", secondary_y=False, color="grey")
    
    fig.update_yaxes(title_text=f"Price {ticker} (USD)", secondary_y=True)
    fig.update_xaxes(title_text="Date")
    #fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(template="plotly_white",
                      title=f"Ticker: {ticker}, Company: {get_company_name(ticker)} <br>TA {TA_TIMEFRAME}: {tradingview_rec(ticker, TA_TIMEFRAME)}")

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
