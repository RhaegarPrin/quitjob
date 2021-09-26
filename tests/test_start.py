import names
import datetime
from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged


class TestReason(TransactionCase):

    # def setUpClass(cls):
    #     super(TestReason, cls).setUpClass()

    def test_start(self):
        print('testing')
        for i in range(0, 10):
            record = self.env['quit.reason'].create({'name': names.get_full_name()})

        data = self.env['quit.reason'].sudo().search([], order="id desc", limit=100)
        data.submit()
        print(len(data))
        print('test done')

    def test_submit(self):
        print('testing submit')
        for i in range(0, 100):
            dl = self.env['hr.employee'].create({'name': names.get_full_name()})
            employee = self.env['hr.employee'].create({'name': names.get_full_name(),
                                                       'parent_id':dl.id})

            record = self.env['employee.req'].create({'employee_id': employee.id,
                                                      'req_date':datetime.date.today()})
        data = self.env['employee.req'].sudo().search([], order="id desc", limit=100)
        data.send_req_done()
        print('test submit done')