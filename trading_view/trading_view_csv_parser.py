# -*- coding: utf-8 -*-

import csv


class TradingViewCsvParser:
    @staticmethod
    def parse_trading_view_csv(csv_path: str) -> list:
        trade_data = []
        with open(csv_path, 'r', encoding='utf-8') as r:
            trading_view_csv = csv.reader(r)
            for i, v in enumerate(trading_view_csv):
                if i % 2 == 1:
                    trade_data.append((v[2], v[3]))

        trade_data.reverse()
        return trade_data
