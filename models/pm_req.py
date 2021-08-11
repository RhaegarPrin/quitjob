from odoo import fields, models


class pm_req(models.Model):
    _name = "pm.req"

    dl_reqs = fields.One2many('dl.req', 'pm_id', string="List_req", domain=[('valid_reqs', '=', True)])
    emp_reqs = fields.One2many('employee.req', 'pm_id', domain=[('dl_first_accept', '=', True)])
    rela_user = fields.Many2one('res.users', string='USER Related', default=lambda self: self.env.user)
    hr_id = fields.Many2one('hr.req', string='HR_rq')

