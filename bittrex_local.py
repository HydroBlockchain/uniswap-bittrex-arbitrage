import pandas as pd
from bittrex.bittrex import Bittrex, API_V1_1, BOTH_ORDERBOOK
import os

BITTREX = Bittrex(os.getenv("BITTREX_API_KEY"), os.getenv("BITTREX_API_SECRET"), api_version=API_V1_1)


def get_orderbook_bittrex():
    """Get BTC-HYDRO orderbook."""
    orderbook = BITTREX.get_orderbook('BTC-HYDRO', BOTH_ORDERBOOK)
    assert orderbook["success"]

    buy = (
        pd.DataFrame.from_dict(orderbook["result"]["buy"])
        .assign(order_type="sell_hydro")
    )
    sell = (
        pd.DataFrame.from_dict(orderbook["result"]["sell"])
        .assign(order_type="buy_hydro")
    )

    return pd.concat([buy, sell])


def get_HYDRO_supply(orderbook, order_type):
    """Get total available HYDRO supply."""
    return orderbook.loc[lambda x: x["order_type"] == order_type]["Quantity"].sum()


def market_order_bittrex(orderbook, hydro_volume, order_type):
    """Get the cost/revenue and new price for a market buy/sell, in BTC."""
    assert get_HYDRO_supply(orderbook, order_type) >= hydro_volume

    subset = (
        orderbook
        .loc[lambda x: x["order_type"] == order_type]
        .sort_values("Rate", ascending=False if type == "sell_hydro" else True)
        .assign(cumulative_quantity=lambda x: x["Quantity"].cumsum())
        .loc[lambda x: (x["cumulative_quantity"] < hydro_volume).shift(1).fillna(True)]
        .assign(percentage_filled=1)
        .assign(percentage_filled=lambda x: x["percentage_filled"].where(x["cumulative_quantity"] < hydro_volume, (x["Quantity"] - (x["cumulative_quantity"] - hydro_volume)) / x["Quantity"]))
        .assign(traded_quantity=lambda x: x["Quantity"] * x["percentage_filled"])
        .assign(price_to_trade_all=lambda x: x["traded_quantity"] * x["Rate"])
    )
    btc_total = subset["price_to_trade_all"].sum()
    new_price = subset["Rate"].iloc[-1]

    return [btc_total, new_price]


def get_USD_BTC_price_bittrex():
    """Get USD price of BTC."""
    price = BITTREX.get_ticker("USD-BTC")
    assert price["success"]
    return price["result"]["Last"]


def get_BTC_HYDRO_price_bittrex():
    """Get USD price of HYDRO."""
    price = BITTREX.get_ticker("BTC-HYDRO")
    assert price["success"]
    return price["result"]["Last"]


def get_USD_ETH_price_bittrex():
    """Get USD price of ETH."""
    price = BITTREX.get_ticker("USD-ETH")
    assert price["success"]
    return price["result"]["Last"]
