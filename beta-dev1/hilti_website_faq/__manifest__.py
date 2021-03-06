{
    'name': 'HILTI Website FAQ',
    'description': 'This module will add functionality of FAQ.',
    'category': 'Website',
    'version': '1.0',
    'author': 'HILTI / Mustufa Kantawala',
    'website': 'http://www.hilti.com',
    'depends': ['website', 'hilti_modifier_company'],
    'data': [
        'security/ir.model.access.csv',
        'data/hashmicro_website_data.xml',
        'views/website_faq_template.xml',
        'views/website_faq.xml',
    ],
    'application': True,
    'installable': True,
}