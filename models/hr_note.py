from odoo import fields,models


class hr_wizard(models.Model):
    _name='hr_note_test'
    employee_req_id = fields.Many2one('employee.req')
    notes = fields.Char(string='HR Note')
    carr = fields.Boolean(string='Ho so')
