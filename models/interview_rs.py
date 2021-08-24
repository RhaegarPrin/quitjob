from odoo import fields, models


class interview_rs(models.Model):
    _name = "interview_rs"

    emp_id = fields.Many2one('employee.req', string='Employee')

    note = fields.Char(string='Pm Note')
    emp_view = fields.Boolean(default=False)
    result = fields.Boolean(string='Interview Result', default=False)


