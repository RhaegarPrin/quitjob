from odoo import api, fields, models, _, tools
from odoo import fields, models
from odoo.exceptions import ValidationError
import datetime


class Employee_rq(models.Model):
    _name = "employee.req"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reasons = fields.Many2many('quit.reason', relation='emp_reason', string='Reasons')
    pm_reason = fields.Many2many('quit.reason', relation='pm_reason', string='Pm reason')
    dl_reason = fields.Many2many('quit.reason', relation='dl_reason', string='Dl reason')
    hr_reason = fields.Many2many('quit.reason', relation='hr_reason', string='Hr reason')
    name = fields.Char(related='employee_id.name')
    position = fields.Char(compute="_get_position", string='Position')
    job_title = fields.Char(related='employee_id.job_id.name')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    parent_department_id = fields.Many2one('hr.department', related='department_id.parent_id')
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True,
                                  default=lambda self: self.env.user.employee_id)
    own_rec = fields.Boolean(compute='get_current_uid')

    rela_user = fields.Many2one('res.users', string='USER Related', related='employee_id.user_id',
                                required=True)
    contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id', groups="base.group_user")
    pm_id = fields.Many2one('hr.employee', string='pm')
    dl_id = fields.Many2one('hr.employee', string='dl', related='employee_id.parent_id')
    hr_id = fields.Many2one('hr.employee', string='hr', related='contract_id.hr_responsible_id.employee_id')

    parent_id = fields.Many2one('hr.employee', related='department_id.manager_id')
    it_id = fields.Many2one('it.req')

    dl_first_accept = fields.Boolean(default=False, string="DL 1st accepted")
    dl_second_accept = fields.Boolean(default=False, string="DL 2nd accepted")
    pm_accept = fields.Boolean(default=False, string="PM accepted")
    hr_accept = fields.Boolean(default=False, string="hr accepted")
    other_confirm = fields.Boolean(default=False, string="IT confirm")
    acct_confirm = fields.Boolean(default=False, string="Ke toan confirm")
    result = fields.Boolean(compute="_compute_status")
    req_date = fields.Date(string="Request Date", required=True, tracking=True)
    est_date = fields.Date(string="Est Date", compute="_compute_est_date")
    dl_pick_date = fields.Date(string="DL PICK DATE", default=datetime.date.today())
    dl_acc = fields.Selection([('yes', 'Đồng ý cho nghỉ'), ('no', 'Không đồng ý cho nghỉ')], default='no')
    reason = fields.Selection([
        ('luong thap', 'Luong Thap'),
        ('Met ', 'Met'),
        ('Chuyen Cty', 'Chuyen Cty'),
        ('khac', 'Khac'),
    ], tracking=True)
    specific_reason = fields.Text(string="Lý do cụ thể", tracking=True)

    status = fields.Selection([
        ('refuse', 'Refuse'),
        ('draft', 'Draft'),
        ('pm', 'PM Assessing'),
        ('dl2', 'Dl Assessing'),
        ('hr', 'Hr Assessing'),
        ('done', 'Approved')], default='draft', tracking=True)
    creator_role = fields.Char()
    editable = fields.Boolean(default=True, compute='_check_edit_')

    pm_interview = fields.Text(string='PM Note',
                               groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    dl_interview = fields.Text(string='DL Note',
                               groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    dl_msg_pm = fields.Text(string='DL MSG for PM',
                            groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    hr_interview = fields.Text(string='HR Note',
                               groups="quitjob_manage.group_dl_user,quitjob_manage.group_pm_user,quitjob_manage.group_hr_user")
    profile = fields.Boolean(string='Hồ sơ')
    notes = fields.Char()
    refuse_notes = fields.Char()
    pos_ass = fields.Char(default='draft')
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

    def send_req_done(self):
        check = self.env['employee.req'].sudo().search(
            [('employee_id', '=', self.employee_id.id), ('status', 'not in', ['refuse', 'draft', 'done'])])
        for d in check:
            print(d.status)
        if len(check) > 0:
            raise ValidationError('Nhân viên này đang trong quá trình ngỉ việc không thể nộp đơn mới')
        for record in self:
            if record.status == 'draft' and record.creator_role == 'draft':
                record.status = 'dl2'
                record.pos_ass = 'dl2'
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_dl").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)
                record.editable = False
                record.notes = self.env.user.employee_id.name + 'assigned DL to do resignation request '
            else:
                raise ValidationError('Bạn không có quyền thay đổi')

    def send_req(self):
        form_view = self.env.ref('quitjob_manage.approved_note')
        return {
            'name': _('Note'),
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
            if record.dl_pick_date < (datetime.date.today() - datetime.timedelta(5)):
                raise ValidationError("Invalid est_date")
            if type(record.dl_interview) != bool and len(record.dl_interview) < 10:
                raise ValidationError('Ghi chú phải hơn 10 ký tự')
            record.dl_second_accept = True
            record.dl_first_accept = True
            record.pm_accept = True
            record.status = 'hr'
            record.pos_ass = 'hr'
            record.notes = self.env.user.employee_id.name + 'assigned Hr manager to do resignation request ' + record.employee_id.name
            template_id = self.env.ref("quitjob_manage.mail_template_hr").id
            print(template_id)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)
            record.editable = False

    def Dl_approud_1(self):
        check = self.env['employee.req'].sudo().search(
            [('employee_id', '=', self.employee_id.id), ('status', 'not in', ['refuse', 'draft', 'done'])])
        for d in check:
            print(d.status)
        if len(check) > 0 and self.status == 'draft':
            raise ValidationError('Nhân viên này đang trong quá trình ngỉ việc không thể nộp đơn mới')
        for record in self:
            if record.rela_user == self.env.user and record.create_uid != self.env.user:
                raise ValidationError("Bạn không có quyền thay đổi bản ghi")
        form_view = self.env.ref('quitjob_manage.approved_note')
        return {
            'name': _('Note'),
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
                record.pos_ass = 'pm'
                record.dl_first_accept = True
                record.dl_second_accept = False
                record.pm_accept = False
                record.notes = self.env.user.employee_id.name + 'assigned to PM to do resignation request' + record.employee_id.name
                template_id = self.env.ref("quitjob_manage.mail_template_emp_2_pm").id
                print(template_id)
                template = self.env['mail.template'].browse(template_id)
                template.send_mail(self.id, force_send=True)

    def Dl_2_PM(self):
        for record in self:
            if type(record.dl_msg_pm) != bool and len(record.dl_msg_pm) < 10:
                raise ValidationError('Ghi chú phải hơn 10 ký tự')
        form_view = self.env.ref('quitjob_manage.dl_2_pm')
        return {
            'name': _('Note'),
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
            'name': _('Refuse form'),
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
            if type(record.pm_interview) != bool and len(record.pm_interview) < 10:
                raise ValidationError('Ghi chú phải hơn 10 ký tự')
            record.status = 'refuse'
        template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        record.editable = False
        record.refuse_notes = 'PM ' + self.env.user.employee_id.name + 'refuse ' + record.employee_id.name + ' request'

    def dl_refuse_done(self):
        for record in self:
            if type(record.dl_interview) != bool and len(record.dl_interview) < 10:
                raise ValidationError('Ghi chú phải hơn 10 ký tự')
            record.status = 'refuse'
            record.refuse_notes = 'DL ' + self.env.user.employee_id.name + 'refuse ' + record.employee_id.name + ' request'
        template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        record.editable = False

    def hr_refuse_done(self):
        for record in self:
            if type(record.hr_interview) != bool and len(record.hr_interview) < 10:
                raise ValidationError('Ghi chú phải hơn 10 ký tự')
            record.status = 'refuse'
            record.refuse_notes = 'HR ' + self.env.user.employee_id.name + 'refuse ' + record.employee_id.name + ' request'
        template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        record.editable = False

    def it_refuse_done(self):
        for record in self:
            record.status = 'refuse'
            record.other_confirm = False
        template_id = self.env.ref("quitjob_manage.mail_template_IT_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    def accountant_refuse_done(self):
        for record in self:
            record.status = 'refuse'
            record.acct_confirm = False
        template_id = self.env.ref("quitjob_manage.mail_template_Accountant_2_emp").id
        print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    def PM_approud_done(self):
        for record in self:
            if type(record.pm_interview) != bool and len(record.pm_interview) < 10:
                raise ValidationError('Ghi chú phải hơn 10 ký tự')
            record.pm_accept = True
            record.status = 'dl2'
            record.pos_ass = 'dl2'
            template_id = self.env.ref("quitjob_manage.mail_template_pm_2_dl").id
            print(template_id)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)
            record.editable = False
            record.notes = self.env.user.employee_id.name + 'assigned DL to do resignation request ' + record.employee_id.name

    def PM_approud(self):
        check = self.env['employee.req'].sudo().search(
            [('employee_id', '=', self.employee_id.id), ('status', 'not in', ['refuse', 'draft', 'done'])])
        for d in check:
            print(d.status)
        if len(check) > 0 and self.status == 'draft':
            raise ValidationError('Nhân viên này đang chờ xử lý')
        form_view = self.env.ref('quitjob_manage.approved_note')
        return {
            'name': _('Note'),
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
            if type(record.hr_interview) != bool and len(record.hr_interview) < 10:
                raise ValidationError('Ghi chú phải hơn 10 ký tự')
            # if record.other_confirm == False and record.dl_second_accept:
            record.hr_accept = True
            record.dl_second_accept = True
            record.pm_accept = True
            record.status = 'done'
            record.notes = self.env.user.employee_id.name + 'Approved resignation request ' + record.employee_id.name
            template_id = self.env.ref("quitjob_manage.mail_template_hr_2_emp").id
            print(template_id)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)

    def admin_approve(self):
        for r in self:
            r.status = 'done'

    def admin_refuse(self):
        for r in self:
            r.status = 'refuse'

    @api.model
    def create(self, vals):
        res_id = super(Employee_rq, self).create(vals)
        if res_id.create_uid.has_group('quitjob_manage.group_hr_user'):
            res_id.creator_role = 'hr'
            print('hr user')
            res_id.status = 'done'
            res_id.hr_accept = True
            return res_id
        if res_id.create_uid.has_group('quitjob_manage.group_dl_user'):
            print('dl user')
            res_id.creator_role = 'dl2'
            # res_id.status = 'dl2'
            res_id.pos_ass = 'dl2'
            res_id.pm_accept = True
            res_id.dl_first_accept = True
            return res_id
        if res_id.create_uid.has_group('quitjob_manage.group_pm_user'):
            res_id.creator_role = 'pm'
            print('pm user')
            # res_id.status = 'pm'
            res_id.pos_ass = 'pm'
            res_id.pm_accept = True
            return res_id
        if res_id.create_uid.has_group('quitjob_manage.group_admin_user'):
            res_id.creator_role = 'admin'
            print('admin')
            return res_id

        res_id.creator_role = 'draft'
        print('emp user')
        print('line 2  ', res_id.create_uid)
        return res_id

    def unlink(self):
        print(self)
        for record in self:
            if record.editable == False and self.env.user.has_group('quitjob_manage.group_admin_user') == False:
                print(self.env.user.name)
                for i in self.env.user.groups_id:
                    print(i.name)
                raise ValidationError(_("Ban kho the xoa ban ghi"))
            else:
                if record.creator_role == 'hr' and record.hr_accept == True:
                    raise ValidationError(_("Ban kho the xoa ban ghi"))
                print('sdfdfadf')
        return super(Employee_rq, self).unlink()

    @api.depends('status', 'creator_role')
    def _check_edit_(self):
        print('go in')
        for r in self:
            print(r.status)
            print(r.creator_role)
            if r.status == 'draft' and r.create_uid == self.env.user:
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

    @api.onchange('dl_interview')
    def onchange_dl_interview(self):
        for r in self:
            if r.pm_interview != False:
                if len(r.dl_interview) < 10:
                    raise ValidationError('Ghi chú phải hơn 10 ký tự')

    @api.depends()
    def get_current_uid(self):
        for r in self:
            if r.rela_user == self.env.user or r.create_uid == self.env.user:
                r.own_rec = True
            else:
                r.own_rec = False


    def hr_update_date(self):
        print('hr in')
        form_view = self.env.ref('quitjob_manage.hr_note_trans_form')
        return {
            'name': _('Note'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view.id,
            'res_model': 'hr_note_trans',
            'type': 'ir.actions.act_window',
            'context': {'default_employee_req_id': self.id},
            'target': 'new',
        }
