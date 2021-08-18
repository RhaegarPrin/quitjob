from odoo import fields, models


class hr_req(models.Model):
    _name = "hr.req"

    name = fields.Char(string="name resuser", related='rela_user.login')
    pm_reqs = fields.One2many('pm.req', 'hr_id', string="List_PM_req")
    rela_user = fields.Many2one('res.users', string='USER Related', default=lambda self: self.env.user)
    emp_reqs = fields.One2many('employee.req', 'pm_id', string='EMP reqs', domain=[('dl_second_accept', '=', True)])
