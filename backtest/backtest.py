# -*- coding: utf-8 -*-

from pandas import DataFrame


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

    def calculate_balance(self, is_day: bool):
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
                    opened_price = int(self.binance_klines_data.loc[f'{before_date} 00:00']["open"] - 100) \
                        if before_position == 'Long' else int(
                        self.binance_klines_data.loc[f'{before_date} 00:00']["open"] + 100
                    )
                    closed_price = int(self.binance_klines_data.loc[f'{date} 00:00']["open"] - 100) \
                        if before_position == 'Long' else int(
                        self.binance_klines_data.loc[f'{date} 00:00']["open"] + 100
                    )
                    # opened_price = int(self.binance_klines_data.loc[f'{before_date} 00:00']['open'])
                    # closed_price = int(self.binance_klines_data.loc[f'{date} 00:00']['open'])
                else:
                    opened_price = int(self.binance_klines_data.loc[before_date]["open"] - 100) \
                        if before_position == 'Long' else int(self.binance_klines_data.loc[before_date]["open"] + 100)
                    closed_price = int(self.binance_klines_data.loc[date]["open"] - 100) \
                        if before_position == 'Long' else int(self.binance_klines_data.loc[date]["open"] + 100)
                    # opened_price = int(self.binance_klines_data.loc[before_date]['open'])
                    # closed_price = int(self.binance_klines_data.loc[date]['open'])
            except:
                break
            roe = round(closed_price / opened_price * 100 - 100, 3)
            roe *= -1 if before_position == 'Short' else 1
            profit_and_loss = round(self.balance * roe * 0.01, 3)

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

            if self.balance <= 0:
                print('[*] Bankruptcy!!!')
                break

            print(f'[*] #{i} / {date} position : {before_position}, Size : ${before_balance}, ROE : {roe}%, '
                  f'PNL : ${profit_and_loss}, balance : ${self.balance}')
            before_position = position
            before_date = date

        winning_percentage = win_count / total_trade_count * 100
        print(f'[*] Winning Percentage : {round(winning_percentage, 2)}%, Total trade count : {total_trade_count}, '
              f'Total Win count : {win_count}, Total Loss count : {loss_count}, '
              f'Total Win pnl : ${total_win_pnl}, '
              f'Total Loss pnl : ${total_loss_pnl}, Total fee : ${round(total_fee, 3)}')
