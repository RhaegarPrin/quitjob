from odoo import fields,models


class hr_wizard(models.TransientModel):
    _name='hr_note_trans'
    employee_req_id = fields.Many2one('employee.req')
    temp_date= fields.Date(string="Ngày momg muốn")
    reason = fields.Text(string="Reason")

    def update_req_date(self):
        print('call func')
        self.employee_req_id.req_date = self.temp_date