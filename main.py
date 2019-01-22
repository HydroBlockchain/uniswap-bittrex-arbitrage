import uniswap
import bittrex_local as bittrex


def binary_search(current_commitment, next_step_size, uniswap_direction, bittrex_direction):
    """Find a HYDRO volume to trade."""
    uniswap_trade = uniswap.market_order_uniswap(current_commitment, uniswap_direction)
    bittrex_trade = bittrex.market_order_bittrex(bittrex_orderbook, current_commitment, bittrex_direction)

    hydro_usd_price_uniswap = uniswap_trade[1] * eth_usd_price
    hydro_usd_price_bittrex = bittrex_trade[1] * btc_usd_price

    prices_swapped = True if (
        ((uniswap_direction == "buy_hydro") and (hydro_usd_price_uniswap > hydro_usd_price_bittrex)) or
        ((uniswap_direction == "sell_hydro") and (hydro_usd_price_uniswap < hydro_usd_price_bittrex))
    ) else False

    print()
    if prices_swapped:
        print(f"Trading {current_commitment:,} HYDRO would bring prices past parity, trying again...")
        binary_search(int(current_commitment - next_step_size), int(next_step_size / 2), uniswap_direction, bittrex_direction)
    else:
        print(f"Trading {current_commitment:,} HYDRO would bring prices closer to parity...")
        trade_volume_usd_uniswap = uniswap_trade[0] * eth_usd_price
        trade_volume_usd_bittrex = bittrex_trade[0] * btc_usd_price

        profit = trade_volume_usd_bittrex - trade_volume_usd_uniswap if uniswap_direction == "buy_hydro" else trade_volume_usd_uniswap - trade_volume_usd_bittrex
        assert profit > 0

        print(f"    Counterfactual Uniswap Price: ${hydro_usd_price_uniswap:0.12f}")
        print(f"    Counterfactual Bittrex Price: ${hydro_usd_price_bittrex:0.12f}")
        percent_difference_counterfactual = get_percent_difference(hydro_usd_price_uniswap, hydro_usd_price_bittrex)
        percent_improvement = (price_percent_difference - percent_difference_counterfactual) / price_percent_difference
        print(f"    This is a {percent_improvement * 100:0.4f}% improvement over the current prices.")
        print(f"    It would lead to profits of ${profit:,.2f}.")

        if (percent_improvement < percent_improvement_threshold):
            binary_search(int(current_commitment + next_step_size), int(next_step_size / 2), uniswap_direction, bittrex_direction)
        else:
            print()
            print("Recommendation:")
            if (uniswap_direction == "buy_hydro"):
                print(f"    Buy {current_commitment:,} HYDRO on Uniswap for ${trade_volume_usd_uniswap:,.2f} worth of ETH.")
                print(f"    Sell {current_commitment:,} HYDRO on Bittrex for ${trade_volume_usd_bittrex:,.2f} worth of BTC.")
                print(f"    Profit: ${profit:,.2f}.")
            else:
                print(f"    Buy {current_commitment:,} HYDRO on Bittrex for ${trade_volume_usd_bittrex:,.2f} worth of BTC.")
                print(f"    Sell {current_commitment:,} HYDRO on Uniswap for ${trade_volume_usd_uniswap:,.2f} worth of ETH.")
                print(f"    Profit: ${profit:,.2f}.")


def get_percent_difference(x, y):
    """Compute percent difference betwen x and y."""
    return abs(x - y) / ((x + y) / 2)


print("Loading Data...")

btc_usd_price = bittrex.get_USD_BTC_price_bittrex()
eth_usd_price = bittrex.get_USD_ETH_price_bittrex()

hydro_eth_price_uniswap = uniswap.get_ETH_HYDRO_price_uniswap()
hydro_btc_price_bittrex = bittrex.get_BTC_HYDRO_price_bittrex()

hydro_usd_price_uniswap = hydro_eth_price_uniswap * eth_usd_price
hydro_usd_price_bittrex = hydro_btc_price_bittrex * btc_usd_price

price_percent_difference = get_percent_difference(hydro_usd_price_uniswap, hydro_usd_price_bittrex)

print()
print(f"Current HYDRO Price Uniswap: ${hydro_usd_price_uniswap:0.12f}")
print(f"Current HYDRO Price Bittrex: ${hydro_usd_price_bittrex:0.12f}")
print(f"Price Differential: {price_percent_difference * 100:.4f}%")
print()

price_percent_difference_threshold = .1
percent_improvement_threshold = .95

if (price_percent_difference >= price_percent_difference_threshold):
    print(f"Running Arbitrage Calculations...")
    bittrex_orderbook = bittrex.get_orderbook_bittrex()

    if (hydro_usd_price_uniswap > hydro_usd_price_bittrex):
        uniswap_direction = "sell_hydro"
        bittrex_direction = "buy_hydro"
        max_commitment_exchange = bittrex.get_HYDRO_supply(bittrex_orderbook, bittrex_direction)
    else:
        uniswap_direction = "buy_hydro"
        bittrex_direction = "sell_hydro"
        max_commitment_exchange = uniswap.get_HYDRO_supply()

    max_commitment_self = 1000000000
    max_commitment = min(max_commitment_self, max_commitment_exchange)

    print()
    print(f"Searching for optimal arbitrage strategy to {uniswap_direction.split('_')[0]} HYDRO on Uniswap and {bittrex_direction.split('_')[0]} on Bittrex...")
    binary_search(int(max_commitment / 2), int(max_commitment / 4), uniswap_direction, bittrex_direction)
else:
    print("Exiting...")
