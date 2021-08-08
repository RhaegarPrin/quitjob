from odoo import api, fields, models, _, tools
from odoo import fields, models
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _name="employee.company"

    full_name =fields.Char('Name',required=True)
    DOB = fields.Date(string="DOB", default=fields.Date.today())
    Addr = fields.Selection([
        ('esteros', 'Westeros'),
        ('essos', 'Esosss'),
        ('dune', 'Dune'),
        ('calanda', 'Calanda'),
    ])
    # req_ids = fields.One2many('employee.req','emp_id',string="List Req")


