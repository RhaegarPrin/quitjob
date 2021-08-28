from odoo import api, fields, models, _, tools
from odoo import fields, models
from odoo.exceptions import ValidationError
import datetime


class Employee_rq(models.Model):
    _name = "employee.req"
    reasons = fields.Many2many('quit.reason', string='Reasons')
    notes = fields.Many2one('quit.note', string='DL Coms')
    position = fields.Char(compute="_get_position", string='Position')
    job_title = fields.Char(related='employee_id.job_title')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    parent_department_id = fields.Many2one('hr.department', related='department_id.parent_id')
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  default=lambda self: self.env.user.employee_id)
    rela_user = fields.Many2one('res.users', string='USER Related', related='employee_id.user_id',
                                required=True)
    contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id', groups="base.group_user")
    pm_id = fields.Many2one('hr.employee', string='pm')
    # domain=lambda self :[('department_id', '=', self.env.user.employee_id.department_id)])
    dl_id = fields.Many2one('hr.employee', string='dl')
    hr_id = fields.Many2one('hr.employee', string='hr')
    rela_user_email = fields.Char(related="rela_user.email")
    parent_id = fields.Many2one('hr.employee', related='department_id.manager_id')
    it_id = fields.Many2one('it.req')

    dl_first_accept = fields.Boolean(default=False, string="DL 1st accepted")
    dl_second_accept = fields.Boolean(default=False, string="DL 2nd accepted")
    pm_accept = fields.Boolean(default=False, string="PM accepted")
    hr_accept = fields.Boolean(default=False, string="hr accepted")
    other_confirm = fields.Boolean(default=False, string="IT confirm")
    acct_confirm = fields.Boolean(default=False, string="Ke toan confirm")
    result = fields.Boolean(compute="_compute_status")
    req_date = fields.Date(string="Request Date")
    est_date = fields.Date(string="Request Date", compute="_compute_est_date")
    reason = fields.Selection([
        ('luong thap', 'Luong Thap'),
        ('Met ', 'Met'),
        ('Chuyen Cty', 'Chuyen Cty'),
        ('khac', 'Khac'),
    ])
    specific_reason = fields.Char(string="Lý do cụ thể")

    status = fields.Selection([
        ('refuse', 'Refuse'),
        ('draft', 'Draft'),
        ('pm', 'PM Assessing'),
        ('dl2', 'Dl Assessing'),
        ('hr', 'Hr Assessing'),
        ('done', 'Approved')], default='draft')
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
            record.editable = False

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
        if res_id.create_uid.has_group('quitjob_manage.group_dl_user'):
            print('dl user')
            res_id.creator_role = 'dl2'
            res_id.status = 'dl2'
            res_id.pm_accept = True
            res_id.dl_first_accept = True
        if res_id.create_uid.has_group('quitjob_manage.group_pm_user'):
            res_id.creator_role = 'pm'
            print('pm user')
            res_id.status = 'pm'
            res_id.pm_accept = True
        if res_id.create_uid.has_group('quitjob_manage.group_emp_user'):
            res_id.creator_role = 'draft'
            print('emp user')
        print('line 2  ', res_id.create_uid)
        return res_id

    def unlink(self):
        print(self)
        for record in self:
            if record.editable == False:
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
            if r.hr_accept and r.acct_confirm:
                r.status = 'done'

    def acct_confirm_(self):
        for r in self:
            r.acct_confirm = True
            if r.hr_accept and r.it_confirm:
                r.status = 'done'

    def delete_rec(self):
        for record in self:
            if record.dl_second_accept == False:
                record.unlink()

    @api.constrains('req_date')
    def _check_est_date(self):
        for r in self:
            if r.req_date < r.create_date.date() :
                raise ValidationError("Invalid est_date")

    @api.depends('req_date')
    def _compute_est_date(self):
        for record in self:
            if record.req_date:
                record.est_date = record.req_date + datetime.timedelta(5)
            else:
                record.est_date = datetime.date.today()

    def group_score(self, group_name):
        if group_name == 'Hr User':
            return 3
        if group_name == 'DL User':
            return 2
        if group_name == 'PM User':
            return 1
        if group_name == 'EMP User':
            return 0
        return -10

    def get_group_name(self):
        user = self.env['res.users'].browse(self.env.uid)
        if user.has_group('quitjob_manage.group_hr_user'):
            return 'Hr User'
        if user.has_group('quitjob_manage.group_dl_user'):
            return 'DL User'
        if user.has_group('quitjob_manage.group_pm_user'):
            return 'PM User'
        if user.has_group('quitjob_manage.group_emp_user'):
            return 'EMP User'
        return 'base.group_user'

    @api.constrains('rela_user')
    def _check_rela_user(self):
        try:
            print('go in rela')
            user_gr = self.get_group_name()
            print('user group : ', user_gr)
            for record in self:
                gr_ids = record.rela_user.reqs[0].rela_user.groups_id
                print(gr_ids)
                count = len(gr_ids)
                print(count)
                if record.rela_user == self.env.user:
                    print('env user')
                    pass
                else:
                    name = None
                    print('other user')
                    if record.rela_user.has_group('quitjob_manage.group_hr_user'):
                        name = 'Hr User'
                    if record.rela_user.has_group('quitjob_manage.group_dl_user'):
                        name = 'DL User'
                    if record.rela_user.has_group('quitjob_manage.group_pm_user'):
                        name = 'PM User'
                    if record.rela_user.has_group('quitjob_manage.group_emp_user'):
                        name = 'EMP User'
                    if record.group_score(name) >= record.group_score(user_gr):
                        raise ValidationError("Invalid user")
        except:
            pass

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

    #
    # def hr_note_inverse(self):
    #     if len(self.hr_notes) > 0:
    #         hr_note = self.env['hr_note_test'].browse(self.hr_notes[0].id)
    #         hr_note.employee_req_id = False
    #     self.hr_note.employee_req_id=self

    def test_open_edit(self):
        return {

            'type': 'ir.actions.act_window',

            'view_type': 'form',

            'view_mode': 'form',

            'res_model': 'employee.req',  # name of respective model,
            'target': 'new',
            'context': {'force_detailed_view': 'true',
                        'form_view_initial_mode': 'edit'},
        }
