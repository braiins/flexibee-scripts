#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Purpose: This script processes all unpaid invoices by converting
# them from CZK to BTC and creating a cash payment within the
# accounting system. The result is CSV payment order that can be
# imported into e.g. Electrum.
#
# Synopsis: see below
#
#
# Copyright © 2015 Braiins Systems s.r.o. <jan.capek@braiins.cz>
#
# This file is part of PyFlexibee <https://github.com/braiins/pyflexibee/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import requests
import os
from flexibee.api import ReceivedInvoiceRequest
from flexibee.api import RateRequest
from flexibee.api import CashTransactionRequest
from flexibee.objects import DynamicObject
from flexibee.objects import InvoiceCashPayment
from flexibee.objects import ExchangeRate
import re
import importlib
import traceback
from datetime import date
from decimal import Decimal
import argparse



class ExchangeRateToday(object):
    """
    Helper class loads today's exchange rate from flexibee
    """

    def __init__(self, settings):
        today_str = date.today().strftime("%Y-%m-%d")
        # request to fetch the current BTC/USD exchange rate
        exchange_rate_req = \
            RateRequest("mena='code:UBTC' and platiOdData >= '%s'" % today_str)
        self.exchange_rate_btc_today = \
            exchange_rate_req.get_and_build_objects(ExchangeRate,
                                                    settings.url,
                                                    settings.user,
                                                    settings.passwd,
                                                    params={'limit':'1',
                                                            },
        )
        if len(self.exchange_rate_btc_today) == 0:
            raise Exception('No BTC/CZK exchange rate available for today: %s' % today_str)


    def lookup(self, invoice_code):
        """
        Returns today's exchange rate regardless of the invoice code

        @return exchange rate for an invoice code
        """
        return self.exchange_rate_btc_today[0]


    def __str__(self):
        return '%s BTC/CZK' % self.exchange_rate_btc_today[0].nbStred



class ExchangeRatePerInvoice(object):
    """
    Helper class that loads per invoice exchange rate table from a file.

    It provides exchange rates for individual invoices.
    """
    def __init__(self, exchange_rate_file):
        self.invoice_rates = {}
        f = open(exchange_rate_file, 'r')
        for line in iter(f):
            (inv_code, inv_date, btc_czk) = line.rstrip().split(';')
            self.invoice_rates[inv_code] = \
                ExchangeRate.new_for_update(inv_date, btc_czk)
        f.close()


    def lookup(self, invoice_code):
        """
        @return exchange rate for an invoice code
        """
        return self.invoice_rates[invoice_code]


    def __str__(self):
        return 'N/A (individual exchange rate for each processed invoice: %s' % \
            self.invoice_rates



parser = argparse.ArgumentParser(description='Prepares payments for all unpaid BTC invoices. Currently, the script processes only plain invoices without items!')

parser.add_argument('-w', '--write-changes', dest='dry_run', action='store_false',
                   default=True,
                   help='Write actual changes to invoices and payments in flexibee (disabled by default)')
parser.add_argument('-e', '--exchange-rate-file', dest='exchange_rate_file',
                    default=None,
                    help='Load exchange rates for individual invoices from a simple CSV in the form: "invoice number;exchange_rate"')
parser.add_argument('-s', '--disable-ssl-check', action='store_const',
                    dest='config_ssl_check',
                    const=requests.packages.urllib3.disable_warnings,
                    default=lambda: None,
                    help='Disable SSL checking (insecure)')
parser.add_argument('settings_module_name',
                    help='Name of the configuration module with connection details')

args = parser.parse_args()

# Configure SSL checking as specified on the command line
args.config_ssl_check()
# import custom settings
settings = importlib.import_module(args.settings_module_name)

today_str = date.today().strftime("%Y-%m-%d")

# request to fetch all unpaid invoices
unpaid_invoices_req = ReceivedInvoiceRequest("(stavUhrK is empty)")
# and datSplat > now())")

