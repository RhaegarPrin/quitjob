from odoo import api, fields, models, _, tools
from odoo import fields, models
from odoo.exceptions import ValidationError


class Employee_rq(models.Model):
    _name = "employee.req"

    rela_user = fields.Many2one('res.users', string='USER Related', default=lambda self: self.env.user,
                                required=True)
    rela_user_email = fields.Char(related="rela_user.email")
    dl_id = fields.Many2one('dl.req', string="DL", required=True, default=lambda self: self.env['dl.req'].search([]))
    pm_id = fields.Many2one('pm.req', related='dl_id.pm_id', default=lambda self: self.env['pm.req'].search([]))
    it_id = fields.Many2one('it.req')

    dl_first_accept = fields.Boolean(default=False, string="DL 1st accepted")
    dl_second_accept = fields.Boolean(default=False, string="DL 2nd accepted")
    pm_accept = fields.Boolean(default=False, string="PM accepted")
    hr_accept = fields.Boolean(default=False, string="hr accepted")
    other_confirm = fields.Boolean(default=False, string="Other confirm")
    result = fields.Boolean(compute="_compute_status")
    req_date = fields.Date(string="Request Date", default=fields.Date.today())
    est_date = fields.Date(string="Request Date")

    reason = fields.Selection([
        ('luong thap', 'Luong Thap'),
        ('Met ', 'Met'),
        ('Chuyen Cty', 'Chuyen Cty'),
        ('khac', 'Khac'),
    ])

    status = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Send'),
        ('dl1', 'Dl 1st accepted'),
        ('pm', 'PM accepted'),
        ('dl2', 'Dl 2nd accepted'),
        ('hr', 'Hr accepted'),
        ('it', 'IT confirmed'),
        ('done', 'All done'),
    ], default='draft')
    interview_ids = fields.One2many('interview_rs', 'emp_id', string="interviews", store=True)

    def send_req(self):
        for record in self:
            if record.status == 'draft':
                record.status = 'send'
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_dl").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    def cancel_send_req(self):
        for record in self:
            if record.dl_first_accept == False:
                record.status = 'draft'

    def Dl_approud_1(self):
        for record in self:
            if record.dl_second_accept == False:
                record.dl_first_accept = True
                record.status = 'dl1'
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_pm").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    def Dl_approud_1_cancel(self):
        for record in self:
            if record.pm_accept == False:
                record.status = 'send'
                record.dl_first_accept = False

    def Dl_approud_2(self):
        for record in self:
            if record.hr_accept == False:
                record.dl_second_accept = True
                record.status = 'dl2'
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_hr").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    def Dl_approud_2_cancel(self):
        for record in self:
            if record.hr_accept == False:
                record.status = 'pm'
                record.dl_second_accept = False

    def PM_approud(self):
        for record in self:
            if record.dl_second_accept == False and record.dl_first_accept:
                record.pm_accept = True
                record.status = 'pm'
                template_id = self.env.ref("quitjob_manage.mail_template_pm_2_dl").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    def PM_approud_cancel(self):
        for record in self:
            if record.dl_second_accept == False:
                record.status = 'dl1'
                if record.dl_first_accept == False:
                    record.status = 'send'
                record.pm_accept = False

    def HR_approud(self):
        for record in self:
            if record.other_confirm == False and record.dl_second_accept:
                record.hr_accept = True
                record.status = 'hr'
                print('email : ', record.rela_user.login)
                print(record.dl_id.rela_user.login)
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_it").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    def HR_approud_cancel(self):
        for record in self:
            if record.dl_second_accept == False:
                record.status = 'send'
            else:
                record.status = 'dl2'
            record.hr_accept = False

    def it_confirm(self):
        for record in self:
            if record.hr_accept:
                record.other_confirm = True
                record.status = 'it'

    def delete_rec(self):
        for record in self:
            if record.dl_second_accept == False:
                record.unlink()



