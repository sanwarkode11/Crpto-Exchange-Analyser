# Create your views here.
import json
from decimal import Decimal

import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets



class CrptoDifferenceViewSet(View):


    def get(self, request):

        response_from_wazirx = requests.get("https://api.wazirx.com/api/v2/tickers")
        response_wtext = response_from_wazirx.json()
        response_from_binance = requests.get("https://api.binance.com/api/v3/ticker/price")
        response_btext = response_from_binance.json()
        # currency_response =requests.get("https://paxful.com/rest/v2/currencies/INR?transformResponse=camelCase")
        # print(json.loads(response_from_binance.text))
        # currency_response_text = currency_response.json()
        # btc_inr = currency_response_text["rate"]["btc"]
        response_for_btc_to_eur = requests.get(
            "https://www.binance.com/bapi/asset/v2/public/asset-service/product/get-products", {"includeEtf": "true"})
        btc_to_euro = response_for_btc_to_eur.json()["data"]
        btc_to_eur_price = next(item for item in btc_to_euro if item["s"] == "BTCEUR")["c"]
        respose_for_currency_converter = requests.get(
            "https://www.binance.com/bapi/asset/v1/public/asset-service/product/currency")
        currency_exchange = respose_for_currency_converter.json()["data"]
        currency_list = list((item for item in currency_exchange if item["pair"] in ["EUR_USD", "INR_USD"]))
        # currency_list = next(item for item in currency_exchange if item["pair"] in ["EUR_USD"])
        # currency_list = next(item for item in currency_exchange if item["pair"] in ["INR_USD"])
        usd_to_eur, usd_to_inr = (currency_list[0]["rate"], currency_list[1]["rate"]) if currency_list[0][
                                                                                             "pair"] == "EUR_USD" else (
            currency_list[1]["rate"], currency_list[0]["rate"])
        print(usd_to_eur, usd_to_inr)
        exchange_response = {}

        wazirx_btc = response_wtext["btcinr"]["last"]
        binance_btc = Decimal(btc_to_eur_price) * Decimal(usd_to_inr) / Decimal(usd_to_eur)
        difference_btc = Decimal(wazirx_btc) / Decimal(binance_btc)
        difference_btc *=100

        exchange_response.update({
            "BTC":
                {"wazirx_price": wazirx_btc,
                 "binance_price": round(binance_btc, 4),
                 "difference":str(round(difference_btc,2))}
        })
        for crpto in response_btext:
            # result = [ item["price"] for item in response_btext if item["symbol"] == value["base_unit"].upper() + "BTC"]
            # print(result)
            crpto_base_name = crpto["symbol"].split("BTC")[0].lower()
            base_name_with_unit = crpto_base_name + "inr"
            if base_name_with_unit in response_wtext:

                binance_crpto_price = Decimal(crpto["price"]) * Decimal(usd_to_inr) * Decimal(
                    btc_to_eur_price) / Decimal(usd_to_eur)

                wazirx_price = response_wtext[base_name_with_unit]["last"]
                difference = Decimal(wazirx_price) / Decimal(binance_crpto_price)
                difference *= 100
                print(difference)

                exchange_response.update(
                    {crpto_base_name.upper():
                         {"wazirx_price": wazirx_price,
                          "binance_price": str(round(binance_crpto_price, 4)),
                          "difference": str(round(difference,2))}})

                # exchange_response

        return HttpResponse(json.dumps(exchange_response), content_type="application/json")

        # return render(request, "application/table.html", context={"dict": exchange_response})
