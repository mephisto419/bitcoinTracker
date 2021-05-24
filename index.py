import os
import numpy as np
import pandas as pd
import pickle
import quandl
import chart_studio

import plotly.offline as py
import plotly.graph_objs as go

py.init_notebook_mode(connected=True)

quandl.ApiConfig.api_key = "api here"


def get_quandl_data(quandl_code):
    cache_path = '{}.pkl'.format(quandl_code).replace('/', '-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(quandl_code))
    except (OSError, IOError) as e:
        df = quandl.get(quandl_code, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}').format(quandl_code, cache_path)
    return df


btc = get_quandl_data('BCHARTS/KRAKENUSD')
btc.head()

btc_trace = go.Scatter(x=btc.index, y=btc['Weighted Price'])
py.iplot([btc_trace])

exchanges = ['COINBASE', 'BITSTAMP', 'ITBIT']
exchange_data = {}
exchange_data['KRAKEN'] = btc

for exchange in exchanges:
    exchange_code = 'BCHARTS/{}USD'.format(exchange)
    btc_exchange_df = get_quandl_data(exchange_code)
    exchange_data[exchange] = btc_exchange_df


def merge_df(dataframes, labels, col):
    series_dict = {}

    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]
    return pd.DataFrame(series_dict)


btc_usd_df = merge_df(list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price')
btc_usd_df.tail()

layout = go.Layout(
    title='Bitcoin Price Tracker (USD)',
    legend={'orientation': 'h'},
    xaxis={'type': 'date'},
    yaxis={'title': 'Value'}
)

trace_arr = []
labels = list(btc_usd_df)
for index, label in enumerate(labels):
    series = btc_usd_df[label]

    trace = go.Scatter(x=series.index, y=series, name=label)
    trace_arr.append(trace)

fig = go.Figure(data=trace_arr, layout=layout)
py.iplot(fig)

btc_usd_df['avg'] = btc_usd_df.mean(axis=1)
btc_trace = go.Scatter(x=btc_usd_df.index, y=btc_usd_df['avg'])
fig = go.Figure(data=[btc_trace], layout=layout)
py.iplot(fig)

chart_studio.tools.set_credentials_file(username='here', api_key='api-here')
chart_studio.plotly.plot(fig, filename='Bitcoin USD price', auto_open=True)
