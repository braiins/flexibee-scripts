#!/usr/bin/python
#
# Purpose: simple script that loads btc/czk exchange rates from CSV into flexibee
# Synopsis: see below
#
import sys
import requests
import os
import flexibee.api



if len(sys.argv) != 3:
    print "Missing login credentials"
    print "Synopsis: %s user password" % os.path.basename(sys.argv[0])
    sys.exit(2)

acc_url = "https://acc.bnet:5434/c/braiins_systems_s_r_o_1/kurz.json"

# fetch all exchange rates
rates = []
for line in sys.stdin:
    (date, none1, none2, btc_czk) = line.rstrip().split(';')
    rates.append(flexibee.api.ExchangeRate(date, btc_czk))

rate_req = flexibee.api.RateRequest(rates).to_json()

print "Sending: %s" % rate_req

response = requests.put(acc_url, data=rate_req, auth=(sys.argv[1], sys.argv[2]),
			verify=False)

print response.content
