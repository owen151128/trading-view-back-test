# -*- coding: utf-8 -*-

import pandas as pd

from binance.client import Client
from datetime import datetime, timedelta, timezone
from pandas import DataFrame

from exchange.binance_api_key_manager import BinanceApiKeyManager


class BinanceHistoryKlinesManager:
    data_subject = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                    'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    time_format: str = '%Y-%m-%d %H:%M'
    utc_time_format: str = '%Y-%m-%dT%H:%M'
    key_manager: BinanceApiKeyManager = None
    interval: str = ''
    start_date: datetime = None
    end_date: datetime = None
    candle_count: int = 0
    limit: int = 0
    request_count: int = 0
    df: DataFrame = DataFrame()

    def __init__(self, start_date, end_date, interval, key_manager: BinanceApiKeyManager):
        self.interval = interval
        self.start_date = datetime.strptime(start_date, self.time_format)
        self.end_date = datetime.strptime(end_date, self.time_format)
        subtract_time = self.end_date - self.start_date
        self.candle_count = int(subtract_time.days * 24 + subtract_time.seconds / 3600)

        # max weight(2400) : limit(candle : 1500, weight : 10) -> max weight(2400) / weight(10) = 240
        # 1500 * 240 = 360000 -> 1m limit : 360000
        self.limit = 1500
        self.request_count = 1 if self.candle_count <= 1500 else int(self.candle_count / 1500 + 1)
        self.key_manager = key_manager

    def get_klines(self, excel_path: str, is_real_download: bool):
        current_start_date = self.start_date.astimezone(timezone.utc)
        current_end_date = current_start_date + timedelta(
            hours=self.candle_count if self.candle_count <= 1501 else 1501
        )
        downloaded_candle_count = 0
        binance_client = Client(api_key=self.key_manager.api_key, api_secret=self.key_manager.api_secret_key)

        for i in range(1, self.request_count + 1):
            # 18 00 ~ 20 00 / 21 00 ~ 23 00
            print(f'[*] Get klines ('
                  f'{current_start_date.astimezone().strftime(self.time_format)} ~ '
                  f'{current_end_date.astimezone().strftime(self.time_format)}) [{i}/{self.request_count}]')
            if is_real_download:
                history_klines = binance_client. \
                    futures_historical_klines('BTCUSDT', self.interval,
                                              current_start_date.strftime(self.utc_time_format),
                                              current_end_date.strftime(self.utc_time_format))

                current_df = DataFrame(history_klines, columns=self.data_subject)
                current_df['time'] = current_df['time'].apply(
                    lambda x: datetime.fromtimestamp(x / 1000).strftime(self.time_format))
                current_df = current_df.set_index('time')
                self.df = pd.concat([self.df, current_df])

            downloaded_candle_count += 1500
            current_start_date = current_end_date + timedelta(hours=1)
            current_end_date = current_start_date + timedelta(
                hours=self.candle_count - downloaded_candle_count - i
                if self.candle_count - downloaded_candle_count - i < 1501 else 1501)
            print(f'downloaded candle count : {downloaded_candle_count}')

        if is_real_download:
            print('[*] Write Excel...')
            self.df.to_excel(excel_path)
