# Overview

A set of flexibee automation scripts allows controlling flexibee via
API. Each script requires a settings file that specifies flexibee
connecting URL, and credentials.

## Settings file

Example configuration is given in: settings_template.py

## Installation into virtual environment

```
mkdir flexibee-automation
cd flexibee-automation
mkdir config
virtualenv .env
echo `pwd`/config > ./.env/lib/python2.7/site-packages/flexibee-scripts-config.pth
source .env/bin/activate
```

Install all requirements:

pip install -r requirements.txt

Custom configuration settings can be placed in **flexibee-automation/config** directory or similar depending on particular path setup


## Current Script Suite

The set of script provides the following automated operations:

- import daily bitcoin exchange rate based on the average rate from
  bitstamp
- processing of bank transactions based on user specified map/filter
- transformation of CZK invoices to BTC while using the current
  exchange rate
