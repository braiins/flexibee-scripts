#!/usr/bin/python
# -*- coding: utf-8 -*-
# Purpose: This script processes bank transactions based on user specified map.
# Synopsis: see below
#
import sys
import requests
import os
import flexibee.api
import flexibee.automation
from flexibee.objects import BankTransaction
import re
import importlib
import traceback

# Disable all SSL related warnings since flexibee is accessible via
# VPN only but the SSL certificate is invalid
requests.packages.urllib3.disable_warnings()


if len(sys.argv) != 2:
    print "Missing user settings"
    print "Synopsis: %s settings" % os.path.basename(sys.argv[0])
    sys.exit(2)

# import custom settings
settings = importlib.import_module(sys.argv[1])

# materialize all processors
processors = flexibee.automation.EntryProcessor.create_from_tupples(settings.processing_map)

# fetch all transactions that have not been processed yet
bank_req = flexibee.api.BankRequest("zuctovano='False'")

try:
    transactions = \
        bank_req.get_and_build_objects(BankTransaction,
                                       settings.url,
                                       settings.user,
                                       settings.passwd,
                                       params={'limit':'0'},
                                       attributes=['id',
                                                   'datVyst',
                                                   'mena',
                                                   'popis',
                                                   'typUcOp',
                                                   ])


    # Iterate through all fetched transaction and process them
    for t in transactions:
        print '%s' % t.popis.encode('utf-8')
        for p in processors:
            if p.match(t.popis) is not None:
                # processor provides a new type accounting
                # operation. Therefore, we override the current one
                # (current operation should be empty)
                t.typUcOp = p.get_op()
                bank_req.append(t)

    response = bank_req.put(settings.url, settings.user, settings.passwd)

except Exception, e:
    print 'Error: %s' % e
    print(traceback.format_exc())
    sys.exit(2)