try:

    unpaid_invoices = \
        unpaid_invoices_req.get_and_build_objects(DynamicObject,
                                                  settings.url,
                                                  settings.user,
                                                  settings.passwd,
                                                  params={'limit':'0',
                                                          'includes':'faktura-prijata/banSpojDod',
                                                          'detail': 'full',
                                                          },
                                                  )

    unpaid_invoices_update_req = ReceivedInvoiceRequest()
    unpaid_invoices_payment_req = ReceivedInvoiceRequest()
    # Iterate through all unpaid invoices an generate payment CSV lines
    payment_csv_lines = []
    payment_descriptions = []

    if args.exchange_rate_file is None:
        exchange_rate_registry = ExchangeRateToday(settings)
        get_payment_date = lambda invoice: today_str
    else:
        exchange_rate_registry = ExchangeRatePerInvoice(args.exchange_rate_file)
        get_payment_date = lambda invoice: invoice.datVyst


    for invoice in unpaid_invoices:
        invoice_exchange_rate = exchange_rate_registry.lookup(invoice.kod)
        total_in_ubtc = \
            invoice_exchange_rate.convert_to_currency(invoice.sumCelkem)
        total_in_ubtc_str = '%s' % total_in_ubtc.quantize(Decimal('1e-2'))
        total_in_btc = (total_in_ubtc) / 1000000
        total_in_btc_str = '%s' % total_in_btc.quantize(Decimal('1e-8'))

        payment_csv_lines.append('%s,%s' %
                                 (invoice.banSpojDod[0]['buc'].strip(),
                                  total_in_btc_str))
        company_name = invoice.banSpojDod[0]['firma'].replace('code:', '')
        payment_descriptions.append(company_name)

        # Add the invoice to the update request to convert the unpaid
        # invoice to a uBTC invoice
        unpaid_invoices_update_req.append(
            DynamicObject(id=invoice.id,
                          mena='code:UBTC',
                          kurzMnozstvi=invoice_exchange_rate.kurzMnozstvi,
                          kurz=invoice_exchange_rate.nbStred)

            )
        # Prepare an invoice cash payment
        unpaid_invoices_payment_req.append(
            InvoiceCashPayment(invoice_id=invoice.id,
                               pokladna='code:POKLADNA BTC',
                               typDokl='code:STANDARD',
                               castka=total_in_ubtc_str,
                               kurzKDatuUhrady='false',
                               datumUhrady=get_payment_date(invoice)))


    if args.dry_run:
        print 'Dry run, skipping conversion of unpaid invoices and payment.'
        print 'Showing the resulting flexibee requests.'
        print 'Unpaid invoices update:'
        print unpaid_invoices_update_req
        print 'Unpaid invoices payment request:'
        print unpaid_invoices_payment_req
    else:
        # Update the invoice (convert it to an invoice in BTC based on
        # today's exchange rate)
        print 'Updating all invoices with current BTC exchange rate'
        response = unpaid_invoices_update_req.put(settings.url, settings.user,
                                                  settings.passwd)
        print 'Received: %s' % response.content

        print 'Updating all invoices'
        response = unpaid_invoices_payment_req.put(settings.url, settings.user,
                                                   settings.passwd)
        print 'Received: %s' % response.content


    # r = CashTransactionRequest()
    # r.append(DynamicObject(id='41',
    #                        sumCelkemMen='22500'
    #                        )
    #          )
    # response = r.put(settings.url, settings.user, settings.passwd)
    #print 'ReceivedXXXX: %s' % response.content
    print '----- CSV PAYMENT for Electrum CUT HERE ----'
    for line in payment_csv_lines:
        print line
    print '--------------------------------------------'
    print 'Description: %s %s' % ((',').join(payment_descriptions), today_str)
    print 'Exchange Rate: %s' % exchange_rate_registry



except Exception, e:
    print 'Error: %s' % e
    print(traceback.format_exc())
    sys.exit(2)
