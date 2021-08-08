from numpy.random._examples.cffi.extending import vals
from odoo import api, fields, models, _, tools
from odoo import fields, models
from odoo.exceptions import ValidationError


class Employee_rq(models.Model):
    _name = "employee.req"

    rela_user = fields.Many2one('res.users', string='USER Related')
    dl_id = fields.Many2one('dl.req', string="Employee", required=True)

    dl_first_accept = fields.Boolean(default=False, string="DL 1st accepted")
    dl_second_accept = fields.Boolean(default=False, string="DL 2nd accepted")
    pm_accept = fields.Boolean(default=False, string="PM accepted")
    hr_accept = fields.Boolean(default=False, string="hr accepted")
    other_confirm = fields.Boolean(default=False, string="Other confirm")
    req_date = fields.Date(string="Request Date", default=fields.Date.today())

    reason = fields.Selection([
        ('luong thap', 'Luong Thap'),
        ('Met ', 'Met'),
        ('Chuyen Cty', 'Chuyen Cty'),
        ('khac', 'Khac'),
    ])
    status = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Send')
    ], default='draft')

    def send_req(self):
        for record in self:
            record.status = 'send'

    def cancel_send_req(self):
        for record in self:
            record.status = 'draft'

    def Dl_approud_1(self):
        for record in self:
            record.dl_first_accept = True

    def Dl_approud_2(self):
        for record in self:
            record.dl_second_accept = True

    def PM_approud(self):
        for record in self:
            record.pm_accept = True

    def HR_approud(self):
        for record in self:
            record.hr_accept = True
