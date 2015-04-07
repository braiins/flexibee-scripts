# -*- coding: utf-8 -*-
# This is a template settings file

from __future__ import unicode_literals

# Common login credentials
url = 'https://your.flexibee:5434/c/your_company_s_r_o_1'
user = 'maintenance'
passwd = 'maintenance'

# Example processing map for process_bank_transactions.py
processing_map = [
    ('Úrok.*', 'ÚROK'),
    ('Kreditni urok', 'ÚROK'),
    ('Transaction fee', 'POPLATKY'),
    ('VZP-zalohy', 'ZDRAV-ZALOHY'),
    ('Srážková daň', 'SRAZKOVA DAN'),
    ('PSSZ - zaloha', 'CSSZ-ZALOHY')
]
