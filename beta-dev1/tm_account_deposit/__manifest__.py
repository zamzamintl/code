# -*- coding: utf-8 -*-
{
    'name': 'TM Account Deposit',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'website': "http://www.hashmicro.com",
    'summary': 'TM Account Deposit',
    'depends': [
        'account','account_cancel',
    ],
    'data': [
        'wizard/return_deposit_wizard_view.xml',
        'wizard/reconcile_deposit_wizard_view.xml',
        'wizard/convert_to_revenue_view.xml',
        'views/account_deposit_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
