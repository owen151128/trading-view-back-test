import json

from flask import Flask, request, session, redirect
from flask.templating import render_template

import os
import uuid
import pandas as pd

from backtest.backtest import Backtest
from trading_view.trading_view_csv_parser import TradingViewCsvParser

is_first = True
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
token_dict = {}


def load_account(path: str) -> dict:
    result = {}
    with open(path, 'r') as a:
        for s in a.readlines():
            user_id, user_pw = s.split(', ')
            result[user_id] = user_pw.rstrip('\n')

    return result


account_map = load_account('account.txt')


@app.route('/')
def root():
    # Debug only
    # if is_first:
    #     token = uuid.uuid4()
    #     session['token'] = token
    #     token_dict[token] = "test"
    token = session.get('token')
    if token is not None:
        identifier = token_dict.get(token)
        if identifier is not None:
            return render_template('index.html', user_id=identifier, user_token=token)
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/login/form')
def login():
    token = session.get('token')
    if token is not None:
        identifier = token_dict.get(token)
        if identifier is not None:
            return redirect('/')

    return render_template('login.html')


@app.route('/login/proc', methods=['GET', 'POST'])
def logic_proc():
    token = session.get('token')
    if token is not None:
        identifier = token_dict.get(token)
        if identifier is not None:
            return redirect('/')

    request_id = request.form['userId']
    request_pw = request.form['userPw']
    pw = account_map[request_id] if request_id in account_map else None
    if pw is not None:
        if request_pw == pw:
            token = uuid.uuid4()
            if token in token_dict:
                return render_template('alert.html', message='잠시후 다시 시도해 주세요.', redirect='/')
            session['token'] = token
            token_dict[token] = request_id

            return redirect('/')
        else:
            return render_template('alert.html', message='아이디 또는 비밀번호가 틀렸습니다.', redirect='/')
    else:
        return render_template('alert.html', message='아이디 또는 비밀번호가 틀렸습니다.', redirect='/')


@app.route('/login/logout')
def logout():
    session.clear()

    return redirect('/')


@app.route('/trading_view/backtest/request', methods=['POST'])
def request_backtest():
    token, balance, stop_loss, leverage, candle_size, csv_data = request.json['token'], int(request.json['balance']), \
                                                                 int(request.json['stopLoss']), \
                                                                 int(request.json['leverage']), \
                                                                 request.json['candleSize'], request.json['data']

    trade_data = TradingViewCsvParser.parse_trading_view_csv_from_encoded(csv_data)
    is_day = False
    is_1min = False
    if candle_size == '1m':
        binance_klines_data = pd.read_excel('binance_1m_candle_history.xlsx', sheet_name='Sheet1', index_col=0)
        is_1min = True
    elif candle_size == '1h' or candle_size == '2h' or candle_size == '4h' or candle_size == '6h' or \
            candle_size == '8h' or candle_size == '12h':
        binance_klines_data = pd.read_excel('binance_1h_candle_history.xlsx', sheet_name='Sheet1', index_col=0)
    else:
        is_day = True
        binance_klines_data = pd.read_excel('binance_1h_candle_history.xlsx', sheet_name='Sheet1', index_col=0)

    backtest = Backtest(balance, trade_data, binance_klines_data)

    return backtest.calculate_balance(is_day, stop_loss, is_1min, leverage)


if __name__ == '__main__':
    app.run()
