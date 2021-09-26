from odoo import fields, models


class reson_quit(models.Model):
    _name = 'quit.reason'

    name = fields.Char(string='Name')
    status = fields.Selection([
        ('not', 'NOT'),
        ('submit', 'Submited')], default='not')

    def submit(self):
        for r in self:
            print(r.name)
            print('before change : ', r.status)
            r.status='submit'
            print('before : ', r.status)
        # print(self.name)
        # print('before change : ', self.status)
        # self.status = 'submit'
        # print('before : ',self.status)

    def check_submit(self):
        for record in self :
            print(record.status)
