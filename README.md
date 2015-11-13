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
virtualenv .env
source .env/bin/activate
```

Install all requirements:

pip install -r requirements.txt


## Current Script Suite

The set of script provides the following automated operations:

- import daily bitcoin exchange rate based on the average rate from
  bitstamp
- processing of bank transactions based on user specified map/filter
