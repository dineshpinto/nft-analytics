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
from pycoingecko import CoinGeckoAPI

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenSeaAPI:
    def __init__(self, asset_contract_address: str):
        self.asset_limit = 10
        self.asset_contract_address = asset_contract_address
        self.cg = CoinGeckoAPI()
        self.base_url = "https://api.opensea.io/api/v1/"

    def get_eth_usd_price(self) -> float:
        coin_id = "ethereum"
        vs_currency = "usd"
        return float(self.cg.get_price(ids=coin_id, vs_currencies=vs_currency)[coin_id][vs_currency])

    def request_last_sales(self) -> list:
        return self.parse_successful_event_data(self.get_successful_event_data())

    def get_floor_price(self, asset_data: list) -> float:
        url = self.base_url + "collections"

        floor_price = 0
        addr_id = 0

        while floor_price == 0:
            querystring = {
                "asset_owner": asset_data[addr_id]["owner"]["address"],
            }
            response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)
            json_response = json.loads(response.text)

            for item in json_response:
                if item["primary_asset_contracts"]:
                    if item["primary_asset_contracts"][0]["address"].lower() == self.asset_contract_address.lower():
                        floor_price = float(item["stats"]["floor_price"])
            addr_id += 10
        logger.info(f"floor price is {floor_price} ETH")
        return floor_price

    def get_successful_event_data(self, offset: int = 0, limit: int = 10) -> dict:
        url = self.base_url + "events"
        querystring = {
            "only_opensea": "true",
            "offset": str(offset),
            "limit": str(limit),
            "asset_contract_address": self.asset_contract_address,
            "event_type": "successful"
        }
        response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)

        return json.loads(response.text)

    def get_asset_data(self, offset: int = 0, limit: int = 50, collection: str = None) -> dict:
        url = self.base_url + "assets"

        querystring = {
            "offset": str(offset),
            "limit": str(limit),
            "asset_contract_address": self.asset_contract_address,
        }

        if collection:
            querystring["collection"] = collection

        response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)

        return json.loads(response.text)

    def get_event_data(self, offset: int = 0, limit: int = 50) -> dict:
        url = self.base_url + "events"

        querystring = {
            "only_opensea": "true",
            "offset": str(offset),
            "limit": str(limit),
            "asset_contract_address": self.asset_contract_address,
        }
        response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)

        return json.loads(response.text)

    def get_collections_data(self, address: str) -> dict:
        url = self.base_url + "collections"

        querystring = {
            "asset_owner": address,
            "offset": "0",
            "limit": "300"
        }
        response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)

        return json.loads(response.text)

    def get_account_data(self) -> dict:
        url = self.base_url + "accounts"

        querystring = {
            "offset": "0",
            "limit": "300"
        }
        response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)

        return json.loads(response.text)

    def parse_successful_event_data(self, json_dump: dict) -> list:
        json_list = []
        # Loop through the last sales
        for i in range(self.asset_limit):
            # json only contains the last sale info
            asset_info = json_dump['asset_events'][i]['asset']

            if not asset_info:
                continue

            image_url = asset_info['image_url']
            great_ape_number = asset_info['name']
            product_link = asset_info['permalink']

            # Seller info
            seller_info = json_dump['asset_events'][i]['seller']
            if not seller_info['user']:
                seller_username = None
            else:
                seller_username = seller_info['user']['username']
            seller_address = seller_info['address']

            # Buyer info
            buyer_info = json_dump['asset_events'][i]['winner_account']
            if not buyer_info['user']:
                buyer_username = None
            else:
                buyer_username = buyer_info['user']['username']
            buyer_address = buyer_info['address']

            payment_info = json_dump['asset_events'][i]['payment_token']
            payment_token = payment_info['symbol']

            sale_id = json_dump['asset_events'][i]['id']
            if payment_token in ["ETH", "WETH"]:
                sale_price = int(json_dump['asset_events'][i]['total_price']) / 1e18
                sale_price_usd = self.get_eth_usd_price() * sale_price
            else:
                sale_price = float(json_dump['asset_events'][i]['total_price'])
                sale_price_usd = None

            json_info = {
                'asset_info': {
                    'asset_name': great_ape_number,
                    'asset_image': image_url,
                    'asset_link': product_link,
                },
                'seller_info': {
                    'seller_username': seller_username,
                    'seller_address': seller_address
                },
                'buyer_info': {
                    'buyer_username': buyer_username,
                    'buyer_address': buyer_address
                },
                'payment_token': payment_token,
                'sale_price': sale_price,
                'sale_price_usd': sale_price_usd,
                'sale_id': sale_id
            }
            json_list.append(json_info)
        return json_list

    def get_sales_ids(self, sales_list: list) -> list:
        sales_ids = []

        for i in range(self.asset_limit):
            sales_ids.append(sales_list[i]['sale_id'])
        return sales_ids


if __name__ == "__main__":
    os_api = OpenSeaAPI(asset_contract_address="0xA0F38233688bB578c0a88102A95b846c18bc0bA7")
    os_api.request_last_sales()