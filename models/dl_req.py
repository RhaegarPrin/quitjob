from odoo import fields, models, api


class dl_req(models.Model):
    _name = "dl.req"

    emp_reqs = fields.One2many('employee.req', 'dl_id', string="List_req", domain=[('status', '=', 'send')])
    valid_reqs = fields.Boolean(compute="_compute_valid_req", store=True, default=False)
    pm_id = fields.Many2one('pm.req', string='PM')
    rela_user = fields.Many2one('res.users', string='USER Related',default=lambda self: self.env.user)

    # @api.depends("emp_reqs")
    # def _empty_or_not(self):
    #     for record in self:
    #         if len(record.emp_reqs) == 0:
    #             record.pm_id = None
    @api.depends("emp_reqs")
    def _compute_valid_req(self):
        for record in self:
            if len(record.emp_reqs) == 0:
                self.valid_reqs = False
            else:
                self.valid_reqs = True
