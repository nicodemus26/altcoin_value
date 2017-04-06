#!/usr/bin/env python
import click
import collections
import decimal
import requests
import sys
import yaml

FIAT_SUPPORTED = [
    "AUD",
    "BRL",
    "CAD",
    "CHF",
    "CNY",
    "EUR",
    "GBP",
    "HKD",
    "IDR",
    "INR",
    "JPY",
    "KRW",
    "MXN",
    "RUB",
    "USD",
]

@click.command()
@click.option("--fiat-symbol", default="USD",
    type=click.Choice(FIAT_SUPPORTED),
    help="Convert value into this fiat currency.")
@click.option("--yaml-assets", multiple=True,
    type=click.File(mode="rb"),
    help="Path to a YAML file defining some of your assets")
def main(fiat_symbol=None, yaml_assets=None):
    decimal.getcontext().prec = 19
    params = {}
    assets = collections.defaultdict(decimal.Decimal)
    for assets_fh in yaml_assets:
        vals = yaml.load(assets_fh)
        if "assets" not in vals:
            print("Invalid YAML. See example.yaml.")
            sys.exit(1)
        i = 0
        for asset in vals["assets"]:
            for expectation in ["symbol", "count"]:
                if expectation not in asset:
                    print("Invalid YAML: expected key '%s' on asset. See example.yaml." % (expectation,))
                    sys.exit(1)
            symbol = asset["symbol"]
            count = asset["count"]
            label = asset["label"] if "label" in asset else ""
            assets[(symbol, label)] = assets[(symbol, label)] + decimal.Decimal(count)
    
    if fiat_symbol != "USD":
        params["convert"] = fiat_symbol
    req = requests.get("https://api.coinmarketcap.com/v1/ticker/",
                       params=params)
    ticker_list = req.json()
    tickers = dict((t["symbol"], t) for t in ticker_list)
    print("Symbol Total                 Price %3s             Total %3s             Pct Ch 1h             Pct 1d                Pct 1w                Fiat 1h               Fiat 1d               Fiat 1w               Label" % (fiat_symbol, fiat_symbol))
    print("====== ===================== ===================== ===================== ===================== ===================== ===================== ===================== ===================== ===================== =====")
    total_fiat, total_fiat_1h, total_fiat_1d, total_fiat_1w = decimal.Decimal(0),decimal.Decimal(0),decimal.Decimal(0),decimal.Decimal(0)
    for symbol, label in assets.keys():
        total = assets[(symbol, label)]
        if symbol not in tickers:
            print("%s\t%s\tUnknown symbol." %(symbol, total))
            continue
        tick = tickers[symbol]
        price = decimal.Decimal(tick["price_%s" % (fiat_symbol.lower())])
        in_fiat = total*price
        pct_1h = decimal.Decimal(tick["percent_change_1h"]) / 100
        pct_1d = decimal.Decimal(tick["percent_change_24h"]) / 100
        pct_1w = decimal.Decimal(tick["percent_change_7d"]) / 100
        price_1h = price-(price / (1 + pct_1h))
        price_1d = price-(price / (1 + pct_1d))
        price_1w = price-(price / (1 + pct_1w))
        total_1h = total*price_1h
        total_1d = total*price_1d
        total_1w = total*price_1w
        total_fiat = total_fiat + in_fiat
        total_fiat_1h = total_fiat_1h + total_1h
        total_fiat_1d = total_fiat_1d + total_1d
        total_fiat_1w = total_fiat_1w + total_1w
        print("%6s %21s %21s %21s %21s %21s %21s %21s %21s %21s %s" %(
            symbol, total, price, in_fiat, pct_1h*100, pct_1d*100, pct_1w*100, total_1h, total_1d, total_1w, label))
    if total_fiat > 0:
        print("%6s %21s %21s %21s %21s %21s %21s %21s %21s %21s %s" %(
            "TOTAL", "N/A", "N/A", total_fiat, (1-(total_fiat-total_fiat_1h)/total_fiat)*100, (1-(total_fiat-total_fiat_1d)/total_fiat)*100, (1-(total_fiat-total_fiat_1w)/total_fiat)*100, total_fiat_1h, total_fiat_1d, total_fiat_1w, ""))
        
        


if __name__ == "__main__":
    main()
