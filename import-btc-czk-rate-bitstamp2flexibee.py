#!/usr/bin/python
#
# Purpose: simple script that loads btc/czk exchange rates based on
# weighted average BTC price from bitstamp and the current exchange
# rate for this day from cnb
# Synopsis: see below
#
import sys
import requests
import os
import flexibee.api
from decimal import Decimal
import bitstamp.client
from datetime import date

if len(sys.argv) != 3:
    print "Missing login credentials"
    print "Synopsis: %s user password" % os.path.basename(sys.argv[0])
    sys.exit(2)


CNB_API_URI = 'http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt'
CNB_API_CURRENCY_AMOUNT = 2
CNB_API_CURRENCY_CODE = 3
CNB_API_CURRENCY_RATE = 4

# fetch USD exchange rate from CNB
response = requests.get(CNB_API_URI, params={"date": date.today().strftime("%d.%m.%Y")})
rates = {}
for number, line in enumerate(response.iter_lines()):
    if number > 2:
	currency = line.split('|')
	amount = int(currency[CNB_API_CURRENCY_AMOUNT])
	rate_float = Decimal(currency[CNB_API_CURRENCY_RATE].replace(',', '.'))

	rates[currency[CNB_API_CURRENCY_CODE]] = rate_float / amount

usd_czk = rates['USD']

# fetch BTC/USD price - weighted average for the past 24 hours
client = bitstamp.client.Public()
ticker = client.ticker()
btc_usd = Decimal(ticker['vwap'])


btc_czk = usd_czk * btc_usd
btc_czk_str = "%s" % btc_czk.quantize(Decimal('1e-2'))
print "USD/CZK: %s; BTC/USD: %s; BTC/CZK: %s" % (usd_czk, btc_usd, btc_czk_str)


# import the exchange rate into flexibee
acc_url = "https://acc.bnet:5434/c/braiins_systems_s_r_o_1"

req = flexibee.api.RateRequest()
req.append(flexibee.api.ExchangeRate(date.today().strftime("%Y-%m-%d"),
				     btc_czk_str))

print "Sending: %s" % req

response = req.send(acc_url, sys.argv[1], sys.argv[2])

print "Received: %s" % response.content
