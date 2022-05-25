# NFT Analytics
One of the hardest problems of non-fungible tokens (NFT) projects is data modeling.

Modeling covers areas like understanding hodler behaviour, sales volume trends, identifying whales, and valuing NFTs relative to each other within a specific collection. 

NFT Analytics is a Python framework to make that process easier. It contains code to interact with the most popular NFT marketplace on Ethereum. Ethereum was chosen as the base due to its dominant nature in the NFT space. This raw data is then modeled mathematically to distill usable information and visualize it.

## Installation
1. Create the conda environment from file
```shell
conda env create --file conda-env.yml
```
2. Activate environment 
```shell
conda activate nft_analytics
```
3. Add environment to Jupyter kernel 
```shell
python -m ipykernel install --name=nft_analytics
```
4. Install jupyter lab extensions for plotly 
```shell
jupyter labextension install jupyterlab-plotly
```
5. To use the Infura backend (required for querying blockchain data), rename `config-dummy.py`to `config.py`, and add in your private Infura API key
6. Explore the various Jupyterlab Notebooks under `notebooks/`

## APIs used
- OpenSea public API (`src/opensea_api.py`)
- Infura private API (`src/infura_api.py`)

### Export conda environment
```shell
conda env export --no-builds | grep -v "^prefix: " > conda-env.yml
```

## Disclaimer
This project is for educational purposes only. You should not construe any such information or other material as legal, tax, investment, financial, or other advice. Nothing contained here constitutes a solicitation, recommendation, endorsement, or offer by me or any third party service provider to buy or sell any securities or other financial instruments in this or in any other jurisdiction in which such solicitation or offer would be unlawful under the securities laws of such jurisdiction.

If you plan to use real money, use at your own risk.

Under no circumstances will I be held responsible or liable in any way for any claims, damages, losses, expenses, costs, or liabilities whatsoever, including, without limitation, any direct or indirect damages for loss of profits.
