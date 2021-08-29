from odoo import api, fields, models, _, tools
from odoo import fields, models
from odoo.exceptions import ValidationError
import datetime


class Employee_rq(models.Model):
    _name = "employee.req"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reasons = fields.Many2many('quit.reason', string='Reasons')
    notes = fields.Many2one('quit.note', string='DL Coms')
    position = fields.Char(compute="_get_position", string='Position')
    job_title = fields.Char(related='employee_id.job_title')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    parent_department_id = fields.Many2one('hr.department', related='department_id.parent_id')
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True,
                                  default=lambda self: self.env.user.employee_id)
    rela_user = fields.Many2one('res.users', string='USER Related', related='employee_id.user_id',
                                required=True)
    contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id', groups="base.group_user")
    pm_id = fields.Many2one('hr.employee', string='pm')
    # domain=lambda self :[('department_id', '=', self.env.user.employee_id.department_id)])
    dl_id = fields.Many2one('hr.employee', string='dl')
    hr_id = fields.Many2one('hr.employee', string='hr')

    parent_id = fields.Many2one('hr.employee', related='department_id.manager_id')
    it_id = fields.Many2one('it.req')

    dl_first_accept = fields.Boolean(default=False, string="DL 1st accepted")
    dl_second_accept = fields.Boolean(default=False, string="DL 2nd accepted")
    pm_accept = fields.Boolean(default=False, string="PM accepted")
    hr_accept = fields.Boolean(default=False, string="hr accepted")
    other_confirm = fields.Boolean(default=False, string="IT confirm")
    acct_confirm = fields.Boolean(default=False, string="Ke toan confirm")
    result = fields.Boolean(compute="_compute_status")
    req_date = fields.Date(string="Request Date", required=True,tracking=True)
    est_date = fields.Date(string="Est Date", compute="_compute_est_date")
    reason = fields.Selection([
        ('luong thap', 'Luong Thap'),
        ('Met ', 'Met'),
        ('Chuyen Cty', 'Chuyen Cty'),
        ('khac', 'Khac'),
    ],tracking=True)
    specific_reason = fields.Char(string="Lý do cụ thể",tracking=True)

    status = fields.Selection([
        ('refuse', 'Refuse'),
        ('draft', 'Draft'),
        ('pm', 'PM Assessing'),
        ('dl2', 'Dl Assessing'),
        ('hr', 'Hr Assessing'),
        ('done', 'Approved')], default='draft',tracking=True)
    creator_role = fields.Char()
    editable = fields.Boolean(default=True, compute='_check_edit_')

    interview_ids = fields.One2many('interview_rs', 'emp_id', string="interviews", store=True)
    hr_notes = fields.One2many('hr_note_trans', 'employee_req_id', string='hr Notes', store=True)
    pm_interview = fields.Char(string='PM Note',
                               groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    dl_interview = fields.Char(string='DL Note',
                               groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    dl_msg_pm = fields.Char(string='DL MSG for PM',
                            groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    hr_interview = fields.Char(string='HR Note',
                               groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    personal_asset = fields.Selection([
        ('no', 'Có'),
        ('yes', 'Không'),
    ], default='no')
    customer_asset = fields.Selection([
        ('no', 'Có'),
        ('yes', 'Không'),
    ], default='no')
    other_asset = fields.Selection([
        ('no', 'Có'),
        ('yes', 'Không'),
    ], default='no')
    Email_asset = fields.Selection([
        ('no', 'Có'),
        ('yes', 'Không'),
    ], default='no')
    git_account = fields.Selection([
        ('no', 'Có'),
        ('yes', 'Không'),
    ], default='no')

    # send req gọi form note , form note gọi send_req_done để chuyển trạng thái
    def send_req_done(self):
        for record in self:
            if record.dl_id.id == False:
                raise ValidationError("Invalid DL ID")

            if record.status == 'draft':
                record.status = 'dl2'
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_dl").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)
                record.editable = False

    def send_req(self):
        form_view = self.env.ref('quitjob_manage.approved_note')
        return {
            'name': _('DL Note'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_model': 'employee.req',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def cancel_send_req(self):
        for record in self:
            record.status = 'draft'
            record.pm_accept = False
            record.dl_first_accept = False
            record.dl_second_accept = False
            record.hr_accept = False
            record.other_confirm = False
            record.acct_confirm = False

    def Dl_approved_done(self):
        for record in self:
            if record.hr_id.id == False :
                raise ValidationError("Invalid Hr ID")
            if record.dl_second_accept == False and record.status != 'draft':
                record.dl_second_accept = True
                record.dl_first_accept = True
                record.pm_accept = True
                record.status = 'hr'
                template_id = self.env.ref("quitjob_manage.mail_template_hr").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)
                record.editable = False

    def Dl_approud_1(self):
        form_view = self.env.ref('quitjob_manage.approved_note')
        return {
            'name': _('DL Note'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_model': 'employee.req',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def DL_2_PM_done(self):
        for record in self:
            if record.pm_id.id == False:
                raise ValidationError("Invalid PM ID")
            if record.hr_accept == False:
                record.status = 'pm'
                record.dl_first_accept = True
                record.dl_second_accept = False
                record.pm_accept = False
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_pm").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    def Dl_2_PM(self):
        form_view = self.env.ref('quitjob_manage.dl_2_pm')
        return {
            'name': _('DL Note'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_model': 'employee.req',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    # Gọi form refuse pm , dl , hr đều dùng
    def call_Refuse_form(self):
        form_view = self.env.ref('quitjob_manage.refuse_note')
        return {
            'name': _('DL Note'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_model': 'employee.req',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def pm_refuse_done(self):
        for record in self:
            record.status = 'refuse'
            record.pm_accept = False
        template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        record.editable = False

    def dl_refuse_done(self):
        for record in self:
            record.status = 'refuse'
            record.pm_accept = False
            record.dl_first_accept = False
            record.dl_second_accept = False
        template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        record.editable = False

    def hr_refuse_done(self):
        for record in self:
            record.status = 'refuse'
            record.pm_accept = False
            record.dl_first_accept = False
            record.dl_second_accept = False
            record.hr_accept = False
            record.other_confirm = False
            record.acct_confirm = False
        template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        record.editable = False

    def PM_approud_done(self):
        for record in self:
            record.pm_accept = True
            record.status = 'dl2'
            template_id = self.env.ref("quitjob_manage.mail_template_pm_2_dl").id
            print(template_id)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)
            record.editable = False

    def PM_approud(self):
        form_view = self.env.ref('quitjob_manage.approved_note')
        return {
            'name': _('DL Note'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_model': 'employee.req',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def Hr_approved_done(self):
        for record in self:
            # if record.other_confirm == False and record.dl_second_accept:
            record.hr_accept = True
            record.dl_second_accept = True
            record.pm_accept = True
            if record.it_confirm and record.acct_confirm:
                record.status = 'done'
            template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
            print(template_id)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)

    def admin_approve(self):
        for r in self:
            r.pm_accept=True
            r.dl_second_accept=True
            r.hr_accept=True
            r.other_confirm=True
            r.acct_confirm=True
            r.status='done'

    def admin_refuse(self):
        for r in self:
            r.pm_accept=False
            r.dl_second_accept=False
            r.hr_accept=False
            r.other_confirm=False
            r.acct_confirm=False
            r.status='refuse'

    @api.model
    def create(self, vals):
        print('line 1')
        res_id = super(Employee_rq, self).create(vals)
        if res_id.create_uid.has_group('quitjob_manage.group_hr_user'):
            res_id.creator_role = 'hr'
            print('hr user')
            res_id.status = 'hr'
            res_id.pm_accept = True
            res_id.dl_first_accept = True
            res_id.dl_second_accept = True
            return res_id
        if res_id.create_uid.has_group('quitjob_manage.group_dl_user'):
            print('dl user')
            res_id.creator_role = 'dl2'
            res_id.status = 'dl2'
            res_id.pm_accept = True
            res_id.dl_first_accept = True
            return res_id
        if res_id.create_uid.has_group('quitjob_manage.group_pm_user'):
            res_id.creator_role = 'pm'
            print('pm user')
            res_id.status = 'pm'
            res_id.pm_accept = True
            return res_id
        if res_id.create_uid.has_group('quitjob_manage.group_admin_user'):
            res_id.creator_role = 'admin'
            return res_id

        res_id.creator_role = 'draft'
        print('emp user')
        print('line 2  ', res_id.create_uid)
        return res_id

    def unlink(self):
        print(self)
        for record in self:
            if record.editable == False and record.creator_role in ['admin'] == False:
                raise ValidationError(_("Ban kho the xoa ban ghi"))
            else:
                print('sdfdfadf')
        return super(Employee_rq, self).unlink()

    @api.depends('status', 'creator_role')
    def _check_edit_(self):
        print('go in')
        for r in self:
            print(r.status)
            print(r.creator_role)
            if r.status in [r.creator_role]:
                r.editable = True
            else:
                print('false --- ')
                r.editable = False

    def it_confirm(self):
        for r in self:
            r.other_confirm = True
            if r.hr_accept == True and r.acct_confirm == True:
                r.status = 'done'

    def acct_confirm_(self):
        for r in self:
            r.acct_confirm = True
            if r.hr_accept == True and r.other_confirm == True:
                r.status = 'done'

    def delete_rec(self):
        for record in self:
            if record.dl_second_accept == False:
                record.unlink()

    @api.constrains('req_date')
    def _check_est_date(self):
        for r in self:
            if r.req_date < r.create_date.date() or r.req_date == False:
                raise ValidationError("Invalid est_date")



    @api.depends('req_date')
    def _compute_est_date(self):
        for record in self:
            if record.req_date:
                record.est_date = record.req_date + datetime.timedelta(5)
            else:
                record.est_date = datetime.date.today()



    @api.depends('rela_user')
    def _get_position(self):
        for r in self:
            if r.rela_user.has_group('quitjob_manage.group_hr_user'):
                r.position = 'Hr User'
            if r.rela_user.has_group('quitjob_manage.group_dl_user'):
                r.position = 'DL User'
            if r.rela_user.has_group('quitjob_manage.group_pm_user'):
                r.position = 'PM User'
            if r.rela_user.has_group('quitjob_manage.group_emp_user'):
                r.position = 'EMP User'

    @api.onchange('employee_id')
    def rela_user_hr_employee(self):
        self.rela_user = self.employee_id.user_id


