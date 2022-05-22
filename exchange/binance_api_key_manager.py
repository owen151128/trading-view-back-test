# -*- coding: utf-8 -*-

from yaml import load, CLoader


class BinanceApiKeyManager:
    api_key: str = ''
    api_secret_key: str = ''

    def __init__(self, binance_key_yaml_path: str):
        with open(binance_key_yaml_path) as s:
            binance_keys = load(s, CLoader)
            self._api_key = binance_keys['api_key']
            self.api_secret_key = binance_keys['api_secret_key']
