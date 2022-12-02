from odoo.tests import TransactionCase, tagged

from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


@tagged('myodoo')
class TestSaleOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Set up data for all tests in this test class."""
        super(TestSaleOrder, cls).setUpClass()
        _logger.info(f'BEGINNING OF "sale_order" MODULE UNIT TESTS!')


        # Account.
        user_type_payable = cls.env.ref('account.data_account_type_payable')
        cls.account_payable = cls.env['account.account'].create({
            'code': 'NC1110',
            'name': 'Test Payable Account',
            'user_type_id': user_type_payable.id,
            'reconcile': True
        })
        user_type_receivable = cls.env.ref('account.data_account_type_receivable')
        cls.account_receivable = cls.env['account.account'].create({
            'code': 'NC1111',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True
        })

        # Create test partners.
        cls.company_partner_checked = cls.env['res.partner'].create({
            'name': 'Checked Partner Company',
            'type': 'contact',
            'vat': 'PL1234567891',
            'company_type': 'company',
            'property_account_payable_id': cls.account_payable.id,
            'property_account_receivable_id': cls.account_receivable.id,
        })

        # Create test products.
        cls.test_product_1 = cls.env['product.product'].create({
            'name': 'Test Product 1',
            'sale_ok': True
        })
        cls.test_product_2 = cls.env['product.product'].create({
            'name': 'Test Product 2',
            'sale_ok': True
        })

        # Create sale orders
        cls.test_sale_order = cls.env['sale_order'].create({
            'partner_id': cls.company_partner_checked.id,
            'x_is_poland': False
        })

        cls.test_sale_order_line = cls.env['sale_order_line'].create({
            'order_id': cls.test_sale_order.id,
            'product_id': cls.test_product_1.id
        })


    # def setUp(self):
    #     """Set up data before each test method."""
    #     super(TestSaleOrder, self).setUp()
    #     self.periodic_report_1 = self.env['sale_order'].create({

    # def tearDown(self):
    #     """Tear down data after each test method."""
    #     super(TestSaleOrder, self).tearDown()
    #     self.periodic_report_1.unlink()


    def test_x_compute_is_poland(self):
        _logger.info(f'RUNNING "test_x_compute_is_poland" TEST!')
        if cls.env.user.company_id.country_id.id == self.env.ref('base.pl').id:
            cls.x_is_poland = True

        self.assertTrue(
            cls.x_is_poland,
            'Successfully running _x_compute_is_poland test.'
        )

        _logger.info(f'TEST COMPLETE!')