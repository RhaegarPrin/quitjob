from odoo import fields, models


class pm_req(models.Model):
    _name = "pm.req"

    name = fields.Char(string="name resuser", related='rela_user.login')
    dl_id = fields.Many2one('dl.req',  string="DL ID : ")
    emp_reqs = fields.One2many('employee.req', 'pm_id', domain=[('dl_first_accept','=',True)])
    rela_user = fields.Many2one('res.users', string='USER Related', default=lambda self: self.env.user)
    hr_id = fields.Many2one('hr.req', string='HR_rq' , related='dl_id.hr_id')

