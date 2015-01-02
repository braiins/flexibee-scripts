#!/usr/bin/python
#
# Purpose: simple script that loads btc/czk exchange rates from CSV into flexibee
# Synopsis: see below
#
import sys
import requests, json
import os


class ExchangeRate(object):
    """
    Exchange rate object as required by the flexibee API
    """
    def __init__(self, valid_from, rate, currency='code:UBTC', amount=1000000):
	self.mena = currency
	self.nbStred = rate
	self.platiOdData = valid_from
	self.kurzMnozstvi = amount


class RateRequest(object):
    """
    Represents the exchange rate request
    """
    def __init__(self, rates=[]):
	"""
	@param rates - a list of exchange rates
	"""
	self.rates = rates

    def to_json(self):
	json_dict = {"winstrom":
			 {"@version":"1.0",
			  "kurz": [ r.__dict__ for r in self.rates ]
			  }
		     }

	return json.dumps(json_dict)


if len(sys.argv) != 3:
    print "Missing login credentials"
    print "Synopsis: %s user password" % os.path.basename(sys.argv[0])
    sys.exit(2)

acc_url = "https://acc.bnet:5434/c/braiins_systems_s_r_o_1/kurz.json"

# fetch all exchange rates
rates = []
for line in sys.stdin:
    (date, none1, none2, btc_czk) = line.rstrip().split(';')
    rates.append(ExchangeRate(date, btc_czk))

rate_req = RateRequest(rates).to_json()

print "Sending: %s" % rate_req

response = requests.put(acc_url, data=rate_req, auth=(sys.argv[1], sys.argv[2]),
			verify=False)

print response.content
