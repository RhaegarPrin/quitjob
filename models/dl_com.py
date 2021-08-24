from odoo import fields, models


class dl_com(models.Model):
    _name = 'quit.note'

    emp_req_id = fields.Many2one('employee.req', string='Employee Req')
    name = fields.Char(string='Name')
    status = fields.Selection([
        ('yes', 'Có'),
        ('no', 'Không'),
        ('other', 'Khác')
    ], default='no', string='status')
    note = fields.Char(string='Note')
    # emp_id = fields.Many2many('employee.req')
