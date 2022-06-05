# -*- coding: utf-8 -*-

from base64 import b64decode
from io import StringIO

import csv


class TradingViewCsvParser:
    @staticmethod
    def parse_trading_view_csv(csv_path: str) -> list:
        trade_data = []
        last_data = None
        with open(csv_path, 'r', encoding='utf-8') as r:
            trading_view_csv = csv.reader(r)
            for i, v in enumerate(trading_view_csv):
                if i % 2 == 1:
                    trade_data.append((v[2], v[3]))
                last_data = (v[2], v[3])

        trade_data.append(last_data)
        trade_data.reverse()

        return trade_data

    @staticmethod
    def parse_trading_view_csv_from_encoded(encoded: str) -> list:
        decoded = StringIO(b64decode(encoded).decode(encoding='utf-8'))
        trade_data = []
        last_data = None
        trading_view_csv = csv.reader(decoded)
        for i, v in enumerate(trading_view_csv):
            if i % 2 == 1:
                trade_data.append((v[2], v[3]))
            last_data = (v[2], v[3])

        trade_data.append(last_data)
        trade_data.reverse()

        return trade_data
