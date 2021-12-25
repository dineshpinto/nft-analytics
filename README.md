# NFT Analytics
One of the hardest problems of non-fungible tokens (NFT) projects is data modeling.

Modeling covers areas like understanding hodler behaviour, sales volume trends, identifying whales, and valuing NFTs relative to each other within a specific collection. 

NFT Analytics is a Python framework to make that process easier. It contains code to interact with the most popular NFT marketplace on Ethereum. Ethereum was chosen as the base due to its dominant nature in the NFT space. This raw data is then modeled mathematically to distill usable information and visualize it.

## Installation
1. Create the conda environment from file
   + ```conda env create --file conda-env.yml```
2. Activate environment 
   + ```conda activate nft_analytics```
3. Add environment to Jupyter kernel 
    + ```python -m ipykernel install --name=nft_analytics```
4. Install jupyter lab extensions for plotly 
   + ```jupyter labextension install jupyterlab-plotly```
5. To use the Infura backend, rename `config-dummy.py`to `config.py`, and add in your private Infura API key
6. Explore the various Jupyterlab Notebooks under `notebooks/`

## APIs used
- OpenSea public API (`src/opensea_api.py`)
- Infura private API (`src/infura_api.py`)

## Disclaimer
This project is only for educational purposes, always do your own research before making any investment decisions.