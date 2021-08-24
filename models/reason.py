from odoo import fields, models



class reson_quit(models.Model):
    _name = 'quit.reason'

    name = fields.Char(string='Name')
    # emp_id = fields.Many2many('employee.req')
