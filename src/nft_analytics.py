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
import os
import sys
from json import JSONDecodeError

import numpy as np
import pandas as pd
from tqdm import tqdm

from .infura_api import InfuraAPI
from .opensea_api import OpenSeaAPI

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class NFTAnalytics(OpenSeaAPI):
    def __init__(self, asset_contract_address: str):
        super().__init__(asset_contract_address)
        self.eth_api = InfuraAPI()

    @staticmethod
    def make_directories(folder_name: str):
        """ Set up directories for data and results if they don't exist. """
        data_folder = os.path.join("data", folder_name)
        result_folder = os.path.join("results", folder_name)

        if not os.path.isdir(data_folder):
            logger.info(f"Making directoy {data_folder}")
            os.makedirs(data_folder)

        if not os.path.isdir(result_folder):
            logger.info(f"Making directoy {result_folder}")
            os.makedirs(result_folder)

        return data_folder, result_folder

    def fetch_data(self, max_offset: int = 10000, collection: str = None) -> list:
        """
        Query OpenSea API for collection data, offset is shifted until max
        offset is reached (i.e. number of items in a collection).
        """
        local_assets = []

        pbar = tqdm(range(0, max_offset + 1, 50))
        for offset in pbar:
            pbar.set_description(f"{offset}")
            try:
                asset_data = self.get_asset_data(offset=offset, limit=50, collection=collection)
            except JSONDecodeError:
                logger.error(f"Only fetched data till offset={offset - 1}. "
                             f"Warning={self.get_asset_data(offset=offset, limit=50)}")
                return local_assets

            if "assets" not in asset_data:
                logger.error(f"Only fetched data till offset={offset - 1}. Warning={asset_data}")
                return local_assets

            for asset in asset_data["assets"]:
                local_assets.append(asset)

        return local_assets

    def fetch_events(self, max_offset: int = 10000) -> list:
        """
        Query OpenSea API for event data, offset is shifted until max
        offset is reached (i.e. number of items in a collection).
        """
        local_events = []

        pbar = tqdm(range(0, max_offset + 1, 300))
        for offset in pbar:
            pbar.set_description(f"{offset}")
            try:
                event_data = self.get_event_data(offset=offset, limit=300)
            except JSONDecodeError:
                logger.error(f"Only fetched data till offset={offset - 1}. "
                             f"Warning={self.get_asset_data(offset=offset, limit=50)}")
                return local_events

            if "asset_events" not in event_data:
                logger.error(f"Only fetched data till offset={offset - 1}. Warning={event_data}")
                return local_events

            for event in event_data["asset_events"]:
                local_events.append(event)

        return local_events

    @staticmethod
    def save_json(asset_data: list, filename: str = "data.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asset_data, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved asset data to {filename}")

    @staticmethod
    def load_json(filename: str = "data.json") -> list:
        with open(filename) as f:
            asset_data = json.load(f)

        return asset_data

    @staticmethod
    def get_trait_values_for_type(asset_data: list, trait_type: str) -> list:
        """ Get all possible values of traits for a specific type of trait. """
        trait_values = []
        for asset in asset_data:
            for traits in asset["traits"]:
                if traits["trait_type"] == trait_type and traits["value"] not in trait_values:
                    trait_values.append(traits["value"])

        return trait_values

    def get_trait_type_median_price(self, asset_data: list, trait_type: str) -> dict:
        """ Get the median price of a specific trait type. """
        trait_value_prices = {}
        for value in self.get_trait_values_for_type(asset_data, trait_type):
            listing_prices_trait = []

            for asset in asset_data:
                if asset["sell_orders"]:
                    for traits in asset["traits"]:
                        if traits["trait_type"] == trait_type and traits["value"] == value:
                            listing_prices_trait.append(float(asset["sell_orders"][0]["base_price"]) / 1e18)

            trait_value_prices[value] = np.median(np.array(listing_prices_trait))

        return dict(sorted(trait_value_prices.items(), key=lambda item: item[1], reverse=True))

    def get_median_prices(self, asset_data: list, traits_dict: dict) -> np.ndarray:
        """ Get median prices of all trait types. """
        median_prices = []
        for trait_type, trait_value in traits_dict.items():
            median_prices.append(self.get_trait_type_median_price(asset_data, trait_type)[trait_value])

        return np.array(median_prices)

    def get_traits_with_median_prices(self, asset_data: list, asset: dict) -> dict:
        """ Get median prices of trait types for specific asset. """
        traits = {}
        for trait in asset["traits"]:
            traits[trait["trait_type"]] = trait["value"]

        trait_prices = {}

        for trait_type, trait_value in traits.items():
            price = self.get_trait_type_median_price(asset_data, trait_type)[trait_value]
            trait_prices[trait_value + " " + trait_type] = price

        return trait_prices

    def get_nft_holdings(self, asset_data: list, asset_name: str, eth_balances: bool = True) \
            -> pd.DataFrame:
        """ Query the number of NFTs held and/or the ETH balances of addresses in a collection.  """
        nfts_held = {}

        for asset in asset_data:
            nfts_held[asset["owner"]["address"]] = 0

        for asset in asset_data:
            nfts_held[asset["owner"]["address"]] += 1

        logger.info(f"Total NFTs in collection = {sum(nfts_held.values())}")

        if eth_balances:
            logger.info(f"Getting NFT holdings and ETH balances...")
            df = pd.DataFrame(columns=["Address", asset_name, "ETH_balance"])

            pbar = tqdm(nfts_held.items())

            for idx, (address, num_nfts) in enumerate(pbar):
                pbar.set_description(f"{idx}")
                df.loc[idx] = [address, num_nfts, self.eth_api.get_eth_balance(address)]
        else:
            logger.info(f"Getting NFT holdings...")
            df = pd.DataFrame(columns=["Address", asset_name])

            pbar = tqdm(nfts_held.items())

            for idx, (address, num_nfts) in enumerate(pbar):
                pbar.set_description(f"{idx}")
                df.loc[idx] = [address, num_nfts]

        etherscan_links = []
        for address in df["Address"]:
            etherscan_links.append(f"https://etherscan.io/address/{address}")
        df["Etherscan_link"] = etherscan_links

        opensea_links = []
        for address in df["Address"]:
            opensea_links.append(f"https://opensea.io/{address}")
        df["OpenSea_link"] = opensea_links

        return df

    @staticmethod
    def calculate_rarity_df(asset_data: list, items_in_collection: int) -> pd.DataFrame:
        """
        Calculate rarity of a particular trait.

        Uses the formula from rarity tools, full article at:
            raritytools.medium.com/ranking-rarity-understanding-rarity-calculation-methods-86ceaeb9b98c

        Formula:
        [Rarity Score for a Trait Value] =
            1 / ([Number of Items with that Trait Value] / [Total Number of Items in Collection])

        The total Rarity Score for an NFT is the sum of the Rarity Score of all of its trait values.
        """
        df = pd.DataFrame(columns=["Name", "Price", "Rarity", "RarityPriceRatio"])

        for idx, asset in enumerate(asset_data):
            if asset["sell_orders"]:
                if asset["sell_orders"][0]["payment_token_contract"]["symbol"] == "ETH":
                    price = float(asset["sell_orders"][0]["current_price"]) / 1e18
                    if price != 0:
                        rarity = 0
                        for trait in asset["traits"]:
                            trait_count = int(trait["trait_count"])
                            if trait_count != 0:
                                rarity += 1 / (trait_count / items_in_collection)
                        name = asset["name"]
                        df.loc[idx] = [name, price, rarity, rarity / price]

        return df
