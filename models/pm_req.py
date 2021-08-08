from odoo import fields, models

class pm_req(models.Model):
    _name = "pm.req"

    dl_reqs = fields.One2many('dl.req','pm_id',string="List_req", domain=[('valid_reqs', '=', True)])
    rela_user = fields.Many2one('res.users' ,string='USER Related')