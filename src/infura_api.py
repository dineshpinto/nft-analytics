# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2021 Dinesh Pinto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import logging
import sys

import requests
from web3 import Web3
from web3.contract import Contract

from config import INFURA_PROJECT_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class InfuraAPI:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}'))
        if not self.w3.isConnected():
            raise Exception("Unable to connect to Web3 endpoint")
        else:
            logger.info("Connected to Infura endpoint.")

        self.abi_endpoint = 'https://api.etherscan.io/api?module=contract&action=getabi&address='

    def get_contract(self, contract_address: str) -> Contract:
        response = requests.get('%s%s' % (self.abi_endpoint, contract_address))
        abi_json = json.loads(response.json()['result'])
        return self.w3.eth.contract(self.w3.toChecksumAddress(contract_address), abi=abi_json)

    @staticmethod
    def get_contract_balance(contract: Contract, address: str) -> float:
        return contract.functions.balanceOf(Web3.toChecksumAddress(address)).call()

    def get_eth_balance(self, address: str) -> float:
        return self.w3.eth.get_balance(Web3.toChecksumAddress(address)) / 1e18

    def get_total_eth_weth_balance(self, weth_contract: Contract, address: str) -> float:
        return self.get_eth_balance(address) + self.get_contract_balance(weth_contract, address)
