# -*- coding: utf-8 -*-

from pandas import DataFrame
from datetime import datetime, timedelta

from exchange.binance_history_klines_manager import BinanceHistoryKlinesManager

import json


class Backtest:
    is_first = True
    fee = 0.0004
    balance = 0
    trade_data: list = None
    binance_klines_data: DataFrame = None

    def __init__(self, balance: int, trade_data: list, binance_klines_data: DataFrame):
        self.balance = balance
        self.trade_data = trade_data
        self.binance_klines_data = binance_klines_data

    def calculate_balance(self, is_day: bool, stop_loss: int, is_1min: bool, leverage_rate: int = 1) -> str:
        result = {}
        total_trade_count = len(self.trade_data)
        total_fee = 0
        total_win_pnl = 0
        total_loss_pnl = 0
        win_count = 0
        loss_count = 0
        before_position = ''
        before_date = ''
        for i, (position, date) in enumerate(self.trade_data):
            if self.is_first:
                before_position = position
                before_date = date
                self.is_first = False
                continue

            try:
                if is_day:
                    opened_price = int(self.binance_klines_data.loc[f'{before_date} 09:00']["open"] + 100) \
                        if before_position == 'Long' else int(
                        self.binance_klines_data.loc[f'{before_date} 09:00']["open"] - 100
                    )
                    closed_price = int(self.binance_klines_data.loc[f'{date} 09:00']["open"] - 100) \
                        if before_position == 'Long' else int(
                        self.binance_klines_data.loc[f'{date} 09:00']["open"] + 100
                    )
                    # opened_price = int(self.binance_klines_data.loc[f'{before_date} 00:00']['open'])
                    # closed_price = int(self.binance_klines_data.loc[f'{date} 00:00']['open'])
                    elapsed_times = (datetime.strptime(f'{date} 09:00', BinanceHistoryKlinesManager.time_format) -
                                     datetime.strptime(f'{before_date} 09:00', BinanceHistoryKlinesManager.time_format))
                    elapsed_times = elapsed_times.seconds / 360 + elapsed_times.days * 24
                    before_datetime = datetime.strptime(f'{before_date} 09:00', BinanceHistoryKlinesManager.time_format)
                else:
                    opened_price = int(self.binance_klines_data.loc[before_date]["open"] - 100) \
                        if before_position == 'Long' else int(self.binance_klines_data.loc[before_date]["open"] + 100)
                    closed_price = int(self.binance_klines_data.loc[date]["open"] - 100) \
                        if before_position == 'Long' else int(self.binance_klines_data.loc[date]["open"] + 100)
                    # opened_price = int(self.binance_klines_data.loc[before_date]['open'])
                    # closed_price = int(self.binance_klines_data.loc[date]['open'])
                    elapsed_times = (datetime.strptime(date, BinanceHistoryKlinesManager.time_format) -
                                     datetime.strptime(before_date, BinanceHistoryKlinesManager.time_format))
                    if is_1min:
                        elapsed_times = elapsed_times.seconds / 60 + elapsed_times.days * 24 * 60
                    else:
                        elapsed_times = elapsed_times.seconds / 360 + elapsed_times.days * 24
                    before_datetime = datetime.strptime(before_date, BinanceHistoryKlinesManager.time_format)
            except:
                break

            roe = round(closed_price / opened_price * 100 - 100, 3)
            roe *= -1 if before_position == 'Short' else 1
            if leverage_rate > 1:
                leverage_roe = round(roe * leverage_rate, 3)
            else:
                leverage_roe = roe
            profit_and_loss = round(self.balance * leverage_roe * 0.01, 3)

            # liquidation & stop loss
            liquidation_percent = 100 / leverage_rate
            liquidation_price = opened_price * (1 - liquidation_percent / 100) if before_position == 'Long' \
                else opened_price * (1 + liquidation_percent / 100)
            stop_loss_price = opened_price * (1 - stop_loss / self.balance / leverage_rate) \
                if before_position == 'Long' else opened_price * (1 + stop_loss / self.balance / leverage_rate)
            for e in range(int(elapsed_times)):
                if is_1min:
                    current_candle_time = (before_datetime + timedelta(minutes=e)) \
                        .strftime(BinanceHistoryKlinesManager.time_format)
                else:
                    current_candle_time = (before_datetime + timedelta(hours=e)) \
                        .strftime(BinanceHistoryKlinesManager.time_format)
                try:
                    candle = self.binance_klines_data.loc[current_candle_time]
                except:
                    break
                high, low = candle["high"], candle["low"]
                if before_position == 'Long' and liquidation_price >= low:
                    result['Liquidation(Long)'] = current_candle_time
                    result['Liquidation price'] = liquidation_price
                    result['Liquidation low'] = low
                    result['Liquidation tissue'] = f'${self.balance}'
                    result['Liquidation result'] = 'GG'
                    return json.dumps(result)

                if before_position == 'Short' and liquidation_price <= high:
                    result['Liquidation(Short)'] = current_candle_time
                    result['Liquidation price'] = liquidation_price
                    result['Liquidation high'] = high
                    result['Liquidation tissue'] = f'${self.balance}'
                    result['Liquidation result'] = 'GG'

                    return json.dumps(result)

                if before_position == 'Long' and stop_loss_price >= low:
                    roe = round(stop_loss_price / opened_price * 100 - 100, 3)
                    roe *= -1 if before_position == 'Short' else 1
                    if leverage_rate > 1:
                        leverage_roe = round(roe * leverage_rate, 3)
                    else:
                        leverage_roe = roe
                    profit_and_loss = round(self.balance * leverage_roe * 0.01, 3)

                if before_position == 'Short' and stop_loss_price <= high:
                    roe = round(stop_loss_price / opened_price * 100 - 100, 3)
                    roe *= -1 if before_position == 'Short' else 1
                    if leverage_rate > 1:
                        leverage_roe = round(roe * leverage_rate, 3)
                    else:
                        leverage_roe = roe
                    profit_and_loss = round(self.balance * leverage_roe * 0.01, 3)

            if profit_and_loss > 0:
                win_count += 1
                total_win_pnl += round(profit_and_loss, 3)
            else:
                loss_count += 1
                total_loss_pnl += round(abs(profit_and_loss), 3)
            before_balance = self.balance
            self.balance += profit_and_loss
            total_fee += before_balance * self.fee + self.balance * self.fee
            self.balance -= before_balance * self.fee + self.balance * self.fee
            self.balance = round(self.balance, 3)

            result[f'{i}'] = f'{date} position : {before_position}, Size : ${before_balance}, ROE : {roe}%, ' \
                             f'Leverage_roe : {leverage_roe}%, PNL : ${profit_and_loss}, balance : ${self.balance}'
            before_position = position
            before_date = date

        winning_percentage = win_count / total_trade_count * 100
        result['Winning Percentage'] = f'{round(winning_percentage, 2)}%'
        result['Total trade count'] = total_trade_count
        result['Total Win count'] = win_count
        result['Total Loss count'] = loss_count
        result['Total Win pnl'] = total_win_pnl
        result['Total Loss pnl'] = total_loss_pnl
        result['Total fee'] = f'${round(total_fee, 3)}'

        if self.balance <= 0:
            print('[*] Bankruptcy!!!')
            result['Critical'] = 'Bankruptcy!!!'

            return json.dumps(result)

        return json.dumps(result)
