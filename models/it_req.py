from odoo import fields, models


class it_req(models.Model):
    _name = "it.req"

    rela_user = fields.Many2one('res.users', string='USER Related', default=lambda self: self.env.user)
    emp_reqs = fields.One2many('employee.req', 'it_id', string='EMP reqs', domain=[('hr_accept', '=', True)])
