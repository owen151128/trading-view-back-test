# -*- coding: utf-8 -*-

import argparse
import datetime
import math

import pandas as pd

from exchange.binance_api_key_manager import BinanceApiKeyManager
from exchange.binance_history_klines_manager import BinanceHistoryKlinesManager
from trading_view.trading_view_csv_parser import TradingViewCsvParser
from backtest.backtest import Backtest

from binance.client import Client
from time import sleep
from pyfiglet import Figlet


class Constants:
    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise ValueError('Constants can\'t be re-assigned!')
        self.__dict__[key] = value

    def __delattr__(self, item):
        if item in self.__dict__:
            raise ValueError('Constants can\' be removed!')


constants: Constants = Constants()


class EntryDescription:
    def __init__(self, application_name, version_name, example_message):
        self.application_name = application_name
        self.version_name = f' {application_name} {version_name} '
        self.example_message = f'example : python {__file__} {example_message}'

    def print_entry_description(self):
        result = Figlet(font='slant')
        print(result.renderText(self.application_name))
        print(f'{"=" * 80}\n{self.version_name:=^80}\n{"=" * 80}\n')
        sleep(0.01)


def main():
    global constants
    constants.APP = 'Trading View BackTest'
    constants.VERSION = 'vtest'
    constants.KEY_OPTION = '-k'
    constants.INPUT_OPTION = '-i'
    constants.BINANCE_OPTION = '-b'
    constants.DOWNLOAD_OPTION = '--d'
    constants.KEY_OPTION_META = 'binance_api_keys yaml file path'
    constants.INPUT_OPTION_META = 'Trading view transaction history csv file path'
    constants.BINANCE_OPTION_META = 'Binance candle history xlsx file path'
    constants.DOWNLOAD_OPTION_META = 'Try *Download* candle history from binance api'
    constants.UNDER_BAR = '_'
    constants.BLANK = ' '

    entry_description = EntryDescription(constants.APP, constants.VERSION,
                                         f'{constants.KEY_OPTION} [{constants.KEY_OPTION_META}] '
                                         f'{constants.INPUT_OPTION} [{constants.INPUT_OPTION_META}]')
    entry_description.print_entry_description()

    arg_parser = argparse.ArgumentParser(description=entry_description.version_name,
                                         epilog=entry_description.example_message)
    arg_parser.add_argument(constants.KEY_OPTION, metavar=f'[{constants.KEY_OPTION_META}]', required=True,
                            help=constants.KEY_OPTION_META.replace(constants.UNDER_BAR, constants.BLANK))
    arg_parser.add_argument(constants.INPUT_OPTION, metavar=f'[{constants.INPUT_OPTION_META}]', required=True,
                            help=constants.INPUT_OPTION_META.replace(constants.UNDER_BAR, constants.BLANK))
    arg_parser.add_argument(constants.BINANCE_OPTION, metavar=f'[{constants.BINANCE_OPTION_META}]', required=True,
                            help=constants.BINANCE_OPTION_META.replace(constants.UNDER_BAR, constants.BLANK))
    arg_parser.add_argument(constants.DOWNLOAD_OPTION, action='store_true',
                            help=constants.DOWNLOAD_OPTION_META.replace(constants.UNDER_BAR, constants.BLANK))
    args = arg_parser.parse_args()

    api_key_manager = BinanceApiKeyManager(args.k)

    binance_history_klines_manager = BinanceHistoryKlinesManager('2022-05-16 09:00', datetime.datetime.now().strftime(
        BinanceHistoryKlinesManager.time_format), Client.KLINE_INTERVAL_1MINUTE, api_key_manager)
    binance_history_klines_manager.get_klines(args.b, args.d)

    balance = 10000
    trade_data = TradingViewCsvParser.parse_trading_view_csv(args.i)
    binance_klines_data = pd.read_excel(args.b, sheet_name='Sheet1', index_col=0)
    backtest = Backtest(balance, trade_data, binance_klines_data)
    backtest.calculate_balance(False, 1)


def one_minutes_validation():
    is_first = True
    df = pd.read_excel('binance_1m_candle_history.xlsx', sheet_name='Sheet1', index_col=0)
    current_time: datetime.datetime = datetime.datetime.now()
    for i, r in df.iterrows():
        if is_first:
            current_time = datetime.datetime.strptime(str(i), '%Y-%m-%d %H:%M')
            is_first = False
        else:
            current_time += datetime.timedelta(minutes=1)
        if datetime.datetime.strptime(str(i), '%Y-%m-%d %H:%M') != current_time:
            print(f'[*] Illegal expected : {i}, actual : {current_time}')
            break
        else:
            print(f'[*] Passed : {i}')


if __name__ == '__main__':
    main()
