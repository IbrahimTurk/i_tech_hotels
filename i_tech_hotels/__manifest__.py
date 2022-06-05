# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'I-Tech Hotels',
    'version' : '15.0',
    'summary': 'for Hotels',
    'sequence': 10,
    'description': ' Hotels Managment',
    'category': 'Extra Tools',
    'website': 'https://www.odoo.com/app/billing',
    'depends' : ['base_setup', 'portal', 'digest','account','mail'],
    'data': [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/hotels_sequence_data.xml",
        "static/payment.xml",
        "static/partners.xml",
         "static/users.xml",
        "views/hotels.xml",
        "wizard/create_payment_wizard.xml",
        "reports/hotels_room_print.xml",
        "reports/templates/hotels_template_report.xml",
    ],
    'demo': [],
    'Images': ['static/description/hotels.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
