from odoo import fields,models


class hr_wizard(models.TransientModel):
    _name='hr_notes'

    employee_req_id = fields.Many2one('employee.req')
    notes = fields.Char(string='HR Note')
    carr = fields.Boolean(string='Ho so')