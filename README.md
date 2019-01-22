# Quickstart

1. Clone this repo:
```bash
git clone https://github.com/NoahZinsmeister/uniswap-bittrex-arbitrage
cd uniswap-bittrex-arbitrage
```

2. Ensure that a Python 3.6 install is available on your command prompt via `python3.6`:
```bash
python3.6 --version
# Python 3.6.5
```

3. Set up a virtual environment:
```bash
python3.6 -m venv hydro-bittrex-arbitrage-env
```

4. Activate your virtual environment:
```bash
source ./hydro-bittrex-arbitrage-env/bin/activate
```

5. Install dependencies:
```bash
pip3.6 install -r requirements.txt
```

6.
```bash
python3.6 main.py
```


# Explanation

The following explains a strategy to keep the price of a liquid, fungible asset on a decentralized exchange stable relative to the price on a centralized exchange. For the purposes of this example, the asset will be HYDRO, the decentralized exchange will be Uniswap, and the centralized exchange will be Bittrex.

## Pricing
All pricing is relative to USD. In practice, HYDRO is likely to be traded exclusively against non-USD pairs, but for clarity we will assume that for Uniswap and Bittrex, we can compute a single USD-equivalent market price for HYDRO:

```
P_uniswap, P_bittrex
```

Prices are denominated as:

```
1 HYDRO / x USD
```

## Market Orders
When considering the HYDRO price on an exchange in the context of trading, we define vector functions for market buys and sells, which are parameterized by the current order book of the exchange (`OB_{exchange}`) and the volume of the trade (`V_HYDRO`), and return a vector of the USD cost/revenue of the trade (`V_trade`) and the new price (`P_{exchange}`). We assume that the cost is inclusive of all fees, and that no risk or failure probability is involved in executing these trades.

These functions can easily be computed for a given exchange.

### Market Buy
```
MarketBuy_{exchange}(OB_{exchange}, V_HYDRO) = <V_trade, P_{exchange}>
```

This function is increasing for `V_trade` in `V_HYDRO` (it costs more USD to buy more HYDRO) and non-decreasing for `P_{exchange}` in `V_HYDRO` for any given order book (buying HYDRO pushes the price up).

### Market Sell
```
MarketSell_{exchange}(OB_{exchange}, V_HYDRO) = <V_trade, P_{exchange}>
```

This function is increasing for `V_trade` in `V_HYDRO` (it yields more USD to sell more HYDRO) and non-increasing for `P_{exchange}` in `V_HYDRO` for any given order book (selling HYDRO pushes the price down).

## Utility Function
Our utility is a function of the prices of HYDRO on Uniswap and Bittrex.

```
Utility(P_uniswap, P_bittrex)
```

One way to parametrize this function is:

```
U(P_uniswap, P_bittrex) = (P_uniswap - P_bittrex)**2
```

This function is increasing in the price differential between the exchanges, and scales non-linearly with the magnitude of the differential.

## Strategy
As soon as a price differential emerges, we seek to extinguish it by a) executing a market buy on the exchange with the lower price, b) executing a market sell on the exchange with a higher price, or c) both. One reason to pursue a) or b) would be if we consider one exchange as a fundamentally better/more stable/etc. market. In this scenario, we would trade on the other exchange to bring the price back to parity with the stable exchange. However, this leaves us long either HYDRO or the asset we received for it (ETH, say), every time the price changes on the non-stable exchange. So, we will consider option c), which lets us extinguish this long position, and not take a stance on the stability of either exchange.

If we assume that:

```
P_uniswap > P_bittrex
```

We execute a market buy on Bittrex, and a market sell on Uniswap:

```
MarketBuy_bittrex(OB_bittrex, V_HYDROBuy) = <V_tradeBuy, P_bittrex>
```

```
MarketSell_uniswap(OB_uniswap, V_HYDROSell) = <V_tradeSell, P_uniswap>
```

that satisfies the following constraints:

```
V_HYDROBuy = V_HYDROSell
P_bittrex = P_uniswap
```

After execution, this leaves us with profits of `V_tradeSell - V_tradeBuy`. This will be a positive number!
