from odoo import fields,models


class hr_wizard(models.TransientModel):
    _name='hr_note_trans'
    employee_req_id = fields.Many2one('employee.req')
    notes = fields.Char(string='HR Note')
    pm_notes = fields.Char(string='PM Note')
    dl_notes = fields.Char(string='DL Note')
    carr = fields.Boolean(string='Ho so')
