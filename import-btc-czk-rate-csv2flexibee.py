#!/usr/bin/python
#
# Purpose: simple script that loads btc/czk exchange rates from CSV into flexibee
# Synopsis: see below
#
import sys
import requests
import os
import flexibee.api
import importlib


if len(sys.argv) != 2:
    print "Missing user settings"
    print "Synopsis: %s settings" % os.path.basename(sys.argv[0])
    sys.exit(2)

# import custom settings
settings = importlib.import_module(sys.argv[1])


req = flexibee.api.RateRequest()
for line in sys.stdin:
    (date, none1, none2, btc_czk) = line.rstrip().split(';')
    req.append(flexibee.api.ExchangeRate(date, btc_czk))


try:
    print "Sending: %s" % req

    response = req.send(settings.url, settings.user, settings.passwd)

    print response.content

except Exception, e:
    print 'Error: %s' % e
    sys.exit(2)
