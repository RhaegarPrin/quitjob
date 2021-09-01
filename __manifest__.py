# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'QUITJOB',
    'version': '1.1',
    'summary': 'employee quitjob manage',
    'sequence': -11,
    'description': "None",
    'category': 'Accounting/Accounting',
    'website': 'https://www.odoo.com/page/billing',
    'images': [],
    'depends': ['sale', 'hr', 'hr_contract', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'view/menu.xml',
        'view/popup_form.xml',
        'view/form_view.xml',
        'view/dl_view_form.xml',
        'view/hr_view_form.xml',
        'wizard/create_hr_note.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
