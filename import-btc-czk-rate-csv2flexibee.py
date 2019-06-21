#!/usr/bin/env python
#
# Purpose: simple script that loads btc/czk exchange rates from CSV into flexibee
# Synopsis: see below
#
import sys
import requests
import os
import flexibee.api
import importlib
import fileinput
from flexibee.api import RateRequest
from flexibee.objects import ExchangeRate


if len(sys.argv) != 3:
    print "Missing user settings"
    print "Synopsis: %s settings" % os.path.basename(sys.argv[0])
    sys.exit(2)

# import custom settings
settings = importlib.import_module(sys.argv[1])
csv_file = fileinput.input(sys.argv[2], openhook=fileinput.hook_encoded("utf-8"))

req = flexibee.api.RateRequest()

# Skip the header
csv_file.readline()
for line in csv_file:
    (date, none1, none2, btc_czk) = line.rstrip().split(';')
    # Set correct decimal point for exchange rate object
    btc_czk = btc_czk.replace(',', '.')
    req.append(ExchangeRate.new_for_update(date, btc_czk))

try:
    print "Sending: %s" % req

    response = req.put(settings.url, settings.user, settings.passwd)

    print response

except Exception, e:
    print 'Error: %s' % e
    sys.exit(2)
