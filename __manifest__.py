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
    'depends': [],
    'data': [
        'view/menu.xml',
        'view/form_view.xml',
        'view/dl_view.xml',
        'view/pm_view.xml',
        'view/interview_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
